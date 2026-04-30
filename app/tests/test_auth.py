from fastapi.testclient import TestClient


def test_login_with_valid_user_returns_token(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "admin@eduflow.ai", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_viewer_cannot_create_student(client: TestClient, viewer_headers: dict[str, str]) -> None:
    response = client.post(
        "/students",
        headers=viewer_headers,
        json={"name": "Viewer Blocked", "email": "viewer.student@example.com", "cpf": "11122233344"},
    )
    assert response.status_code == 403
