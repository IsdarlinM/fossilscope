import json
from datetime import datetime, timezone, timedelta
from sric.workspace import Workspace
from fossilscope.core import FossilEngine
from fossilscope.models import Observation, Relationship

def test_lifecycle_api_diff_decay_clusters_and_temporal_graph(tmp_path):
    e = FossilEngine(Workspace.create(tmp_path, 'ws').root)
    old = datetime.now(timezone.utc) - timedelta(days=1200)
    e.add_observation(Observation(observation_id='o1', entity_type='api_endpoint', value='https://old.example/v1/export', source='archive', last_seen=old, evidence_ids=['E1'], metadata={'acquisition': 'brand-a'}))
    e.add_observation(Observation(observation_id='o2', entity_type='api_endpoint', value='https://old.example/v1/export', source='sdk', current_reference=True, current_reachable=True, evidence_ids=['E2'], metadata={'acquisition': 'brand-a'}))
    life = e.lifecycle()[0]
    assert life['state'] == 'CURRENTLY_REACHABLE'
    decay = e.confidence_decay('https://old.example/v1/export')
    assert 'historical_confidence' in decay
    assert e.clusters()[0]['cluster'] == 'brand-a'
    assert e.temporal_graph()['nodes']
    before = tmp_path / 'before.json'
    after = tmp_path / 'after.json'
    before.write_text(json.dumps({'paths': {'/v1/export': {}, '/v1/keep': {}}}))
    after.write_text(json.dumps({'paths': {'/v1/keep': {}}}))
    diff = e.historical_api_diff(before, after)
    assert diff['removed_from_documentation'] == ['/v1/export'] and diff['still_referenced'] == ['/v1/export']

def test_acquisition_lineage_is_explicit(tmp_path):
    e = FossilEngine(Workspace.create(tmp_path, 'ws').root)
    e.add_relationship(Relationship(relationship_id='r1', source_value='brand-a', target_value='company-b', relationship_type='acquired_by', confidence=0.9, evidence_ids=['E1']))
    assert e.acquisition_lineage()[0]['relationship'] == 'acquired_by'
