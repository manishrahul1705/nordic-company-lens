"""Bundled indexes decode once even when source workers start concurrently."""
import io,json,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from signalpost.web import shared_identifiers as shared


def test_both_indexes_load_once_per_process_under_concurrent_misses(monkeypatch):
    calls=Counter()
    def opened(path,*args,**kwargs):
        calls[path.name]+=1
        time.sleep(.02)
        return io.StringIO(json.dumps({'loaded':path.name}))
    shared._bundled.cache_clear()
    monkeypatch.setattr(shared.gzip,'open',opened)
    names=['shared_identifiers.json.gz','cc_orgnr_index.json.gz']*8
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(shared.bundled,names))
        assert calls=={'shared_identifiers.json.gz':1,'cc_orgnr_index.json.gz':1}
        for name in set(names):
            matching=[result for name_arg,result in zip(names,results) if name_arg==name]
            assert all(result is matching[0] for result in matching)
    finally:shared._bundled.cache_clear()
