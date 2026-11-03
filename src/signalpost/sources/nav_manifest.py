"""NAV Index Manifest, Coverage Certification, and Transactional Checkpointing (F05 & F06).

Certified States:
- COMPLETE_FOR_DECLARED_WINDOW: Complete forward feed coverage within the declared lookback window.
- PARTIAL: Incomplete feed run or detail cap reached before exhausting candidates.
- STALE: Index age exceeds maximum allowed age (e.g. >21 days without historical snapshot permission).
- AUTH_BLOCKED: Source access refused (401/403/token unavailable).
- SOURCE_UNAVAILABLE: Feed endpoint down, network unreachable, or 5xx outage.
- INTEGRITY_FAILED: Corrupted gzip, missing mandatory schema keys, or broken JSON.
- COVERAGE_UNKNOWN: Feed status unknown or unverified.
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID

from ..budget import SourceFailure
from ..identity.orgnr import valid
from .nav import timestamp

CERT_COMPLETE = "COMPLETE_FOR_DECLARED_WINDOW"
CERT_PARTIAL = "PARTIAL"
CERT_STALE = "STALE"
CERT_AUTH_BLOCKED = "AUTH_BLOCKED"
CERT_SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
CERT_INTEGRITY_FAILED = "INTEGRITY_FAILED"
CERT_COVERAGE_UNKNOWN = "COVERAGE_UNKNOWN"


@dataclass
class IndexManifest:
    schema_version: int
    index_version: str
    built_at: str
    cursor: str
    source_api: str
    certification_status: str
    sha256_checksum: str
    compressed_bytes: int
    total_ads_count: int
    active_unexpired_count: int
    expired_count: int
    inactive_withdrawn_count: int
    distinct_employer_orgnrs: int
    earliest_ad_published: str | None
    latest_ad_published: str | None
    failed_details_count: int
    seeded_from_disk_count: int
    fresh_fetched_ads_count: int
    certified_at: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_usable_for_publication(self) -> bool:
        if self.certification_status not in {CERT_COMPLETE, "HISTORICAL_SNAPSHOT"}:
            return False
        if self.active_unexpired_count <= 0:
            return False
        if self.failed_details_count > 0:
            return False
        if any("invalid" in r or "unsupported" in r or "corrupt" in r for r in self.reasons):
            return False
        return True


def certify_index_data(
    data: dict[str, Any],
    file_bytes: bytes | None = None,
    now: datetime | None = None,
    max_age_days: float = 21.0,
    allow_historical_snapshot: bool = False
) -> IndexManifest:
    """
    Forensically certify an existing or newly built NAV index.
    Checks date boundaries, status distributions, employer orgnr validity, and checksums.
    """
    now_dt = now or datetime.now(timezone.utc)
    certified_at = now_dt.isoformat().replace("+00:00", "Z")

    reasons = []
    # 1. Structural schema checks
    if not isinstance(data, dict):
        raise SourceFailure("index_invalid")

    schema_version = data.get("schema_version", 0)
    index_version = str(data.get("index_version", ""))
    built_at_str = str(data.get("built_at", ""))
    cursor_str = str(data.get("cursor", ""))
    ads = data.get("ads", [])

    if not index_version or not built_at_str:
        return IndexManifest(
            schema_version=schema_version,
            index_version=index_version,
            built_at=built_at_str,
            cursor=cursor_str,
            source_api="https://pam-stilling-feed.nav.no",
            certification_status=CERT_INTEGRITY_FAILED,
            sha256_checksum="",
            compressed_bytes=len(file_bytes) if file_bytes else 0,
            total_ads_count=0,
            active_unexpired_count=0,
            expired_count=0,
            inactive_withdrawn_count=0,
            distinct_employer_orgnrs=0,
            earliest_ad_published=None,
            latest_ad_published=None,
            failed_details_count=0,
            seeded_from_disk_count=0,
            fresh_fetched_ads_count=0,
            certified_at=certified_at,
            reasons=["missing_index_metadata"]
        )

    status = CERT_COMPLETE
    if schema_version != 1:
        reasons.append(f"unsupported_schema_version_{schema_version}")
        status = CERT_INTEGRITY_FAILED

    if cursor_str.startswith("http://") or cursor_str.startswith("https://"):
        if not cursor_str.startswith("https://pam-stilling-feed.nav.no/"):
            reasons.append("invalid_cursor_external_url")
            status = CERT_INTEGRITY_FAILED

    # 2. Check age
    built_at_dt = timestamp(built_at_str)
    if built_at_dt is None:
        reasons.append("invalid_built_at_timestamp")
        status = CERT_INTEGRITY_FAILED
    else:
        age_days = (now_dt - built_at_dt).total_seconds() / 86400.0
        if age_days < -0.01:
            reasons.append("index_built_in_future")
            status = CERT_INTEGRITY_FAILED
        elif age_days > max_age_days:
            if allow_historical_snapshot:
                if status == CERT_COMPLETE:
                    status = "HISTORICAL_SNAPSHOT"
                reasons.append(f"historical_snapshot_age_{age_days:.1f}_days")
            else:
                reasons.append(f"index_stale_age_{age_days:.1f}_days")
                if status == CERT_COMPLETE:
                    status = CERT_STALE

    # 3. Ad-level audit
    active_unexpired = 0
    expired = 0
    inactive = 0
    valid_orgs = set()
    earliest_pub = None
    latest_pub = None

    for ad in ads:
        if not isinstance(ad, dict):
            reasons.append("corrupt_ad_entry")
            status = CERT_INTEGRITY_FAILED
            continue

        emp_org = ad.get("employer_orgnr", "")
        if valid(emp_org):
            valid_orgs.add(emp_org)
        else:
            reasons.append(f"invalid_employer_orgnr_{emp_org}")
            status = CERT_INTEGRITY_FAILED

        ad_uuid = ad.get("uuid", "")
        try:
            UUID(str(ad_uuid))
        except (ValueError, AttributeError):
            reasons.append(f"invalid_uuid_{ad_uuid}")
            status = CERT_INTEGRITY_FAILED

        ad_status = ad.get("status", "UNKNOWN")
        exp_dt = timestamp(ad.get("expires"))
        pub_dt = timestamp(ad.get("published"))

        if pub_dt:
            pub_iso = pub_dt.isoformat()
            if earliest_pub is None or pub_iso < earliest_pub:
                earliest_pub = pub_iso
            if latest_pub is None or pub_iso > latest_pub:
                latest_pub = pub_iso

        if ad_status != "ACTIVE":
            inactive += 1
        elif exp_dt is not None and exp_dt <= now_dt:
            expired += 1
        else:
            active_unexpired += 1

    # Check failed details
    failed_details = int(data.get("failed_details", 0))
    if failed_details > 0 and status == CERT_COMPLETE:
        status = CERT_PARTIAL
        reasons.append(f"{failed_details}_failed_details")

    # 4. Checksum calculation
    if file_bytes:
        checksum = hashlib.sha256(file_bytes).hexdigest()
        comp_len = len(file_bytes)
    else:
        raw_repr = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        checksum = hashlib.sha256(raw_repr).hexdigest()
        comp_len = len(raw_repr)

    return IndexManifest(
        schema_version=schema_version,
        index_version=index_version,
        built_at=built_at_str,
        cursor=cursor_str,
        source_api="https://pam-stilling-feed.nav.no",
        certification_status=status,
        sha256_checksum=checksum,
        compressed_bytes=comp_len,
        total_ads_count=len(ads),
        active_unexpired_count=active_unexpired,
        expired_count=expired,
        inactive_withdrawn_count=inactive,
        distinct_employer_orgnrs=len(valid_orgs),
        earliest_ad_published=earliest_pub,
        latest_ad_published=latest_pub,
        failed_details_count=failed_details,
        seeded_from_disk_count=int(data.get("seeded_from_disk", 0)),
        fresh_fetched_ads_count=int(data.get("fresh_fetched_ads", 0)),
        certified_at=certified_at,
        reasons=sorted(list(set(reasons)))
    )


class NavCheckpointManager:
    """
    Durable transactional checkpointing for NAV feed ingestion (F06).
    Enforces atomic write via temporary file replacement and durable state replay.
    """

    def __init__(self, checkpoint_path: Path):
        self.path = checkpoint_path

    def load_checkpoint(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict) or "cursor" not in data or "updated_at" not in data:
                return None
            return data
        except Exception:
            return None

    def save_checkpoint(self, cursor: str, pages_processed: int, items_processed: int, extra: dict | None = None) -> bool:
        """Atomic write using temporary file to prevent corruption on crash."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload = {
            "cursor": cursor,
            "pages_processed": pages_processed,
            "items_processed": items_processed,
            "updated_at": now_str,
            "extra": extra or {}
        }
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        tmp_path = self.path.with_suffix(self.path.suffix + f".tmp.{os.getpid()}")
        try:
            tmp_path.write_bytes(body)
            tmp_path.replace(self.path)
            return True
        except Exception:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            return False
