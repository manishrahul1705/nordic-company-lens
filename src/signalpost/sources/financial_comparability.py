"""
Feature F03: Comparable Financial-Period Gate.

Deterministic comparability predicate and typed reason codes for multi-period
accounting data. Prevents misleading trend/growth synthesis across differing
currencies, accounting scopes, truncated fiscal years, restatements or entity shifts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class FinancialObservation:
    organisation_number: str
    fiscal_year: str
    period_start: str
    period_end: str
    currency: str | None = None
    unit: str | None = None
    account_type: str | None = "SELSKAP"
    metrics: dict[str, float | int | None] = field(default_factory=dict)
    journalnr: str | None = None


@dataclass
class ComparabilityResult:
    comparable: bool
    reason_codes: list[str]
    explanation: str
    nominal_change: float | int | None = None
    growth_rate: float | None = None
    period_1: dict[str, Any] | None = None
    period_2: dict[str, Any] | None = None
    metric: str | None = None


class ComparablePeriodGate:
    """
    Evaluates whether two financial periods from Regnskapsregisteret can be
    defensibly compared to compute growth, CAGR, or multi-year trends.
    """

    MIN_ANNUAL_DAYS = 350
    MAX_ANNUAL_DAYS = 375
    MAX_ALLOWED_GAP_DAYS = 35

    def compare(
        self,
        current: FinancialObservation,
        prior: FinancialObservation,
        metric: str | None = None
    ) -> ComparabilityResult:
        reasons: list[str] = []

        # 1. Legal Entity check
        if str(current.organisation_number or "").strip() != str(prior.organisation_number or "").strip():
            reasons.append("differing_legal_entity")

        # 2. Accounting Scope check (SELSKAP vs KONSERN)
        curr_scope = str(current.account_type or "").upper()
        prior_scope = str(prior.account_type or "").upper()
        if curr_scope != prior_scope or curr_scope not in {"SELSKAP"}:
            reasons.append("differing_accounting_scope")

        # 3. Currency check (silent currency conversion strictly disallowed)
        curr_curr = str(current.currency or "").upper()
        prior_curr = str(prior.currency or "").upper()
        if curr_curr != prior_curr or not curr_curr:
            reasons.append("currency_mismatch")

        # 3b. Unit check (unit scale mismatch strictly disallowed)
        curr_unit = str(current.unit or "").upper()
        prior_unit = str(prior.unit or "").upper()
        if curr_unit != prior_unit or not curr_unit:
            reasons.append("unit_mismatch")

        # 4. Period Boundaries and Length check
        d_curr_start = self._parse_date(current.period_start)
        d_curr_end = self._parse_date(current.period_end)
        d_prior_start = self._parse_date(prior.period_start)
        d_prior_end = self._parse_date(prior.period_end)

        if not all([d_curr_start, d_curr_end, d_prior_start, d_prior_end]):
            reasons.append("missing_period_dates")
        else:
            # Ensure chronologically ordered (current must be later than prior)
            if d_curr_end < d_prior_end:
                d_curr_start, d_prior_start = d_prior_start, d_curr_start
                d_curr_end, d_prior_end = d_prior_end, d_curr_end

            len_curr = (d_curr_end - d_curr_start).days + 1
            len_prior = (d_prior_end - d_prior_start).days + 1

            if d_curr_start == d_prior_start and d_curr_end == d_prior_end:
                reasons.append("identical_periods")
            else:
                if (len_curr < self.MIN_ANNUAL_DAYS or len_curr > self.MAX_ANNUAL_DAYS or
                        len_prior < self.MIN_ANNUAL_DAYS or len_prior > self.MAX_ANNUAL_DAYS):
                    reasons.append("non_standard_period_length")

                # Check for temporal gap between prior end and current start
                gap = (d_curr_start - d_prior_end).days
                if gap > self.MAX_ALLOWED_GAP_DAYS:
                    reasons.append("period_gap")
                elif gap <= 0 and d_curr_start < d_prior_end:
                    reasons.append("overlapping_periods")

        # Base comparability decision
        is_comparable = (len(reasons) == 0)
        
        nominal: float | int | None = None
        growth: float | None = None

        if metric:
            v_curr = current.metrics.get(metric)
            v_prior = prior.metrics.get(metric)
            if v_curr is not None and v_prior is not None and is_comparable:
                nominal = v_curr - v_prior
                if v_prior <= 0:
                    reasons.append("non_positive_prior_base")
                    growth = None
                else:
                    growth = (v_curr - v_prior) / v_prior

        explanation = self._format_explanation(is_comparable, reasons, current, prior, metric)

        return ComparabilityResult(
            comparable=is_comparable,
            reason_codes=sorted(list(set(reasons))),
            explanation=explanation,
            nominal_change=nominal,
            growth_rate=growth,
            period_1={"fiscal_year": current.fiscal_year, "start": current.period_start, "end": current.period_end},
            period_2={"fiscal_year": prior.fiscal_year, "start": prior.period_start, "end": prior.period_end},
            metric=metric
        )

    def _parse_date(self, val: Any) -> date | None:
        if not val:
            return None
        try:
            return date.fromisoformat(str(val)[:10])
        except (ValueError, TypeError):
            return None

    def _format_explanation(
        self,
        comparable: bool,
        reasons: list[str],
        curr: FinancialObservation,
        prior: FinancialObservation,
        metric: str | None
    ) -> str:
        if comparable and not reasons:
            return (
                f"Fiscal years {curr.fiscal_year} and {prior.fiscal_year} are comparable: "
                f"matching legal entity ({curr.organisation_number}), scope ({curr.account_type}), "
                f"currency ({curr.currency}), and standard annual boundaries."
            )
        if "non_positive_prior_base" in reasons and comparable:
            return (
                f"Fiscal years {curr.fiscal_year} and {prior.fiscal_year} are period-comparable, "
                f"but prior base {metric} is non-positive ({prior.metrics.get(metric)}); percentage growth withheld."
            )
        readable_reasons = ", ".join(reasons)
        return (
            f"Fiscal years {curr.fiscal_year} and {prior.fiscal_year} are not directly comparable: "
            f"[{readable_reasons}]. Raw values preserved; growth synthesis gated."
        )


def compare_periods(claim1: Any, claim2: Any, org: str | None = None, metric: str = "revenue") -> ComparabilityResult:
    """
    Convenience bridge comparing two Claim objects or profile record dicts.
    """
    def to_obs(c: Any) -> FinancialObservation:
        if isinstance(c, FinancialObservation):
            return c
        if isinstance(c, dict):
            # Claim dict (from json/model_dump) or profile record dict
            if "reporting_period" in c or "field" in c:
                p = c.get("reporting_period") or {}
                val = c.get("value")
                fld = c.get("field") or ""
                m_name = fld.rsplit(".", 1)[-1]
                metrics = {metric: val}
                if m_name:
                    metrics[m_name] = val
                return FinancialObservation(
                    organisation_number=str(org or ""),
                    fiscal_year=str(p.get("fiscal_year") or ""),
                    period_start=str(p.get("period_start") or ""),
                    period_end=str(p.get("period_end") or ""),
                    currency=p.get("currency"),
                    unit=p.get("unit"),
                    account_type=p.get("account_type") or "SELSKAP",
                    metrics=metrics
                )
            else:
                p = c.get("period", {}) or {}
                metrics = {k: v for k, v in c.items() if k not in {"period", "account_type", "currency", "record_id"}}
                return FinancialObservation(
                    organisation_number=str(org or ""),
                    fiscal_year=str(p.get("tilDato", "")[:4]),
                    period_start=str(p.get("fraDato") or ""),
                    period_end=str(p.get("tilDato") or ""),
                    currency=c.get("currency"),
                    unit=c.get("unit"),
                    account_type=c.get("account_type") or "SELSKAP",
                    metrics=metrics
                )

        p = getattr(c, "reporting_period", None) or {}
        val = getattr(c, "value", None)
        fld = getattr(c, "field", "")
        metrics = {metric: val}
        m_name = fld.rsplit(".", 1)[-1]
        if m_name:
            metrics[m_name] = val
        return FinancialObservation(
            organisation_number=str(org or ""),
            fiscal_year=str(p.get("fiscal_year") or ""),
            period_start=str(p.get("period_start") or ""),
            period_end=str(p.get("period_end") or ""),
            currency=p.get("currency"),
            unit=p.get("unit"),
            account_type=p.get("account_type") or "SELSKAP",
            metrics=metrics
        )

    obs1 = to_obs(claim1)
    obs2 = to_obs(claim2)
    gate = ComparablePeriodGate()
    return gate.compare(obs1, obs2, metric=metric)
