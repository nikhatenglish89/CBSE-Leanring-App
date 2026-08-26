import uuid

from tests.conftest import TestingSessionLocal
from tests.test_admin_users import _admin_headers
from tests.test_curriculum import _auth_headers, _verify_teacher_for_headers


def _me(client, headers):
    return client.get("/api/v1/users/me", headers=headers).json()["data"]


def test_student_can_start_conversation_with_verified_teacher(client):
    teacher_headers = _auth_headers(client, "msg.teacher1@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]

    student_headers = _auth_headers(client, "msg.student1@example.com", "STUDENT")
    resp = client.post("/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["other_user"]["id"] == teacher_id
    assert data["other_user"]["role"] == "TEACHER"
    assert data["unread_count"] == 0


def test_student_cannot_start_conversation_with_unverified_teacher(client):
    teacher_headers = _auth_headers(client, "msg.teacher2@example.com", "TEACHER")
    teacher_id = _me(client, teacher_headers)["id"]

    student_headers = _auth_headers(client, "msg.student2@example.com", "STUDENT")
    resp = client.post("/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "TEACHER_NOT_VERIFIED"


def test_starting_conversation_twice_reuses_same_conversation(client):
    teacher_headers = _auth_headers(client, "msg.teacher3@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]
    student_headers = _auth_headers(client, "msg.student3@example.com", "STUDENT")

    first = client.post("/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id})
    second = client.post("/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id})
    assert first.json()["data"]["id"] == second.json()["data"]["id"]


def test_teacher_can_start_conversation_with_student(client):
    teacher_headers = _auth_headers(client, "msg.teacher4@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    student_headers = _auth_headers(client, "msg.student4@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    resp = client.post("/api/v1/conversations", headers=teacher_headers, json={"other_user_id": student_id})
    assert resp.status_code == 201
    assert resp.json()["data"]["other_user"]["role"] == "STUDENT"


def test_cannot_start_conversation_between_two_students(client):
    a_headers = _auth_headers(client, "msg.student5a@example.com", "STUDENT")
    b_headers = _auth_headers(client, "msg.student5b@example.com", "STUDENT")
    b_id = _me(client, b_headers)["id"]

    resp = client.post("/api/v1/conversations", headers=a_headers, json={"other_user_id": b_id})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARTICIPANTS"


def test_send_and_list_messages_with_unread_tracking(client):
    teacher_headers = _auth_headers(client, "msg.teacher6@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]
    student_headers = _auth_headers(client, "msg.student6@example.com", "STUDENT")

    conv = client.post(
        "/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id}
    ).json()["data"]
    conv_id = conv["id"]

    send = client.post(
        f"/api/v1/conversations/{conv_id}/messages", headers=student_headers, json={"body": "Hello teacher!"}
    )
    assert send.status_code == 201
    assert send.json()["data"]["body"] == "Hello teacher!"

    # Teacher's conversation list shows it unread.
    teacher_list = client.get("/api/v1/conversations", headers=teacher_headers).json()["data"]
    assert teacher_list[0]["unread_count"] == 1
    assert teacher_list[0]["last_message_preview"] == "Hello teacher!"

    # Opening the thread marks it read.
    messages = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=teacher_headers).json()["data"]
    assert len(messages) == 1
    assert messages[0]["sender_name"]

    teacher_list_after = client.get("/api/v1/conversations", headers=teacher_headers).json()["data"]
    assert teacher_list_after[0]["unread_count"] == 0

    # Teacher replies.
    reply = client.post(
        f"/api/v1/conversations/{conv_id}/messages", headers=teacher_headers, json={"body": "Hi! How can I help?"}
    )
    assert reply.status_code == 201

    thread = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=student_headers).json()["data"]
    assert len(thread) == 2


def test_non_participant_cannot_send_or_see_conversation(client):
    teacher_headers = _auth_headers(client, "msg.teacher7@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]
    student_headers = _auth_headers(client, "msg.student7@example.com", "STUDENT")
    conv_id = client.post(
        "/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id}
    ).json()["data"]["id"]

    outsider_headers = _auth_headers(client, "msg.outsider7@example.com", "STUDENT")
    resp = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=outsider_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CONVERSATION_NOT_FOUND"

    send_resp = client.post(
        f"/api/v1/conversations/{conv_id}/messages", headers=outsider_headers, json={"body": "sneaky"}
    )
    assert send_resp.status_code == 404


def test_messageable_users_only_shows_verified_teachers_to_students(client):
    verified_headers = _auth_headers(client, "msg.teacher8v@example.com", "TEACHER")
    _verify_teacher_for_headers(client, verified_headers)
    _auth_headers(client, "msg.teacher8u@example.com", "TEACHER")  # left unverified

    student_headers = _auth_headers(client, "msg.student8@example.com", "STUDENT")
    resp = client.get("/api/v1/conversations/messageable-users", headers=student_headers)
    assert resp.status_code == 200
    names = [u["full_name"] for u in resp.json()["data"]]
    # Both teachers register with the same default full_name ("Test User")
    # in this helper, so assert on presence via email isn't possible here —
    # instead assert the unverified teacher's account id is excluded.
    ids = {u["id"] for u in resp.json()["data"]}
    unverified_me = _me(client, _auth_headers(client, "msg.teacher8u@example.com", "TEACHER"))
    assert unverified_me["id"] not in ids
    assert len(names) >= 1


def test_admin_can_view_but_not_send_in_any_conversation(client):
    teacher_headers = _auth_headers(client, "msg.teacher9@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]
    student_headers = _auth_headers(client, "msg.student9@example.com", "STUDENT")
    conv_id = client.post(
        "/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id}
    ).json()["data"]["id"]
    client.post(f"/api/v1/conversations/{conv_id}/messages", headers=student_headers, json={"body": "hi"})

    admin_headers = _admin_headers(client, email="msg.admin9@example.com")
    view = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=admin_headers)
    assert view.status_code == 200
    assert len(view.json()["data"]) == 1

    send = client.post(f"/api/v1/conversations/{conv_id}/messages", headers=admin_headers, json={"body": "nope"})
    assert send.status_code == 403
    assert send.json()["error"]["code"] == "PERMISSION_DENIED"


def test_admin_moderation_listing(client):
    teacher_headers = _auth_headers(client, "msg.teacher10@example.com", "TEACHER")
    _verify_teacher_for_headers(client, teacher_headers)
    teacher_id = _me(client, teacher_headers)["id"]
    student_headers = _auth_headers(client, "msg.student10@example.com", "STUDENT")
    conv = client.post(
        "/api/v1/conversations", headers=student_headers, json={"other_user_id": teacher_id}
    ).json()["data"]
    client.post(f"/api/v1/conversations/{conv['id']}/messages", headers=student_headers, json={"body": "hey"})

    admin_headers = _admin_headers(client, email="msg.admin10@example.com")
    resp = client.get("/api/v1/conversations/moderation/all", headers=admin_headers)
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()["data"]]
    assert conv["id"] in ids


def test_moderation_listing_requires_permission(client):
    student_headers = _auth_headers(client, "msg.student11@example.com", "STUDENT")
    resp = client.get("/api/v1/conversations/moderation/all", headers=student_headers)
    assert resp.status_code == 403


def test_conversations_require_auth(client):
    assert client.get("/api/v1/conversations").status_code == 401
    assert client.post("/api/v1/conversations", json={"other_user_id": str(uuid.uuid4())}).status_code == 401


def test_start_conversation_with_nonexistent_user_404(client):
    student_headers = _auth_headers(client, "msg.student12@example.com", "STUDENT")
    resp = client.post(
        "/api/v1/conversations", headers=student_headers, json={"other_user_id": str(uuid.uuid4())}
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "USER_NOT_FOUND"
