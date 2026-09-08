from datetime import date

from app.core.config import settings
from tests.conftest import TestingSessionLocal
from tests.test_curriculum import _auth_headers


def _set_date_of_birth(email: str, dob: date) -> None:
    from app.modules.users import repository as users_repo

    db = TestingSessionLocal()
    try:
        user = users_repo.get_user_by_email(db, email)
        user.date_of_birth = dob
        db.commit()
    finally:
        db.close()


def test_user_can_set_own_date_of_birth(client):
    headers = _auth_headers(client, "bday.self1@example.com", "STUDENT")
    resp = client.patch("/api/v1/users/me", headers=headers, json={"date_of_birth": "2010-05-17"})
    assert resp.status_code == 200
    assert resp.json()["data"]["date_of_birth"] == "2010-05-17"

    me = client.get("/api/v1/users/me", headers=headers).json()["data"]
    assert me["date_of_birth"] == "2010-05-17"


def test_send_birthday_emails_requires_cron_secret(client, monkeypatch):
    monkeypatch.setattr(settings, "CRON_SECRET", "test-cron-secret")

    no_header = client.post("/api/v1/internal/send-birthday-emails")
    assert no_header.status_code == 401

    wrong_secret = client.post(
        "/api/v1/internal/send-birthday-emails", headers={"X-Cron-Secret": "wrong"}
    )
    assert wrong_secret.status_code == 401


def test_send_birthday_emails_sends_once_to_users_born_today(client, monkeypatch):
    monkeypatch.setattr(settings, "CRON_SECRET", "test-cron-secret")
    headers = {"X-Cron-Secret": "test-cron-secret"}

    today = date.today()
    not_today = today.replace(day=1) if today.day != 1 else today.replace(day=2)

    _auth_headers(client, "bday.today@example.com", "STUDENT")
    _auth_headers(client, "bday.other@example.com", "STUDENT")
    _set_date_of_birth("bday.today@example.com", today.replace(year=2010))
    _set_date_of_birth("bday.other@example.com", not_today.replace(year=2010))

    resp = client.post("/api/v1/internal/send-birthday-emails", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["sent_count"] == 1

    # Running again the same day must not send a second email to the same user.
    resp2 = client.post("/api/v1/internal/send-birthday-emails", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["data"]["sent_count"] == 0
