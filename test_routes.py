import pytest
import atexit
from app import app, db
from config import Config
from random import randint
from models import User


class TestUser:
    username = f"test_{randint(10000, 99999)}"
    name = "test user"
    password = "test1234"
    jwt_token = ...
    jwt_refresh_token = ...


@atexit.register
def remove_test_user():
    user = db.session.query(User). \
        filter(User.username == TestUser.username). \
        first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def client():
    app.config.from_object(Config)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_health_check(client):
    r = client.get("/health_check")
    assert r.status_code == 200


def test_register_user(client):
    data = {
        "username": TestUser.username,
        "name": TestUser.name,
        "password": TestUser.password
    }
    r = client.post("/user", json=data)
    assert r.status_code == 201, r.get_json().get("error")


def test_login_user(client):
    data = {
        "username": TestUser.username,
        "password": TestUser.password
    }
    r = client.post("/auth", json=data)
    jdata = r.get_json()
    assert r.status_code == 200, jdata.get("error")
    TestUser.jwt_token = jdata.get("access_token")
    TestUser.jwt_refresh_token = jdata.get("refresh_token")


def test_refresh_access_token(client):
    headers = {
        "Authorization": f"Bearer {TestUser.jwt_refresh_token}"
    }
    r = client.put("/auth", headers=headers)
    jdata = r.get_json()
    assert r.status_code == 200, jdata.get("error")
    TestUser.jwt_token = jdata.get("access_token")


def test_get_user(client):
    headers = {
        "Authorization": f"Bearer {TestUser.jwt_token}"
    }
    r = client.get("/user", headers=headers)
    jdata = r.get_json()
    assert r.status_code == 200, jdata.get("error")
    assert jdata.get("username") == TestUser.username, \
        f'{jdata.get("username")} != {TestUser.username}'


def test_modify_user_name(client):
    headers = {
        "Authorization": f"Bearer {TestUser.jwt_token}"
    }
    data = {
        "name": "new name"
    }
    r = client.patch("/user", json=data, headers=headers)
    assert r.status_code == 204, r.get_json().get("error")


def test_modify_user_password(client):
    headers = {
        "Authorization": f"Bearer {TestUser.jwt_token}"
    }
    data = {
        "password": "new_password",
        "old_password": TestUser.password
    }
    r = client.patch("/user", json=data, headers=headers)
    assert r.status_code == 204, r.get_json().get("error")
