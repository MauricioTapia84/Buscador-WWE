import pytest
import pandas as pd
from etl.extract_thesportsdb import get_wrestler


def test_get_wrestler_mock(monkeypatch):
    class DummyResp:
        def __init__(self, json_data):
            self._json = json_data
        def json(self):
            return self._json

    def fake_requests_get(url, timeout=5):
        return DummyResp({"player": [{
            "strPlayer": "John Example",
            "strHeight": "190 cm",
            "strWeight": "100 kg",
            "strNationality": "USA",
            "strDescriptionEN": "Example wrestler"
        }]})

    try:
        monkeypatch.setattr('etl.extractors.thesportsdb.requests_get_with_retry', fake_requests_get)
    except Exception:
        monkeypatch.setattr('etl.extract_thesportsdb.requests_get_with_retry', fake_requests_get)

    res = get_wrestler("John")
    assert res is not None
    assert res["name"] == "John Example"