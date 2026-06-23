import os
import json
import pandas as pd
from pathlib import Path
from etl.normalize import normalize_wrestlers


def write_csv(path, content):
    path.write_text(content)


def read_meta(proc):
    return json.loads((proc / 'wrestlers_metadata.json').read_text())


def test_dedupe_merges_at_low_threshold(tmp_path, monkeypatch):
    proc = tmp_path / 'processed'
    proc.mkdir()
    # create a source with two similar names
    data = 'name\nJohn Doe\nJon Doe\nJane Smith\n'
    (proc / 'wrestlers_thesportsdb.csv').write_text(data)
    monkeypatch.chdir(tmp_path)
    # set low threshold so similar names merge
    monkeypatch.setenv('WRESTLER_DEDUPE_SCORE', '60')
    normalize_wrestlers(processed_dir=str(proc))
    meta = read_meta(proc)
    assert meta['merges_performed'] >= 1


def test_dedupe_keeps_separate_at_high_threshold(tmp_path, monkeypatch):
    proc = tmp_path / 'processed'
    proc.mkdir()
    data = 'name\nJohn Doe\nJon Doe\nJane Smith\n'
    (proc / 'wrestlers_thesportsdb.csv').write_text(data)
    monkeypatch.chdir(tmp_path)
    # set very high threshold to avoid merges
    monkeypatch.setenv('WRESTLER_DEDUPE_SCORE', '99')
    normalize_wrestlers(processed_dir=str(proc))
    meta = read_meta(proc)
    assert meta['merges_performed'] == 0
