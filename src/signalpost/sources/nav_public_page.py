"""Narrow parser for NAV's public job page, used only if its feed token is down."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from uuid import UUID

from ..identity.orgnr import valid
from .nav import timestamp


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts: list[str] = []
        self.h1: list[str] = []
        self._script = False
        self._heading = False
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self._script = True
            self._parts = []
        elif tag == 'h1':
            self._heading = True
            self._parts = []

    def handle_endtag(self, tag):
        if tag == 'script' and self._script:
            self.scripts.append(''.join(self._parts))
            self._script = False
        elif tag == 'h1' and self._heading:
            self.h1.append(''.join(self._parts))
            self._heading = False

    def handle_data(self, data):
        if self._script or self._heading:
            self._parts.append(data)


def _flight_payload(script: str) -> str | None:
    marker = 'self.__next_f.push('
    at = script.find(marker)
    if at < 0:
        return None
    body = script[at + len(marker):]
    if body.endswith(');'):
        body = body[:-2]
    elif body.endswith(')'):
        body = body[:-1]
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return None
    return payload[1] if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], str) else None


def _records(text: str):
    decoder = json.JSONDecoder()
    # The initial page's RSC payload contains JSON objects. Find ad objects
    # from their required fields, without interpreting arbitrary page text.
    for match in re.finditer(r'"orgnr"\s*:\s*"\d{9}"', text):
        pos = match.start()
        left = max(0, pos - 6000)
        for start in (m.start() for m in re.finditer(r'\{', text[left:pos])):
            try:
                obj, _ = decoder.raw_decode(text, left + start)
            except (ValueError, TypeError):
                continue
            if (isinstance(obj, dict) and isinstance(obj.get('employer'), dict)
                    and obj.get('status') in {'ACTIVE', 'INACTIVE', 'DELETED'}
                    and timestamp(obj.get('expires')) is not None
                    and isinstance(obj.get('title'), str)):
                yield obj


def parse_public_ad_page(body: bytes, expected_uuid: str):
    """Return only the public fields needed to confirm one active ad."""
    try:
        expected_uuid = str(UUID(expected_uuid))
        if len(body) > 2_000_000:
            return None
        page = _Page()
        page.feed(body.decode('utf-8', errors='replace'))
        heading = ' '.join(' '.join(page.h1).split())
        normalized_heading = re.sub(r'\W+', ' ', heading.casefold()).strip()
        for script in page.scripts:
            payload = _flight_payload(script)
            if payload is None:
                continue
            for record in _records(payload):
                title = ' '.join(str(record.get('title') or '').split())
                if re.sub(r'\W+', ' ', title.casefold()).strip() != normalized_heading:
                    continue
                employer = record['employer']
                orgnr = str(employer.get('orgnr') or '').strip()
                published = record.get('published')
                expires = record.get('expires')
                if not valid(orgnr) or timestamp(published) is None or timestamp(expires) is None:
                    continue
                return {'uuid': expected_uuid, 'status': record['status'], 'title': title,
                        'published': published, 'expires': expires,
                        'employer': {'orgnr': orgnr, 'name': str(employer.get('name') or '')},
                        'locationList': record.get('locationList') or [],
                        'occupationCategories': record.get('occupationCategories') or []}
    except (ValueError, UnicodeError):
        return None
    return None
