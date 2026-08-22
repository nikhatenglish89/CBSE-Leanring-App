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
    assert body["data"]["email_verified"] is False


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


def test_verify_email_with_valid_token(client):
    from app.core.security import create_email_verification_token

    register_resp = _register(client, email="grace@example.com")
    user_id = register_resp.json()["data"]["id"]
    tokens = _login(client, email="grace@example.com").json()["data"]

    me = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    ).json()["data"]
    assert me["email_verified"] is False

    verify_token = create_email_verification_token(user_id)
    resp = client.post("/api/v1/auth/verify-email", json={"token": verify_token})
    assert resp.status_code == 200
    assert resp.json()["data"]["verified"] is True

    me_after = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    ).json()["data"]
    assert me_after["email_verified"] is True


def test_verify_email_with_invalid_token(client):
    resp = client.post("/api/v1/auth/verify-email", json={"token": "not-a-real-token"})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_resend_verification_then_blocked_once_verified(client):
    from app.core.security import create_email_verification_token

    register_resp = _register(client, email="heidi@example.com")
    user_id = register_resp.json()["data"]["id"]
    tokens = _login(client, email="heidi@example.com").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.post("/api/v1/auth/resend-verification", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["sent"] is True

    verify_token = create_email_verification_token(user_id)
    client.post("/api/v1/auth/verify-email", json={"token": verify_token})

    resp = client.post("/api/v1/auth/resend-verification", headers=headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "ALREADY_VERIFIED"


def test_resend_verification_requires_auth(client):
    resp = client.post("/api/v1/auth/resend-verification")
    assert resp.status_code == 401


def test_change_password_success_and_relogin(client):
    _register(client, email="ivan@example.com", password="StrongPass123")
    tokens = _login(client, email="ivan@example.com").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "StrongPass123", "new_password": "EvenStronger456"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["changed"] is True

    # Old password no longer works, new one does.
    old_login = _login(client, email="ivan@example.com", password="StrongPass123")
    assert old_login.status_code == 401

    new_login = _login(client, email="ivan@example.com", password="EvenStronger456")
    assert new_login.status_code == 200


def test_change_password_wrong_current_password(client):
    _register(client, email="judy@example.com", password="StrongPass123")
    tokens = _login(client, email="judy@example.com").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "EvenStronger456"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CURRENT_PASSWORD_INCORRECT"

    # Original password still works — nothing was changed.
    still_works = _login(client, email="judy@example.com", password="StrongPass123")
    assert still_works.status_code == 200


def test_change_password_revokes_other_refresh_tokens(client):
    _register(client, email="kyle@example.com", password="StrongPass123")
    tokens = _login(client, email="kyle@example.com").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "StrongPass123", "new_password": "EvenStronger456"},
        headers=headers,
    )

    # The refresh token issued before the password change is now revoked.
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401


def test_change_password_requires_auth(client):
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "a", "new_password": "EvenStronger456"},
    )
    assert resp.status_code == 401


def test_change_password_rejects_short_new_password(client):
    _register(client, email="laura@example.com", password="StrongPass123")
    tokens = _login(client, email="laura@example.com").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "StrongPass123", "new_password": "short"},
        headers=headers,
    )
    assert resp.status_code == 422
