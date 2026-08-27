from tests.test_curriculum import _auth_headers, _verify_teacher_for_headers


def _me(client, headers):
    return client.get("/api/v1/users/me", headers=headers).json()["data"]


def _verified_teacher(client, email):
    headers = _auth_headers(client, email, "TEACHER")
    _verify_teacher_for_headers(client, headers)
    return headers


def test_verified_teacher_can_create_group(client):
    headers = _verified_teacher(client, "grp.teacher1@example.com")
    resp = client.post("/api/v1/groups", headers=headers, json={"name": "Physics Toppers", "description": "Extra practice"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Physics Toppers"
    assert data["member_count"] == 0
    assert data["task_count"] == 0


def test_unverified_teacher_cannot_create_group(client):
    headers = _auth_headers(client, "grp.teacher2@example.com", "TEACHER")
    resp = client.post("/api/v1/groups", headers=headers, json={"name": "Chess Club"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "TEACHER_NOT_VERIFIED"


def test_student_cannot_create_group(client):
    headers = _auth_headers(client, "grp.student1@example.com", "STUDENT")
    resp = client.post("/api/v1/groups", headers=headers, json={"name": "Not allowed"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_teacher_adds_students_and_assigns_task(client):
    teacher_headers = _verified_teacher(client, "grp.teacher3@example.com")
    student_headers = _auth_headers(client, "grp.student3@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    group = client.post(
        "/api/v1/groups", headers=teacher_headers, json={"name": "Math Circle"}
    ).json()["data"]
    group_id = group["id"]

    add = client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": student_id})
    assert add.status_code == 201

    task = client.post(
        f"/api/v1/groups/{group_id}/tasks",
        headers=teacher_headers,
        json={"title": "Solve Chapter 4 worksheet", "description": "Q1-Q10", "due_date": "2026-09-01T00:00:00Z"},
    )
    assert task.status_code == 201
    assert task.json()["data"]["title"] == "Solve Chapter 4 worksheet"

    detail = client.get(f"/api/v1/groups/{group_id}", headers=teacher_headers).json()["data"]
    assert detail["members"][0]["id"] == student_id
    assert len(detail["tasks"]) == 1

    mine = client.get("/api/v1/groups/mine", headers=teacher_headers).json()["data"]
    assert mine[0]["member_count"] == 1
    assert mine[0]["task_count"] == 1


def test_member_student_sees_group_and_tasks_in_mine(client):
    teacher_headers = _verified_teacher(client, "grp.teacher4@example.com")
    student_headers = _auth_headers(client, "grp.student4@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    group_id = client.post("/api/v1/groups", headers=teacher_headers, json={"name": "Debate Team"}).json()["data"]["id"]
    client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": student_id})
    client.post(f"/api/v1/groups/{group_id}/tasks", headers=teacher_headers, json={"title": "Prepare opening statement"})

    mine = client.get("/api/v1/groups/mine", headers=student_headers).json()["data"]
    assert len(mine) == 1
    assert mine[0]["id"] == group_id

    detail = client.get(f"/api/v1/groups/{group_id}", headers=student_headers).json()["data"]
    assert detail["tasks"][0]["title"] == "Prepare opening statement"


def test_outsider_student_cannot_view_group(client):
    teacher_headers = _verified_teacher(client, "grp.teacher5@example.com")
    outsider_headers = _auth_headers(client, "grp.outsider5@example.com", "STUDENT")

    group_id = client.post("/api/v1/groups", headers=teacher_headers, json={"name": "Robotics"}).json()["data"]["id"]

    resp = client.get(f"/api/v1/groups/{group_id}", headers=outsider_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "GROUP_NOT_FOUND"


def test_other_teacher_cannot_add_members_or_tasks_to_group_they_do_not_own(client):
    owner_headers = _verified_teacher(client, "grp.teacher6a@example.com")
    other_headers = _verified_teacher(client, "grp.teacher6b@example.com")
    student_headers = _auth_headers(client, "grp.student6@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    group_id = client.post("/api/v1/groups", headers=owner_headers, json={"name": "Owned Group"}).json()["data"]["id"]

    add = client.post(f"/api/v1/groups/{group_id}/members", headers=other_headers, json={"student_id": student_id})
    assert add.status_code == 404
    assert add.json()["error"]["code"] == "GROUP_NOT_FOUND"

    task = client.post(f"/api/v1/groups/{group_id}/tasks", headers=other_headers, json={"title": "Sneaky task"})
    assert task.status_code == 404


def test_adding_same_student_twice_conflicts(client):
    teacher_headers = _verified_teacher(client, "grp.teacher7@example.com")
    student_headers = _auth_headers(client, "grp.student7@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    group_id = client.post("/api/v1/groups", headers=teacher_headers, json={"name": "Science Club"}).json()["data"]["id"]
    client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": student_id})
    dup = client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": student_id})
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "ALREADY_MEMBER"


def test_teacher_can_remove_member(client):
    teacher_headers = _verified_teacher(client, "grp.teacher8@example.com")
    student_headers = _auth_headers(client, "grp.student8@example.com", "STUDENT")
    student_id = _me(client, student_headers)["id"]

    group_id = client.post("/api/v1/groups", headers=teacher_headers, json={"name": "Art Club"}).json()["data"]["id"]
    client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": student_id})

    remove = client.delete(f"/api/v1/groups/{group_id}/members/{student_id}", headers=teacher_headers)
    assert remove.status_code == 200

    detail = client.get(f"/api/v1/groups/{group_id}", headers=teacher_headers).json()["data"]
    assert detail["members"] == []

    removed_again = client.delete(f"/api/v1/groups/{group_id}/members/{student_id}", headers=teacher_headers)
    assert removed_again.status_code == 404
    assert removed_again.json()["error"]["code"] == "MEMBER_NOT_FOUND"


def test_cannot_add_a_non_student_as_member(client):
    teacher_headers = _verified_teacher(client, "grp.teacher9@example.com")
    other_teacher_headers = _auth_headers(client, "grp.teacher9b@example.com", "TEACHER")
    other_teacher_id = _me(client, other_teacher_headers)["id"]

    group_id = client.post("/api/v1/groups", headers=teacher_headers, json={"name": "Bad Add"}).json()["data"]["id"]
    resp = client.post(f"/api/v1/groups/{group_id}/members", headers=teacher_headers, json={"student_id": other_teacher_id})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"
