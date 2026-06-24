import responses
import json
from extract_thesportsdb import fetch_wrestlers_by_name, extract_all

API_BASE = "https://www.thesportsdb.com/api/v1/json/3"

@responses.activate
def test_fetch_success():
    name = "Test Wrestler"
    payload = {"player": [{"idPlayer": "10", "strPlayer": name, "strDescriptionEN": "desc"}]}
    responses.add(responses.GET, f"{API_BASE}/searchplayers.php?p=Test%20Wrestler", json=payload, status=200)
    players = fetch_wrestlers_by_name(name)
    assert isinstance(players, list)
    assert players[0]["strPlayer"] == name

@responses.activate
def test_fetch_empty_then_token_fallback():
    name = "John Doe"
    # initial full name search returns empty
    responses.add(responses.GET, f"{API_BASE}/searchplayers.php?p=John%20Doe", json={"player": None}, status=200)
    # token fallback for 'John' returns a result
    responses.add(responses.GET, f"{API_BASE}/searchplayers.php?p=John", json={"player": [{"idPlayer":"11","strPlayer":"John"}]}, status=200)
    players = fetch_wrestlers_by_name(name)
    assert players and players[0]["strPlayer"] == "John"

@responses.activate
def test_extract_all_uses_fetch(monkeypatch):
    # monkeypatch fetch_wrestlers_by_name to simulate network
    monkeypatch.setattr('extract_thesportsdb.fetch_wrestlers_by_name', lambda n: [{"idPlayer":"99","strPlayer":n}])
    df = extract_all(["Alpha"])
    assert not df.empty
    assert df.iloc[0]["name"] == "Alpha"
