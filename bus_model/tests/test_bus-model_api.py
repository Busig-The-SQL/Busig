from flask.testing import FlaskClient

def test_home(client: FlaskClient) -> None:
    """Test the / endpoint. It returns a TestResponse instead of a Request Response, so we must use response.json"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {'message': 'Hello, World!'}


def test_v1_get_all_stops(client: FlaskClient) -> None:
    """Tests the /v1/stops endpoint."""
    response = client.get('/v1/stops')
    assert response.status_code == 200
    json = response.json
    assert type(json) == list, f"Response is not a list, {type(json)} instead"
    assert len(json) == 2, f"Response of length 2 != {len(json)}"

    keys = ["id", "name", "code", "lat", "lon"]
    for key in keys:
        assert key in json[0], f"Key {key} not in first stop data"
        assert key in json[1], f"Key {key} not in second stop data"
    
    key_type_pairs = [
        ("id", str),
        ("name", str),
        ("code", str),
        ("lat", float),
        ("lon", float),
    ]
    for key, type_ in key_type_pairs:
        assert type(json[0][key]) == type_, f"Key {key} is not of type {type_} in first stop data"
        assert type(json[1][key]) == type_, f"Key {key} is not of type {type_} in second stop data"


def test_v1_get_one_stop(client: FlaskClient, vars) -> None:
    """Tests the /v1/stops/<stop_id> endpoint."""
    response = client.get(f'/v1/stops/{vars.stop_id1}')
    assert response.status_code == 200
    json = response.json
    assert type(json) == dict, f"Response is not a dict, {type(json)} instead"

    assert json.get("id", "") == vars.stop_id1, f"Stop id {json.get('id', '')} != {vars.stop_id1}"
    assert json.get("name", "") == "IDA Ovens", f"Stop name {json.get('name', '')} != IDA Ovens"
    assert json.get("code", "") == vars.stop_code1, f"Stop code {json.get('code', '')} != {vars.stop_code1}"
    assert type(json.get("lat", "")) == float, f"Stop lat {json.get('lat', '')} is not a float"
    assert type(json.get("lon", "")) == float, f"Stop lon {json.get('lon', '')} is not a float"
    assert json.get("direction", "") == 0, f"Stop direction {json.get('direction', '')} != 0"
    