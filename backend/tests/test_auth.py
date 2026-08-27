from tests.conftest import solve_captcha


def _register(client, email="alice@example.com", password="StrongPass123", role="STUDENT"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Alice Example",
            "role": role,
            **solve_captcha(client),
        },
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


def test_forgot_password_existing_and_unknown_email_return_identical_response(client):
    _register(client, email="mallory@example.com", password="StrongPass123")

    known = client.post(
        "/api/v1/auth/forgot-password", json={"email": "mallory@example.com", **solve_captcha(client)}
    )
    unknown = client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody-here@example.com", **solve_captcha(client)}
    )

    # Deliberately indistinguishable — the endpoint must never reveal
    # whether an email has an account.
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json() == {"success": True, "data": {"sent": True}}


def test_captcha_endpoint_returns_token_and_svg(client):
    resp = client.get("/api/v1/auth/captcha")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["token"]
    assert data["svg"].startswith("<svg")


def test_register_rejects_wrong_captcha_answer(client):
    challenge = client.get("/api/v1/auth/captcha").json()["data"]
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong.captcha@example.com",
            "password": "StrongPass123",
            "full_name": "Wrong Captcha",
            "role": "STUDENT",
            "captcha_token": challenge["token"],
            "captcha_answer": "definitely-wrong",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CAPTCHA_INVALID"


def test_register_rejects_garbage_captcha_token(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "garbage.captcha@example.com",
            "password": "StrongPass123",
            "full_name": "Garbage Captcha",
            "role": "STUDENT",
            "captcha_token": "not-a-real-token",
            "captcha_answer": "whatever",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CAPTCHA_INVALID"


def test_captcha_answer_is_case_insensitive(client):
    challenge = client.get("/api/v1/auth/captcha").json()["data"]
    from app.core.security import decode_token

    code = decode_token(challenge["token"], expected_type="captcha")["sub"]
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "case.captcha@example.com",
            "password": "StrongPass123",
            "full_name": "Case Captcha",
            "role": "STUDENT",
            "captcha_token": challenge["token"],
            "captcha_answer": code.lower(),
        },
    )
    assert resp.status_code == 201


def test_forgot_password_rejects_wrong_captcha_answer(client):
    _register(client, email="captcha.forgot@example.com", password="StrongPass123")
    challenge = client.get("/api/v1/auth/captcha").json()["data"]
    resp = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "captcha.forgot@example.com",
            "captcha_token": challenge["token"],
            "captcha_answer": "wrong",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CAPTCHA_INVALID"


def test_reset_password_with_valid_token_changes_password_and_revokes_sessions(client):
    from app.core.security import create_password_reset_token

    register_resp = _register(client, email="nathan@example.com", password="StrongPass123")
    user_id = register_resp.json()["data"]["id"]
    old_tokens = _login(client, email="nathan@example.com").json()["data"]

    reset_token = create_password_reset_token(user_id)
    resp = client.post(
        "/api/v1/auth/reset-password", json={"token": reset_token, "new_password": "BrandNewPass456"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["reset"] is True

    # Old password no longer works, new one does.
    assert _login(client, email="nathan@example.com", password="StrongPass123").status_code == 401
    new_login = _login(client, email="nathan@example.com", password="BrandNewPass456")
    assert new_login.status_code == 200

    # Any refresh token issued before the reset is revoked.
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_tokens["refresh_token"]})
    assert resp.status_code == 401


def test_reset_password_with_invalid_token(client):
    resp = client.post(
        "/api/v1/auth/reset-password", json={"token": "not-a-real-token", "new_password": "WhateverPass123"}
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_reset_password_rejects_wrong_token_type(client):
    from app.core.security import create_email_verification_token

    register_resp = _register(client, email="oscar@example.com", password="StrongPass123")
    user_id = register_resp.json()["data"]["id"]

    # An email-verification token must not double as a password-reset token.
    wrong_type_token = create_email_verification_token(user_id)
    resp = client.post(
        "/api/v1/auth/reset-password", json={"token": wrong_type_token, "new_password": "WhateverPass123"}
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_reset_password_rejects_short_new_password(client):
    from app.core.security import create_password_reset_token

    register_resp = _register(client, email="peggy@example.com", password="StrongPass123")
    user_id = register_resp.json()["data"]["id"]
    reset_token = create_password_reset_token(user_id)

    resp = client.post("/api/v1/auth/reset-password", json={"token": reset_token, "new_password": "short"})
    assert resp.status_code == 422
