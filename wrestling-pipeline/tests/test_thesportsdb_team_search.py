import responses
import json
from etl import extract_thesportsdb as ets

@responses.activate
def test_search_teams_and_extract(monkeypatch):
    team_name = 'WWE'
    search_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
    team_resp = {'teams': [{'idTeam': '100', 'strTeam': 'WWE'}]}
    players_url = f"https://www.thesportsdb.com/api/v1/json/3/lookup_all_players.php?id=100"
    players_resp = {'player': [{'idPlayer': '1', 'strPlayer': 'John Doe'}]}

    responses.add(responses.GET, search_url, json=team_resp, status=200)
    responses.add(responses.GET, players_url, json=players_resp, status=200)

    df = ets.extract_players_for_team_names([team_name])
    assert not df.empty
    assert df.iloc[0]['name'] == 'John Doe'
