import json
from fossilscope.core import FossilEngine

def test_openapi_and_ct_passive_collectors(tmp_path):
    ws = tmp_path / 'ws'
    ws.mkdir()
    (ws / 'workspace.json').write_text('{}')
    engine = FossilEngine(ws)
    openapi = tmp_path / 'api.json'
    openapi.write_text(json.dumps({'paths': {'/v1/export': {'get': {}}, '/v2/me': {'get': {}}}}))
    assert engine.collect_adapter(openapi, 'openapi') == 2
    ct = tmp_path / 'ct.json'
    ct.write_text(json.dumps([{'dns_names': ['api.old.example', '*.legacy.example'], 'not_before': '2020-01-01T00:00:00Z', 'not_after': '2021-01-01T00:00:00Z'}]))
    assert engine.collect_adapter(ct, 'ct') == 2
    values = {x['value'] for x in engine.store.load()['observations']}
    assert '/v1/export' in values
    assert 'legacy.example' in values

def test_passive_collector_rejects_unknown_adapter(tmp_path):
    ws = tmp_path / 'ws'
    ws.mkdir()
    (ws / 'workspace.json').write_text('{}')
    p = tmp_path / 'x.txt'
    p.write_text('example.com')
    try:
        FossilEngine(ws).collect_adapter(p, 'internet-wide-scrape')
    except ValueError as exc:
        assert 'unsupported passive adapter' in str(exc)
    else:
        raise AssertionError('unknown adapter must fail closed')
