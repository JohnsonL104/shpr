import pytest

from shpr.db import db
from shpr.models import Item
from sqlalchemy import select


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b'href="/1/update"' not in response.data
    assert b"swipe-item" not in response.data

    auth.login()
    response = client.get("/")
    assert b'<a href="/auth/logout">Log Out</a>' in response.data
    assert b"for test on 2018-01-01" in response.data
    assert b"swipe-item" in response.data
    assert b"test\ndesc" in response.data
    assert b"test\ndesc2" not in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize(
    ("username", "status", "count"),
    (
        ("", "requested", 1),
        ("test", "requested", 1),
        ("other", "requested", 0),
        ("", "completed", 1),
        ("test", "completed", 1),
        ("other", "completed", 0),
        ("", "all", 2),
        ("test", "all", 2),
        ("other", "all", 0)
    )
)
def test_index_filter(client, auth, username, status, count):
    auth.login()
    response = client.get("/", query_string={"username": username, "status": status})
    assert response.status_code == 200
    # Check that "Requested for " appears in the response data the expected number of times
    assert response.data.count(b"Requested for ") == count
    

@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


def test_author_required(client):
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/3/update", "/3/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    response = client.post("/create", data={"description": "testdescription", "link": "https://example.com"})
    assert response.status_code == 302

    with app.app_context():
        items = db.session.execute(select(Item)).scalars().all()
        count = len(items)
        assert count == 3
        assert items[2].description == "testdescription"
        assert items[2].link == "https://example.com"


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    response = client.post("/1/update", data={"description": "updateddescription", "link": "https://updated-link.com"})
    assert response.status_code == 302  # Ensure redirection after successful update

    with app.app_context():
        result = db.session.execute(select(Item).where(Item.id == 1))
        item = result.scalar_one_or_none()
        assert item.description == "updateddescription"
        assert item.link == "https://updated-link.com"


# @pytest.mark.parametrize("path", ("/create", "/1/update"))
# def test_create_update_validate(client, auth, path):
#     auth.login()
#     response = client.post(path, data={"title": "", "body": ""})
#     assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        result = db.session.execute(select(Item).where(Item.id == 1))
        item = result.scalar_one_or_none()
        assert item is None


def test_create_invalid_data(client, auth):
    auth.login()
    response = client.post("/create", data={"description": "", "link": ""})
    assert b"Description is required." in response.data
    assert response.status_code == 200  # Ensure the form is re-rendered


def test_update_invalid_data(client, auth):
    auth.login()
    assert client.get("/1/update").status_code == 200
    response = client.post("/1/update", data={"description": "", "link": ""})
    assert b"Description is required." in response.data
    assert response.status_code == 200  # Ensure the form is re-rendered


def test_complete_item(client, auth, app):
    auth.login()
    response = client.post("/1/complete")
    assert response.status_code == 200

    with app.app_context():
        item = db.session.execute(select(Item).where(Item.id == 1)).scalar_one()
        assert item.completed_by_id == 1
        assert item.completed_date is not None


def test_complete_item_already_completed(client, auth):
    auth.login()
    response = client.post("/2/complete")
    assert response.status_code == 400
    assert b"Item id 2 is already completed." in response.data
