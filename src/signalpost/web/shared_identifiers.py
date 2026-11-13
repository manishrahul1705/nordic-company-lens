"""Shared registry comparisons; counts never override an ownership veto."""
import gzip
import json
import re
import unicodedata
import threading
from functools import lru_cache
from pathlib import Path

FORMS = {'as','asa','ans','da','enk','nuf','sa','ba','ks','iks','sti'}
FILLER = {'og','and','the','av','of','holding','invest','eiendom','service','consult','group','gruppen','norge','norway'}


def folded(value):
    text = str(value or '').casefold().replace('\u00e6','ae').replace('\u00f8','o').replace('\u00e5','a')
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))


def name_tokens(value):
    words = re.findall(r'[a-z0-9]+', folded(value))
    while words and words[-1] in FORMS:
        words.pop()
    return words


def name_key(value):
    return ' '.join(sorted(set(name_tokens(value)) - FILLER))


def phone_key(value):
    text = str(value or '').strip()
    if text.startswith('+') and not text.startswith('+47'):
        return ''
    n = re.sub(r'\D','',text)
    if n.startswith('0047'): n = n[4:]
    elif len(n)==10 and n.startswith('47'): n = n[2:]
    return n if len(n)==8 else ''


_BUNDLE_LOCK = threading.RLock()


def bundled(filename):
    # lru_cache alone allows duplicate concurrent misses. Source workers must
    # share a single initial decode of each bundled index, too.
    with _BUNDLE_LOCK:
        return _bundled(filename)


@lru_cache(maxsize=4)
def _bundled(filename):
    for path in (Path(__file__).resolve().parents[1]/'data'/filename, Path(__file__).resolve().parents[3]/'data'/filename):
        if path.exists():
            with gzip.open(path,'rt',encoding='utf8') as f: return json.load(f)
    return {}
