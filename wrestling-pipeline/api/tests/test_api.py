from main import get_wrestler, health, list_titles, list_wrestlers

def test_wrestlers():
    payload = list_wrestlers()
    assert isinstance(payload, list)


def test_titles():
    payload = list_titles()
    assert isinstance(payload, list)


def test_health():
    payload = health()
    assert payload.get("status") == "ok"


def test_get_wrestler_not_found():
    try:
        get_wrestler(999)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 404
    else:
        raise AssertionError("Expected 404 when wrestler does not exist")
