import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_session
from app.core.security import get_password_hash
from app.db.database import Base
from app.main import app
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_test_users(db: Session) -> None:
    db.add_all(
        [
            User(
                name="Admin Test",
                email="admin@eduflow.ai",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            ),
            User(
                name="Operator Test",
                email="operator@eduflow.ai",
                hashed_password=get_password_hash("operator123"),
                role="operator",
            ),
            User(
                name="Viewer Test",
                email="viewer@eduflow.ai",
                hashed_password=get_password_hash("viewer123"),
                role="viewer",
            ),
        ]
    )
    db.commit()


@pytest.fixture()
def client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        seed_test_users(db)
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(client: TestClient) -> dict[str, str]:
    return auth_header(client, "admin@eduflow.ai", "admin123")


@pytest.fixture()
def operator_headers(client: TestClient) -> dict[str, str]:
    return auth_header(client, "operator@eduflow.ai", "operator123")


@pytest.fixture()
def viewer_headers(client: TestClient) -> dict[str, str]:
    return auth_header(client, "viewer@eduflow.ai", "viewer123")
