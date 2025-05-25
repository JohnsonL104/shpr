import pytest

from shpr import create_app
from shpr.db import db
from shpr.models import User, Item


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://user:Password123@127.0.0.1:5432/shpr_test"
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
        # Insert test users
        user1 = User(username="test", password="pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f")
        user2 = User(username="other", password="pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79")
        db.session.add_all([user1, user2])
        db.session.commit()
        # Insert test post
        item = Item(description="test\ndesc", requestor_id=user1.id, created="2018-01-01 00:00:00", link="https://example.com")
        item2 = Item(description="test\ndesc2", requestor_id=user1.id, created="2018-01-01 00:00:00", link="https://example.com", completed_by_id=user2.id, completed_date="2018-01-01 00:00:00")
        db.session.add(item)
        db.session.add(item2)
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture(autouse=True)
def clean_db(app):
    """Ensure a clean database state before each test."""
    with app.app_context():
        db.session.rollback()  # Roll back any uncommitted transactions
        db.drop_all()          # Drop all tables
        db.create_all()        # Recreate all tables
        # Reinsert test data
        user1 = User(username="test", password="pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f")
        user2 = User(username="other", password="pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79")
        db.session.add_all([user1, user2])
        db.session.commit()
        item = Item(description="test\ndesc", requestor_id=user1.id, created="2018-01-01 00:00:00", link="https://example.com")
        item2 = Item(description="test\ndesc2", requestor_id=user1.id, created="2018-01-01 00:00:00", link="https://example.com", completed_by_id=user2.id, completed_date="2018-01-01 00:00:00")
        db.session.add(item)
        db.session.add(item2)
        db.session.commit()
