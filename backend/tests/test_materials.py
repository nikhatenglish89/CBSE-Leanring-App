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


def test_browse_materials_and_videos_only_shows_published_courses(client):
    headers = _auth_headers(client, "teacher.browse@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, headers)

    published = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Browsable Course"},
        headers=headers,
    ).json()["data"]
    pub_section = client.post(
        f"/api/v1/courses/{published['id']}/sections", json={"title": "Section 1"}, headers=headers
    ).json()["data"]
    pub_lesson = client.post(
        f"/api/v1/sections/{pub_section['id']}/lessons", json={"title": "Browsable Lesson"}, headers=headers
    ).json()["data"]
    client.patch(f"/api/v1/courses/{published['id']}", json={"status": "PUBLISHED"}, headers=headers)
    client.post(
        f"/api/v1/lessons/{pub_lesson['id']}/materials",
        headers=headers,
        files={"file": ("public.pdf", b"%PDF-1.4 public", "application/pdf")},
    )
    client.put(
        f"/api/v1/lessons/{pub_lesson['id']}/video",
        headers=headers,
        json={"url": "https://www.youtube.com/watch?v=public123", "title": "Public video"},
    )

    draft = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Draft Course"},
        headers=headers,
    ).json()["data"]
    draft_section = client.post(
        f"/api/v1/courses/{draft['id']}/sections", json={"title": "Section 1"}, headers=headers
    ).json()["data"]
    draft_lesson = client.post(
        f"/api/v1/sections/{draft_section['id']}/lessons", json={"title": "Draft Lesson"}, headers=headers
    ).json()["data"]
    client.post(
        f"/api/v1/lessons/{draft_lesson['id']}/materials",
        headers=headers,
        files={"file": ("draft.pdf", b"%PDF-1.4 draft", "application/pdf")},
    )
    client.put(
        f"/api/v1/lessons/{draft_lesson['id']}/video",
        headers=headers,
        json={"url": "https://www.youtube.com/watch?v=draft123", "title": "Draft video"},
    )

    student_headers = _auth_headers(client, "student.browse@example.com", "STUDENT")

    mat_resp = client.get("/api/v1/materials", headers=student_headers)
    assert mat_resp.status_code == 200
    mat_names = [m["file_name"] for m in mat_resp.json()["data"]]
    assert "public.pdf" in mat_names
    assert "draft.pdf" not in mat_names
    published_entry = next(m for m in mat_resp.json()["data"] if m["file_name"] == "public.pdf")
    assert published_entry["course_title"] == "Browsable Course"
    assert published_entry["lesson_title"] == "Browsable Lesson"

    vid_resp = client.get("/api/v1/videos", headers=student_headers)
    assert vid_resp.status_code == 200
    vid_titles = [v["title"] for v in vid_resp.json()["data"]]
    assert "Public video" in vid_titles
    assert "Draft video" not in vid_titles

    unauth_resp = client.get("/api/v1/materials")
    assert unauth_resp.status_code == 401


def test_browse_shows_drafts_to_other_teachers_but_not_students(client):
    owner_headers = _auth_headers(client, "teacher.draftowner@example.com", "TEACHER")
    class_id, subject_id = _get_seeded_class_and_subject(client, owner_headers)

    draft = client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Colleague's Draft"},
        headers=owner_headers,
    ).json()["data"]
    section = client.post(
        f"/api/v1/courses/{draft['id']}/sections", json={"title": "Section 1"}, headers=owner_headers
    ).json()["data"]
    lesson = client.post(
        f"/api/v1/sections/{section['id']}/lessons", json={"title": "Draft Lesson"}, headers=owner_headers
    ).json()["data"]
    client.post(
        f"/api/v1/lessons/{lesson['id']}/materials",
        headers=owner_headers,
        files={"file": ("colleague-notes.pdf", b"%PDF-1.4 colleague", "application/pdf")},
    )

    other_teacher_headers = _auth_headers(client, "teacher.colleague@example.com", "TEACHER")
    resp = client.get("/api/v1/materials", headers=other_teacher_headers)
    assert resp.status_code == 200
    names = [m["file_name"] for m in resp.json()["data"]]
    assert "colleague-notes.pdf" in names

    student_headers = _auth_headers(client, "student.nodrafts@example.com", "STUDENT")
    resp = client.get("/api/v1/materials", headers=student_headers)
    names = [m["file_name"] for m in resp.json()["data"]]
    assert "colleague-notes.pdf" not in names
