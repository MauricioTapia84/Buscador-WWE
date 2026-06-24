import os
import json
from etl.transform.normalize import normalize_wrestlers, normalize_matches

def test_wrestlers_metadata(tmp_path, monkeypatch):
    proc = tmp_path / 'processed'
    proc.mkdir()
    # create small source file
    ts = proc / 'wrestlers_thesportsdb.csv'
    ts.write_text('name\nJohn Doe')
    monkeypatch.chdir(str(tmp_path))
    normalize_wrestlers(processed_dir=str(proc))
    meta = json.loads((proc / 'wrestlers_metadata.json').read_text())
    assert 'generated_at' in meta and 'rows_input' in meta


def test_matches_metadata(tmp_path, monkeypatch):
    proc = tmp_path / 'processed'
    proc.mkdir()
    m = proc / 'matches_normalized.csv'
    m.write_text('Winner,Loser,EventDate\nA,B,2020-01-01')
    monkeypatch.chdir(str(tmp_path))
    normalize_matches(processed_dir=str(proc), raw_dir=str(proc))
    meta = json.loads((proc / 'matches_metadata.json').read_text())
    assert meta['rows'] == 1
