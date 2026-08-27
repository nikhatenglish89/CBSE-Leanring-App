import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.base import Base
from app.modules.auth.seed import seed_roles_and_permissions
from app.modules.classes.seed import seed_academic_baseline
from app.modules.practice.seed import seed_practice_sets

# In-memory SQLite shared across the whole test session via StaticPool (a
# single connection), so tables created once persist across requests within
# a test.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_roles_and_permissions(db)
        seed_academic_baseline(db)
        seed_practice_sets(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def solve_captcha(client) -> dict:
    """Fetches a real CAPTCHA challenge and decodes its expected answer
    from the signed token — legitimate for tests since the test process
    trusts the same JWT secret the token was signed with, unlike a real
    attacker who only ever sees the rendered SVG."""
    from app.core.security import decode_token

    challenge = client.get("/api/v1/auth/captcha").json()["data"]
    code = decode_token(challenge["token"], expected_type="captcha")["sub"]
    return {"captcha_token": challenge["token"], "captcha_answer": code}
