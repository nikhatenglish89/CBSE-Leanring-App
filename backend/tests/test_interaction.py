from datetime import datetime, timedelta, timezone

from tests.test_curriculum import _auth_headers, _get_seeded_class_and_subject
from tests.test_materials import _create_published_lesson


def test_student_can_ask_and_teacher_can_answer(client):
    owner_headers = _auth_headers(client, "teacher.qa.owner@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)

    student_headers = _auth_headers(client, "student.qa.asker@example.com", "STUDENT")
    ask_resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Why is the sky blue?"},
        headers=student_headers,
    )
    assert ask_resp.status_code == 201
    question = ask_resp.json()["data"]
    assert question["body"] == "Why is the sky blue?"
    assert question["answer"] is None

    # A different teacher (not the course owner) can answer — same
    # open-collaboration model as study materials.
    other_teacher_headers = _auth_headers(client, "teacher.qa.other@example.com", "TEACHER")
    answer_resp = client.post(
        f"/api/v1/questions/{question['id']}/answer",
        json={"body": "Rayleigh scattering."},
        headers=other_teacher_headers,
    )
    assert answer_resp.status_code == 200
    assert answer_resp.json()["data"]["body"] == "Rayleigh scattering."

    listing = client.get(f"/api/v1/lessons/{lesson['id']}/questions", headers=student_headers)
    assert listing.status_code == 200
    listed = listing.json()["data"]
    assert len(listed) == 1
    assert listed[0]["answer"]["body"] == "Rayleigh scattering."
    assert listed[0]["answer"]["teacher_name"]


def test_answering_twice_replaces_the_answer(client):
    owner_headers = _auth_headers(client, "teacher.qa.replace@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    student_headers = _auth_headers(client, "student.qa.replace@example.com", "STUDENT")
    question = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Q1"}, headers=student_headers
    ).json()["data"]

    client.post(f"/api/v1/questions/{question['id']}/answer", json={"body": "first answer"}, headers=owner_headers)
    resp = client.post(
        f"/api/v1/questions/{question['id']}/answer", json={"body": "better answer"}, headers=owner_headers
    )
    assert resp.status_code == 200

    listing = client.get(f"/api/v1/lessons/{lesson['id']}/questions", headers=student_headers).json()["data"]
    assert len(listing) == 1
    assert listing[0]["answer"]["body"] == "better answer"


def test_teacher_cannot_ask_question(client):
    owner_headers = _auth_headers(client, "teacher.qa.noask@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Can I ask?"}, headers=owner_headers
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_student_cannot_answer_question(client):
    owner_headers = _auth_headers(client, "teacher.qa.noanswer@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    student_headers = _auth_headers(client, "student.qa.noanswer@example.com", "STUDENT")
    question = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Q?"}, headers=student_headers
    ).json()["data"]

    resp = client.post(
        f"/api/v1/questions/{question['id']}/answer", json={"body": "trying to answer"}, headers=student_headers
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_parent_can_ask_question(client):
    owner_headers = _auth_headers(client, "teacher.qa.parent@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    parent_headers = _auth_headers(client, "parent.qa@example.com", "PARENT")
    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Parent question"}, headers=parent_headers
    )
    assert resp.status_code == 201


def test_cannot_ask_question_on_draft_lesson(client):
    headers = _auth_headers(client, "teacher.qa.draft@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    course = client.post(
        "/api/v1/courses", json={"class_id": class_id, "subject_id": subject_id, "title": "Draft QA"},
        headers=headers,
    ).json()["data"]
    section = client.post(
        f"/api/v1/courses/{course['id']}/sections", json={"title": "S1"}, headers=headers
    ).json()["data"]
    lesson = client.post(
        f"/api/v1/sections/{section['id']}/lessons", json={"title": "L1"}, headers=headers
    ).json()["data"]
    # course intentionally left DRAFT

    student_headers = _auth_headers(client, "student.qa.draft@example.com", "STUDENT")
    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "Sneaky question"}, headers=student_headers
    )
    assert resp.status_code == 404


