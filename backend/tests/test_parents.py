import uuid

from tests.conftest import TestingSessionLocal
from tests.test_admin_users import _admin_headers
from tests.test_curriculum import _auth_headers, _get_seeded_class_and_subject


def _me(client, headers):
    return client.get("/api/v1/users/me", headers=headers).json()["data"]


def _link(client, admin_headers, student_id, parent_id):
    return client.post(
        f"/api/v1/users/{student_id}/link-parent",
        json={"parent_user_id": parent_id},
        headers=admin_headers,
    )


def test_parent_with_no_linked_children_sees_empty_list(client):
    parent_headers = _auth_headers(client, "parent.empty@example.com", "PARENT")
    resp = client.get("/api/v1/parents/children", headers=parent_headers)
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_non_parent_cannot_view_children(client):
    student_headers = _auth_headers(client, "student.notparent@example.com", "STUDENT")
    resp = client.get("/api/v1/parents/children", headers=student_headers)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_parent_sees_linked_childs_test_progress(client):
    admin_headers = _admin_headers(client, email="admin.parents1@example.com")
    parent_headers = _auth_headers(client, "parent.progress@example.com", "PARENT")
    student_headers = _auth_headers(client, "student.progress@example.com", "STUDENT")
    parent_id = _me(client, parent_headers)["id"]
    student_id = _me(client, student_headers)["id"]

    link = _link(client, admin_headers, student_id, parent_id)
    assert link.status_code == 200

    class_id, subject_id = _get_seeded_class_and_subject(client, student_headers)
    practice_set_id = client.get(
        "/api/v1/practice-sets",
        params={"class_id": class_id, "subject_id": subject_id},
        headers=student_headers,
    ).json()["data"][0]["id"]

    db = TestingSessionLocal()
    try:
        from app.modules.practice import repository as practice_repo

        questions = practice_repo.list_questions(db, uuid.UUID(practice_set_id))
        answers = [{"question_id": str(q.id), "selected_index": q.correct_index} for q in questions[:10]]
    finally:
        db.close()

    client.post(
        f"/api/v1/practice-sets/{practice_set_id}/submit", json={"answers": answers}, headers=student_headers
    )

    resp = client.get("/api/v1/parents/children", headers=parent_headers)
    assert resp.status_code == 200
    children = resp.json()["data"]
    assert len(children) == 1
    child = children[0]
    assert child["id"] == student_id
    assert child["full_name"] == "Test User"
    assert child["tests_taken"] == 1
    assert child["average_score_pct"] == 50.0
    assert child["last_activity_at"] is not None
    assert len(child["recent_attempts"]) == 1
    assert child["recent_attempts"][0]["score"] == 10
    assert child["recent_attempts"][0]["total"] == 20


def test_parent_does_not_see_unlinked_students(client):
    parent_headers = _auth_headers(client, "parent.unlinked@example.com", "PARENT")
    _auth_headers(client, "student.unlinked@example.com", "STUDENT")  # never linked

    resp = client.get("/api/v1/parents/children", headers=parent_headers)
    assert resp.json()["data"] == []


def test_unlinking_removes_child_from_parent_view(client):
    admin_headers = _admin_headers(client, email="admin.parents2@example.com")
    parent_headers = _auth_headers(client, "parent.unlink2@example.com", "PARENT")
    student_headers = _auth_headers(client, "student.unlink2@example.com", "STUDENT")
    parent_id = _me(client, parent_headers)["id"]
    student_id = _me(client, student_headers)["id"]

    _link(client, admin_headers, student_id, parent_id)
    assert len(client.get("/api/v1/parents/children", headers=parent_headers).json()["data"]) == 1

    unlink = client.post(f"/api/v1/users/{student_id}/unlink-parent", headers=admin_headers)
    assert unlink.status_code == 200
    assert client.get("/api/v1/parents/children", headers=parent_headers).json()["data"] == []
