from fastapi.testclient import TestClient
from app.main import app, state
from app.service import AutocompleteService

client = TestClient(app)


def test_endpoint_returns_200():
    state.service = AutocompleteService()
    response = client.get("/autocomplete?query=crypt")
    assert response.status_code == 200


def test_endpoint_returns_json():
    state.service = AutocompleteService()
    response = client.get("/autocomplete?query=crypt")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)