import pytest
from shpr.db import db
from shpr.models import User

from sqlalchemy import inspect


def test_get_close_db(app):
    with app.app_context():
        user = User(username="foo", password="bar")
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(username="foo").first() is not None


def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("shpr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called


def test_table_exists(app):
    with app.app_context():
        inspector = inspect(db.engine)
        assert inspector.has_table("user")
        assert inspector.has_table("item")

def test_unique_username_constraint(app):
    with app.app_context():
        user1 = User(username="testuser", password="password1")
        db.session.add(user1)
        db.session.commit()
        assert User.query.filter_by(username="testuser").first() is not None

        user2 = User(username="testuser", password="password2")
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()  # Should raise an IntegrityError due to unique constraint
