import pytest
from flask import g
from flask import session

from shpr.models import User


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            User.query.filter_by(username="a").first()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user.username == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username."), ("test", "a", b"Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session


def test_register_duplicate_username(client, app):
    response = client.post("/auth/register", data={"username": "test", "password": "test"})
    assert b"User test is already registered." in response.data


def test_login_invalid_username(client):
    response = client.post("/auth/login", data={"username": "invalid", "password": "test"})
    assert b"Incorrect username." in response.data


def test_login_invalid_password(client):
    response = client.post("/auth/login", data={"username": "test", "password": "wrong"})
    assert b"Incorrect password." in response.data


def test_access_protected_route_without_login(client):
    response = client.get("/create")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"
