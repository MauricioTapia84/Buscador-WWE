from api.main import list_wrestlers

def test_wrestlers():
    payload = list_wrestlers()
    assert isinstance(payload, list)
