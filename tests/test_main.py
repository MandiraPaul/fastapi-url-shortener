from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "URL Shortener API is running"
    }


def test_invalid_url():
    response = client.post(
        "/shorten",
        json={"url": "hello"}
    )

    assert response.status_code == 422


def test_unknown_short_code():
    response = client.get(
        "/this-code-does-not-exist",
        follow_redirects=False
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Short URL not found"
    }