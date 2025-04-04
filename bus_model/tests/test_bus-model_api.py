from flask.testing import FlaskClient

def test_home(client: FlaskClient) -> None:
    """Test the / endpoint. It returns a TestResponse instead of a Request Response, so we must use response.json"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {'message': 'Hello, World!'}
