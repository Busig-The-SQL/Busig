import requests
import os

def test_v1_routes():
    url = os.getenv("GATEWAY_URI") + "/v1/routes"
    response = requests.get(url)
    assert response.status_code == 200
    json = response.json()
    assert len(json) > 0
    assert json[0]["name"] is not None
    assert len(json[0]["stop_ids"]) > 0