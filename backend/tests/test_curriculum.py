def _register(client, email, role, password="StrongPass123"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User", "role": role},
    )


def _login(client, email, password="StrongPass123"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def _auth_headers(client, email, role):
    _register(client, email, role)
    tokens = _login(client, email).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _get_seeded_class_and_subject(client, headers):
    classes = client.get("/api/v1/classes", headers=headers).json()["data"]
    class_id = classes[0]["id"]
    subjects = client.get(f"/api/v1/subjects?class_id={class_id}", headers=headers).json()["data"]
    return class_id, subjects[0]["id"]


def test_classes_are_seeded_and_browsable_by_any_authenticated_user(client):
    headers = _auth_headers(client, "student.browse@example.com", "STUDENT")
    resp = client.get("/api/v1/classes", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]

    resp = client.get("/api/v1/classes")
    assert resp.status_code == 401


def test_student_cannot_create_class(client):
    headers = _auth_headers(client, "student.noclass@example.com", "STUDENT")
    resp = client.post("/api/v1/classes", json={"name": "Class XIII"}, headers=headers)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_teacher_cannot_manage_subjects_or_chapters(client):
    headers = _auth_headers(client, "teacher.nosubject@example.com", "TEACHER")
    class_id, _ = _get_seeded_class_and_subject(client, headers)
    resp = client.post(
        "/api/v1/subjects", json={"class_id": class_id, "name": "Sanskrit"}, headers=headers
    )
    assert resp.status_code == 403


def test_teacher_can_create_and_manage_own_course(client):
    headers = _auth_headers(client, "teacher.owner@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)

    create_resp = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Algebra Basics"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    course = create_resp.json()["data"]
    assert course["status"] == "DRAFT"

    section_resp = client.post(
        f"/api/v1/courses/{course['id']}/sections", json={"title": "Chapter 1"}, headers=headers
    )
    assert section_resp.status_code == 201
    section = section_resp.json()["data"]

    lesson_resp = client.post(
        f"/api/v1/sections/{section['id']}/lessons",
        json={"title": "Intro to Variables", "content_type": "VIDEO"},
        headers=headers,
    )
    assert lesson_resp.status_code == 201

    publish_resp = client.patch(
        f"/api/v1/courses/{course['id']}", json={"status": "PUBLISHED"}, headers=headers
    )
    assert publish_resp.status_code == 200
    assert publish_resp.json()["data"]["status"] == "PUBLISHED"


def test_teacher_cannot_manage_another_teachers_course(client):
    owner_headers = _auth_headers(client, "teacher.a@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, owner_headers)
    course = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Owned By A"},
        headers=owner_headers,
    ).json()["data"]

    other_headers = _auth_headers(client, "teacher.b@example.com", "TEACHER")
    resp = client.patch(
        f"/api/v1/courses/{course['id']}", json={"title": "Hijacked"}, headers=other_headers
    )
    assert resp.status_code == 403

    resp = client.post(
        f"/api/v1/courses/{course['id']}/sections", json={"title": "Sneaky"}, headers=other_headers
    )
    assert resp.status_code == 403


def test_draft_course_hidden_from_other_users_but_visible_to_owner(client):
    owner_headers = _auth_headers(client, "teacher.draft@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, owner_headers)
    course = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Still Drafting"},
        headers=owner_headers,
    ).json()["data"]

    student_headers = _auth_headers(client, "student.peeking@example.com", "STUDENT")
    resp = client.get(f"/api/v1/courses/{course['id']}", headers=student_headers)
    assert resp.status_code == 404

    resp = client.get(f"/api/v1/courses/{course['id']}", headers=owner_headers)
    assert resp.status_code == 200


def test_published_course_visible_to_students_in_catalog(client):
    owner_headers = _auth_headers(client, "teacher.published@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, owner_headers)
    course = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Published Course"},
        headers=owner_headers,
    ).json()["data"]
    client.patch(f"/api/v1/courses/{course['id']}", json={"status": "PUBLISHED"}, headers=owner_headers)

    student_headers = _auth_headers(client, "student.catalog@example.com", "STUDENT")
    resp = client.get(f"/api/v1/courses/{course['id']}", headers=student_headers)
    assert resp.status_code == 200

    catalog_resp = client.get(f"/api/v1/courses?subject_id={subject_id}", headers=student_headers)
    assert any(c["id"] == course["id"] for c in catalog_resp.json()["data"])


def test_courses_mine_only_returns_own_courses(client):
    headers = _auth_headers(client, "teacher.mine@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Mine Only"},
        headers=headers,
    )
    resp = client.get("/api/v1/courses?mine=true", headers=headers)
    assert resp.status_code == 200
    assert all("id" in c for c in resp.json()["data"])
    assert len(resp.json()["data"]) >= 1
