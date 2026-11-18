"""Offline SSB KLASS titles; versioned source snapshots: data/ and docs/SOURCES.md."""
import json
from pathlib import Path

TABLE = json.loads((Path(__file__).parent / 'data' / 'nace-klass-2026-10-13.json').read_text(encoding='utf8'))


def unspecified(value):
    return isinstance(value, dict) and (value.get('kode') == '00.000' or
        str(value.get('beskrivelse', '')).strip().casefold() == 'uoppgitt')


def english_title(value, version_id=None):
    if not isinstance(value, dict) or unspecified(value):
        return None
    code = str(value.get('kode', ''))
    description = ' '.join(str(value.get('beskrivelse', '')).split()).casefold()
    candidates = []
    matched = []
    for version in TABLE['versions']:
        if version_id is not None and version['version_id'] != version_id:
            continue
        subclass = version['subclasses'].get(code)
        title = version['titles'].get(code)
        if title:
            candidates.append(title)
            if subclass and description == ' '.join(subclass['registered_title'].split()).casefold():
                matched.append(title)
    # Conflicting versions need an exact registered-label match. No guessing.
    titles = set(matched or candidates)
    return next(iter(titles)) if len(titles) == 1 else None


def _divisions():
    """Two-digit division titles per KLASS version, from the same dated SSB snapshots."""
    out = {}
    for version in TABLE['versions']:
        raw = Path(__file__).parent / 'data' / ('ssb-' + version['standard'].lower() + '-en-' + version['download_date'] + '.json')
        items = json.loads(raw.read_text(encoding='utf8'))['classificationItems']
        out[version['version_id']] = {i['code']: i['name'] for i in items if i['level'] == '2'}
    return out


DIVISIONS = _divisions()


def division_title(value):
    """SSB KLASS English title of the registered code's two-digit division, or None.

    The version is the one whose subclass label matches the registered code (as in
    english_title); with no single match, the current standard (first version) is used.
    """
    if not isinstance(value, dict) or unspecified(value):
        return None
    code = str(value.get('kode', ''))
    division = code.split('.', 1)[0]
    description = ' '.join(str(value.get('beskrivelse', '')).split()).casefold()
    matched = [v['version_id'] for v in TABLE['versions'] if (v['subclasses'].get(code) or {}).get('registered_title') is not None
               and description == ' '.join(v['subclasses'][code]['registered_title'].split()).casefold()]
    titles = {DIVISIONS[v].get(division) for v in matched} - {None}
    if len(titles) == 1:
        return next(iter(titles))
    return DIVISIONS[TABLE['versions'][0]['version_id']].get(division)