def test_browse_questions_filters_by_answered_and_mine(client):
    owner_headers = _auth_headers(client, "teacher.qa.browse@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    student_headers = _auth_headers(client, "student.qa.browse@example.com", "STUDENT")

    q1 = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "unanswered one"}, headers=student_headers
    ).json()["data"]
    q2 = client.post(
        f"/api/v1/lessons/{lesson['id']}/questions", json={"body": "will be answered"}, headers=student_headers
    ).json()["data"]
    client.post(f"/api/v1/questions/{q2['id']}/answer", json={"body": "answered!"}, headers=owner_headers)

    unanswered = client.get(
        "/api/v1/questions", params={"answered": False, "mine": True}, headers=student_headers
    ).json()["data"]
    assert any(q["id"] == q1["id"] for q in unanswered)
    assert all(not q["answer"] for q in unanswered)

    answered = client.get(
        "/api/v1/questions", params={"answered": True, "mine": True}, headers=student_headers
    ).json()["data"]
    assert any(q["id"] == q2["id"] for q in answered)
    assert all(q["answer"] for q in answered)


def test_questions_require_auth(client):
    resp = client.get("/api/v1/questions")
    assert resp.status_code == 401


# --- Live classes ---------------------------------------------------------


def test_teacher_can_schedule_and_browse_live_class(client):
    headers = _auth_headers(client, "teacher.live.create@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    scheduled_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    resp = client.post(
        "/api/v1/live-classes",
        json={
            "class_id": class_id,
            "subject_id": subject_id,
            "title": "Doubt clearing session",
            "description": "Bring your questions",
            "scheduled_at": scheduled_at,
            "meeting_url": "https://meet.example.com/abc",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    created = resp.json()["data"]
    assert created["title"] == "Doubt clearing session"
    assert created["teacher_name"]
    assert created["class_name"]
    assert created["subject_name"]

    browse = client.get(
        "/api/v1/live-classes", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    )
    assert browse.status_code == 200
    assert any(lc["id"] == created["id"] for lc in browse.json()["data"])


def test_student_cannot_schedule_live_class(client):
    headers = _auth_headers(client, "student.live.noschedule@example.com", "STUDENT")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    resp = client.post(
        "/api/v1/live-classes",
        json={
            "class_id": class_id,
            "subject_id": subject_id,
            "title": "Nope",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "meeting_url": "https://meet.example.com/nope",
        },
        headers=headers,
    )
    assert resp.status_code == 403


def test_teacher_cannot_manage_another_teachers_live_class(client):
    owner_headers = _auth_headers(client, "teacher.live.owner@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, owner_headers)
    created = client.post(
        "/api/v1/live-classes",
        json={
            "class_id": class_id,
            "subject_id": subject_id,
            "title": "Owned session",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "meeting_url": "https://meet.example.com/owned",
        },
        headers=owner_headers,
    ).json()["data"]

    other_headers = _auth_headers(client, "teacher.live.other@example.com", "TEACHER")
    patch_resp = client.patch(
        f"/api/v1/live-classes/{created['id']}", json={"title": "Hijacked"}, headers=other_headers
    )
    assert patch_resp.status_code == 403

    delete_resp = client.delete(f"/api/v1/live-classes/{created['id']}", headers=other_headers)
    assert delete_resp.status_code == 403


def test_teacher_can_update_and_delete_own_live_class(client):
    headers = _auth_headers(client, "teacher.live.owncrud@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    created = client.post(
        "/api/v1/live-classes",
        json={
            "class_id": class_id,
            "subject_id": subject_id,
            "title": "Original title",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "meeting_url": "https://meet.example.com/mine",
        },
        headers=headers,
    ).json()["data"]

    patch_resp = client.patch(
        f"/api/v1/live-classes/{created['id']}", json={"title": "Updated title"}, headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["title"] == "Updated title"

    delete_resp = client.delete(f"/api/v1/live-classes/{created['id']}", headers=headers)
    assert delete_resp.status_code == 204

    browse = client.get(
        "/api/v1/live-classes", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    ).json()["data"]
    assert all(lc["id"] != created["id"] for lc in browse)


def test_live_classes_require_auth(client):
    resp = client.get("/api/v1/live-classes")
    assert resp.status_code == 401
