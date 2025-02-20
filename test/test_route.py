from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_integration_json():
    response = client.get("/application.json")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["descriptions"]["app_name"] == "Twitter NG Trends Monitor"


def test_tick():
    payload = {
        "return_url": "http://example.com",
        "channel_id": "test_channel",
        "settings": [],
    }
    response = client.post("/tick", json=payload)
    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
