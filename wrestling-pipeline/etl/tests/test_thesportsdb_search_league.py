import responses
from etl import extract_thesportsdb as ets

@responses.activate
def test_search_teams_by_league():
    league = 'WWE League'
    url = f"https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l={league}"
    resp = {'teams': [{'idTeam': '200', 'strTeam': 'WWE'}]}
    responses.add(responses.GET, url, json=resp, status=200)
    teams = ets.search_teams_by_league(league)
    assert isinstance(teams, list)
    assert teams[0]['idTeam'] == '200'
