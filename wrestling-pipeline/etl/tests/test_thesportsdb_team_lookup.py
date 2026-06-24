import responses
import json
from etl import extract_thesportsdb as ets

@responses.activate
def test_fetch_players_by_team(monkeypatch, tmp_path):
    team_id = '133602'  # arbitrary
    api_url = f"https://www.thesportsdb.com/api/v1/json/3/lookup_all_players.php?id={team_id}"
    fake = {'player': [{'idPlayer': '1', 'strPlayer': 'Foo Bar'}]}
    responses.add(responses.GET, api_url, json=fake, status=200)

    res = ets.fetch_players_by_team(team_id)
    assert isinstance(res, list)
    assert res[0]['strPlayer'] == 'Foo Bar'
