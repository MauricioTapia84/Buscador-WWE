import pandas as pd
import os
from etl.transform.normalize import normalize_wrestlers


def test_normalize_wrestlers_creates_outputs(tmp_path, monkeypatch):
    proc = tmp_path / "processed"
    proc.mkdir()
    # create fake sources
    ts = proc / "wrestlers_thesportsdb.csv"
    wiki = proc / "wrestlers_extracted.csv"
    pd.DataFrame([{"name":"John Cena","id":"1"}]).to_csv(ts, index=False)
    pd.DataFrame([{"name":"J. Cena","id":"2"}]).to_csv(wiki, index=False)

    normalize_wrestlers(processed_dir=str(proc))
    assert (proc / 'wrestlers.csv').exists()
    assert (proc / 'wrestlers_metadata.json').exists()
