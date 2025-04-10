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