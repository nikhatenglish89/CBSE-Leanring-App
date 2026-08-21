import uuid

from tests.conftest import TestingSessionLocal
from tests.test_curriculum import _auth_headers, _get_seeded_class_and_subject


def test_practice_sets_are_seeded_and_browsable(client):
    headers = _auth_headers(client, "student.practice.browse@example.com", "STUDENT")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)

    resp = client.get(
        "/api/v1/practice-sets", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    )
    assert resp.status_code == 200
    sets = resp.json()["data"]
    assert len(sets) == 1
    assert sets[0]["question_count"] == 20
    assert sets[0]["class_id"] == class_id
    assert sets[0]["subject_id"] == subject_id


def test_practice_sets_require_auth(client):
    resp = client.get("/api/v1/practice-sets")
    assert resp.status_code == 401


def test_practice_set_detail_withholds_correct_answer(client):
    headers = _auth_headers(client, "student.practice.detail@example.com", "STUDENT")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    practice_set_id = client.get(
        "/api/v1/practice-sets", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    ).json()["data"][0]["id"]

    resp = client.get(f"/api/v1/practice-sets/{practice_set_id}", headers=headers)
    assert resp.status_code == 200
    detail = resp.json()["data"]
    assert len(detail["questions"]) == 20
    for question in detail["questions"]:
        assert len(question["options"]) == 4
        assert "correct_index" not in question


def test_practice_set_not_found(client):
    headers = _auth_headers(client, "student.practice.404@example.com", "STUDENT")
    resp = client.get(
        "/api/v1/practice-sets/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert resp.status_code == 404


def test_submit_practice_set_scores_all_correct(client):
    headers = _auth_headers(client, "student.practice.submit@example.com", "STUDENT")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    practice_set_id = client.get(
        "/api/v1/practice-sets", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    ).json()["data"][0]["id"]

    db = TestingSessionLocal()
    try:
        from app.modules.practice import repository as practice_repo

        questions = practice_repo.list_questions(db, uuid.UUID(practice_set_id))
        answers = [{"question_id": str(q.id), "selected_index": q.correct_index} for q in questions]
    finally:
        db.close()

    resp = client.post(
        f"/api/v1/practice-sets/{practice_set_id}/submit", json={"answers": answers}, headers=headers
    )
    assert resp.status_code == 200
    result = resp.json()["data"]
    assert result["score"] == 20
    assert result["total"] == 20
    assert all(r["is_correct"] for r in result["results"])


def test_submit_practice_set_scores_wrong_and_missing_answers(client):
    headers = _auth_headers(client, "student.practice.wrong@example.com", "STUDENT")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    practice_set_id = client.get(
        "/api/v1/practice-sets", params={"class_id": class_id, "subject_id": subject_id}, headers=headers
    ).json()["data"][0]["id"]

    db = TestingSessionLocal()
    try:
        from app.modules.practice import repository as practice_repo

        questions = practice_repo.list_questions(db, uuid.UUID(practice_set_id))
        # Answer only the first question, and deliberately wrong.
        first = questions[0]
        wrong_index = (first.correct_index + 1) % 4
        answers = [{"question_id": str(first.id), "selected_index": wrong_index}]
    finally:
        db.close()

    resp = client.post(
        f"/api/v1/practice-sets/{practice_set_id}/submit", json={"answers": answers}, headers=headers
    )
    assert resp.status_code == 200
    result = resp.json()["data"]
    assert result["score"] == 0
    assert result["total"] == 20
    first_result = next(r for r in result["results"] if r["question_id"] == str(first.id))
    assert first_result["is_correct"] is False
    assert first_result["selected_index"] == wrong_index
    unanswered = [r for r in result["results"] if r["question_id"] != str(first.id)]
    assert all(r["selected_index"] is None and not r["is_correct"] for r in unanswered)


def test_every_class_subject_has_a_seeded_practice_set(client):
    headers = _auth_headers(client, "student.practice.coverage@example.com", "STUDENT")
    classes = client.get("/api/v1/classes", headers=headers, params={"page_size": 50}).json()["data"]
    for klass in classes:
        subjects = client.get(
            "/api/v1/subjects", headers=headers, params={"class_id": klass["id"], "page_size": 50}
        ).json()["data"]
        for subject in subjects:
            resp = client.get(
                "/api/v1/practice-sets",
                params={"class_id": klass["id"], "subject_id": subject["id"]},
                headers=headers,
            )
            sets = resp.json()["data"]
            assert len(sets) == 1, f"missing practice set for {klass['name']} / {subject['name']}"
            assert sets[0]["question_count"] == 20
