from main import get_wrestler, health, list_titles, list_wrestlers

def test_wrestlers():
    payload = list_wrestlers()
    assert isinstance(payload, list)


def test_titles():
    payload = list_titles()
    assert isinstance(payload, list)
    if payload:
        first = payload[0]
        assert "location" in first
        assert "era" in first
        assert "overall_reign" in first


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


def test_wrestler_title_history_is_richer():
    payload = list_wrestlers()
    history_owner = next((item for item in payload if item.get("title_history")), None)
    if history_owner:
        reign = history_owner["title_history"][0]
        assert "location" in reign
        assert "era" in reign
        assert "end_date" in reign
        assert "defeated_for_title" in reign
