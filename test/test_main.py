from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_app():
    response = client.get("/")
    assert response.status_code == 404  # Assuming no root endpoint is defined
