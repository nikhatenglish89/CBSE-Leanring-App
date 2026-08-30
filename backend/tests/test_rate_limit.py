from tests.conftest import solve_captcha
from tests.test_auth import _login, _register


def test_login_rate_limited_by_ip_after_too_many_attempts(client):
    # Different target emails each time so only the per-IP counter (limit
    # 20 per 5 minutes) is what trips, not the per-email one (limit 8).
    for i in range(20):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": f"iplimit{i}@example.com", "password": "whatever", **solve_captcha(client)},
        )
        assert resp.status_code in (401, 400)  # no such account / bad captcha race, never blocked yet

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "iplimit-overflow@example.com", "password": "whatever", **solve_captcha(client)},
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def test_login_rate_limited_by_target_email_after_too_many_failed_attempts(client):
    _register(client, email="lockout.target@example.com", password="StrongPass123")

    for _ in range(8):
        resp = _login(client, email="lockout.target@example.com", password="wrong-password")
        assert resp.status_code == 401

    # 9th attempt against the SAME account is blocked even though it's a
    # brand-new CAPTCHA/IP-window slot — the per-email lockout is separate.
    blocked = _login(client, email="lockout.target@example.com", password="wrong-password")
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"

    # The correct password is blocked too while locked out — the lockout
    # protects the account regardless of whether this particular attempt
    # would have succeeded.
    still_blocked = _login(client, email="lockout.target@example.com", password="StrongPass123")
    assert still_blocked.status_code == 429


def test_successful_login_clears_the_failed_attempt_counter(client):
    _register(client, email="resets.counter@example.com", password="StrongPass123")

    for _ in range(5):
        resp = _login(client, email="resets.counter@example.com", password="wrong-password")
        assert resp.status_code == 401

    success = _login(client, email="resets.counter@example.com", password="StrongPass123")
    assert success.status_code == 200

    # 5 failed + 1 successful = 6 hits against an 8-attempt lockout — if the
    # successful login hadn't cleared the counter, 3 more attempts here
    # would push the total to 9 and trip the lockout. It shouldn't, because
    # the counter was reset to zero on success.
    for _ in range(5):
        resp = _login(client, email="resets.counter@example.com", password="wrong-password")
        assert resp.status_code == 401


def test_register_rate_limited_by_ip_after_too_many_attempts(client):
    for i in range(8):
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"regfloor{i}@example.com",
                "password": "StrongPass123",
                "full_name": "Reg Floor",
                "role": "STUDENT",
                **solve_captcha(client),
            },
        )
        assert resp.status_code == 201

    blocked = client.post(
        "/api/v1/auth/register",
        json={
            "email": "regfloor-overflow@example.com",
            "password": "StrongPass123",
            "full_name": "Reg Floor",
            "role": "STUDENT",
            **solve_captcha(client),
        },
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def test_forgot_password_rate_limited_by_target_email(client):
    _register(client, email="forgot.target@example.com", password="StrongPass123")

    for _ in range(3):
        resp = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "forgot.target@example.com", **solve_captcha(client)},
        )
        assert resp.status_code == 200

    blocked = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "forgot.target@example.com", **solve_captcha(client)},
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"
