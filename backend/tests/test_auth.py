def _register(client, email="alice@example.com", password="StrongPass123", role="STUDENT"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Alice Example", "role": role},
    )


def _login(client, email="alice@example.com", password="StrongPass123"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_register_success(client):
    resp = _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "alice@example.com"
    assert body["data"]["status"] == "ACTIVE"


def test_register_duplicate_email_conflicts(client):
    _register(client, email="dup@example.com")
    resp = _register(client, email="dup@example.com")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_login_success(client):
    _register(client, email="bob@example.com")
    resp = _login(client, email="bob@example.com")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


def test_login_wrong_password(client):
    _register(client, email="carol@example.com")
    resp = _login(client, email="carol@example.com", password="wrong-password")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_refresh_success_and_rotation(client):
    _register(client, email="dave@example.com")
    tokens = _login(client, email="dave@example.com").json()["data"]

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()["data"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # old refresh token was rotated out — reuse must fail
    reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuse.status_code == 401


def test_refresh_invalid_token(client):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_me_requires_auth(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


def test_me_with_valid_token(client):
    _register(client, email="erin@example.com")
    tokens = _login(client, email="erin@example.com").json()["data"]
    resp = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "erin@example.com"


def test_student_cannot_list_users(client):
    _register(client, email="frank@example.com", role="STUDENT")
    tokens = _login(client, email="frank@example.com").json()["data"]
    resp = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"
