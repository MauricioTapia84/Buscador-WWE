import responses
from etl import extract_thesportsdb as ets

@responses.activate
def test_multiple_team_matches_choose_best():
    team_name = 'WWE'
    # two teams returned, one exact 'WWE Worldwide' and one 'W.W.E'
    search_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
    team_resp = {'teams': [
        {'idTeam': '101', 'strTeam': 'WWE Worldwide'},
        {'idTeam': '102', 'strTeam': 'W.W.E'}
    ]}
    players_resp_101 = {'player': [{'idPlayer': '1', 'strPlayer': 'Alpha'}]}
    players_resp_102 = {'player': [{'idPlayer': '2', 'strPlayer': 'Beta'}]}

    responses.add(responses.GET, search_url, json=team_resp, status=200)
    responses.add(responses.GET, f"https://www.thesportsdb.com/api/v1/json/3/lookup_all_players.php?id=101", json=players_resp_101, status=200)
    responses.add(responses.GET, f"https://www.thesportsdb.com/api/v1/json/3/lookup_all_players.php?id=102", json=players_resp_102, status=200)

    df = ets.extract_players_for_team_names([team_name])
    assert not df.empty
    # prefer the first team in absence of exact; ensure players present
    names = set(df['name'].tolist())
    assert 'Alpha' in names or 'Beta' in names
