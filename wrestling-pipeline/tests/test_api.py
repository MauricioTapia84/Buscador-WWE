from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_wrestlers():
    r = client.get('/wrestlers')
    assert r.status_code == 200
