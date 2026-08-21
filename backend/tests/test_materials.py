from tests.test_curriculum import _auth_headers, _get_seeded_class_and_subject


def _create_published_lesson(client, headers):
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)
    course = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Materials Course"},
        headers=headers,
    ).json()["data"]
    section = client.post(
        f"/api/v1/courses/{course['id']}/sections", json={"title": "Section 1"}, headers=headers
    ).json()["data"]
    lesson = client.post(
        f"/api/v1/sections/{section['id']}/lessons", json={"title": "Lesson 1"}, headers=headers
    ).json()["data"]
    client.patch(f"/api/v1/courses/{course['id']}", json={"status": "PUBLISHED"}, headers=headers)
    return lesson


def test_teacher_can_upload_and_download_material(client):
    headers = _auth_headers(client, "teacher.materials@example.com", "TEACHER")
    lesson = _create_published_lesson(client, headers)

    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=headers,
        files={"file": ("notes.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")},
    )
    assert resp.status_code == 201
    material = resp.json()["data"]
    assert material["material_type"] == "PDF"
    assert material["file_name"] == "notes.pdf"

    dl = client.get(f"/api/v1/materials/{material['id']}/download", headers=headers)
    assert dl.status_code == 200
    assert dl.content == b"%PDF-1.4 fake pdf bytes"
    assert dl.headers["content-type"].startswith("application/pdf")


def test_teacher_can_upload_text_file(client):
    headers = _auth_headers(client, "teacher.textmaterial@example.com", "TEACHER")
    lesson = _create_published_lesson(client, headers)

    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=headers,
        files={"file": ("summary.txt", b"Chapter summary in plain text.", "text/plain")},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["material_type"] == "TEXT"

    dl = client.get(f"/api/v1/materials/{resp.json()['data']['id']}/download", headers=headers)
    assert dl.status_code == 200
    assert dl.content == b"Chapter summary in plain text."


def test_unsupported_file_type_rejected(client):
    headers = _auth_headers(client, "teacher.badtype@example.com", "TEACHER")
    lesson = _create_published_lesson(client, headers)

    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=headers,
        files={"file": ("virus.exe", b"MZ", "application/x-msdownload")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_oversized_file_rejected(client):
    headers = _auth_headers(client, "teacher.bigfile@example.com", "TEACHER")
    lesson = _create_published_lesson(client, headers)

    big = b"0" * (8 * 1024 * 1024 + 1)
    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=headers,
        files={"file": ("big.pdf", big, "application/pdf")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_other_teacher_cannot_upload_or_delete_materials(client):
    owner_headers = _auth_headers(client, "teacher.matowner@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    material = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=owner_headers,
        files={"file": ("notes.pdf", b"%PDF-1.4", "application/pdf")},
    ).json()["data"]

    other_headers = _auth_headers(client, "teacher.matintruder@example.com", "TEACHER")
    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=other_headers,
        files={"file": ("sneaky.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert resp.status_code == 403

    resp = client.delete(f"/api/v1/materials/{material['id']}", headers=other_headers)
    assert resp.status_code == 403


def test_student_can_view_but_not_upload_materials(client):
    owner_headers = _auth_headers(client, "teacher.matview@example.com", "TEACHER")
    lesson = _create_published_lesson(client, owner_headers)
    client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=owner_headers,
        files={"file": ("notes.pdf", b"%PDF-1.4", "application/pdf")},
    )

    student_headers = _auth_headers(client, "student.matview@example.com", "STUDENT")
    resp = client.get(f"/api/v1/lessons/{lesson['id']}/materials", headers=student_headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1

    resp = client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=student_headers,
        files={"file": ("sneaky.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert resp.status_code == 403


def test_teacher_can_set_and_replace_video(client):
    headers = _auth_headers(client, "teacher.video@example.com", "TEACHER")
    lesson = _create_published_lesson(client, headers)

    resp = client.put(
        f"/api/v1/lessons/{lesson['id']}/video",
        json={"url": "https://www.youtube.com/watch?v=abc123", "title": "Intro video"},
        headers=headers,
    )
    assert resp.status_code == 200
    video = resp.json()["data"]
    assert video["provider"] == "YOUTUBE"

    resp = client.put(
        f"/api/v1/lessons/{lesson['id']}/video",
        json={"url": "https://example.com/lecture.mp4", "title": "Replacement"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["provider"] == "URL"

    resp = client.get(f"/api/v1/lessons/{lesson['id']}/video", headers=headers)
    assert resp.json()["data"]["title"] == "Replacement"

    resp = client.delete(f"/api/v1/lessons/{lesson['id']}/video", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/api/v1/lessons/{lesson['id']}/video", headers=headers)
    assert resp.json()["data"] is None
