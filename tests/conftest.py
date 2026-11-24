import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.core.database import Base, get_db
from app.main import app
from app.core.limiter import limiter
from app.models import user, wallet, transaction, audit_log
from app.models.wallet import Wallet


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    limiter.reset()


@pytest.fixture
def registered_users(client, db_session):
    users = {}

    for name in ("alice", "bob", "charlie"):
        response = client.post(
            "/auth/register",
            json={
                "email": f"{name}@example.com",
                "password": f"SecureWallet-{name.title()}-2026!",
                "full_name": name.title(),
            },
        )
        assert response.status_code == 201
        users[name] = response.json()
        wallet_record = db_session.scalar(
            select(Wallet).where(Wallet.user_id == users[name]["id"])
        )
        users[name]["wallet_id"] = wallet_record.id

    return users


@pytest.fixture
def authenticated_clients(client, registered_users):
    clients = {}

    for name in ("alice", "bob", "charlie"):
        response = client.post(
            "/auth/login",
            json={
                "email": f"{name}@example.com",
                "password": f"SecureWallet-{name.title()}-2026!",
            },
        )
        assert response.status_code == 200

        clients[name] = {
            "headers": {
                "Authorization": f"Bearer {response.json()['access_token']}"
            },
            "user": registered_users[name],
        }

    return clients
