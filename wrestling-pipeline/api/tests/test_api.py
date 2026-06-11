from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_wrestlers():
    r = client.get("/wrestlers")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_titles():
    r = client.get("/titles")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_get_wrestler_not_found():
    r = client.get("/wrestlers/999")
    assert r.status_code == 404
