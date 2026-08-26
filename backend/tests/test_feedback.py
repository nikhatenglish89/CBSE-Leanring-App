from tests.test_admin_users import _admin_headers, _create_admin
from tests.test_curriculum import _auth_headers, _login


def test_submit_feedback_success(client):
    headers = _auth_headers(client, "fb.student1@example.com", "STUDENT")
    resp = client.post(
        "/api/v1/feedback", headers=headers, json={"category": "BUG", "message": "The video player is buggy."}
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["category"] == "BUG"
    assert data["status"] == "NEW"
    assert data["message"] == "The video player is buggy."


def test_submit_feedback_requires_auth(client):
    resp = client.post("/api/v1/feedback", json={"category": "GENERAL", "message": "Hello"})
    assert resp.status_code == 401


def test_submit_feedback_rejects_invalid_category(client):
    headers = _auth_headers(client, "fb.student2@example.com", "STUDENT")
    resp = client.post(
        "/api/v1/feedback", headers=headers, json={"category": "NOT_REAL", "message": "test"}
    )
    assert resp.status_code == 422


def test_submit_feedback_rejects_empty_message(client):
    headers = _auth_headers(client, "fb.student3@example.com", "STUDENT")
    resp = client.post("/api/v1/feedback", headers=headers, json={"category": "GENERAL", "message": ""})
    assert resp.status_code == 422


def test_list_my_feedback_shows_only_own_submissions(client):
    a_headers = _auth_headers(client, "fb.student4a@example.com", "STUDENT")
    b_headers = _auth_headers(client, "fb.student4b@example.com", "STUDENT")

    client.post("/api/v1/feedback", headers=a_headers, json={"category": "SUGGESTION", "message": "From A"})
    client.post("/api/v1/feedback", headers=b_headers, json={"category": "SUGGESTION", "message": "From B"})

    mine_a = client.get("/api/v1/feedback/mine", headers=a_headers).json()["data"]
    assert len(mine_a) == 1
    assert mine_a[0]["message"] == "From A"


def test_non_admin_cannot_list_all_feedback(client):
    headers = _auth_headers(client, "fb.student5@example.com", "STUDENT")
    resp = client.get("/api/v1/feedback", headers=headers)
    assert resp.status_code == 403


def test_admin_can_list_all_feedback_with_submitter_info(client):
    student_headers = _auth_headers(client, "fb.student6@example.com", "STUDENT")
    client.post(
        "/api/v1/feedback", headers=student_headers, json={"category": "BUG", "message": "Something broke"}
    )

    admin_headers = _admin_headers(client, email="fb.admin6@example.com")
    resp = client.get("/api/v1/feedback", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(item["message"] == "Something broke" and item["user_email"] == "fb.student6@example.com" for item in data)


def test_admin_can_filter_feedback_by_status_and_category(client):
    student_headers = _auth_headers(client, "fb.student7@example.com", "STUDENT")
    client.post("/api/v1/feedback", headers=student_headers, json={"category": "BUG", "message": "Bug one"})
    client.post(
        "/api/v1/feedback", headers=student_headers, json={"category": "SUGGESTION", "message": "Idea one"}
    )

    admin_headers = _admin_headers(client, email="fb.admin7@example.com")
    bugs_only = client.get("/api/v1/feedback", headers=admin_headers, params={"category": "BUG"}).json()["data"]
    assert all(item["category"] == "BUG" for item in bugs_only)

    new_only = client.get("/api/v1/feedback", headers=admin_headers, params={"status_filter": "NEW"}).json()["data"]
    assert all(item["status"] == "NEW" for item in new_only)


def test_admin_can_update_feedback_status(client):
    student_headers = _auth_headers(client, "fb.student8@example.com", "STUDENT")
    created = client.post(
        "/api/v1/feedback", headers=student_headers, json={"category": "GENERAL", "message": "Nice app"}
    ).json()["data"]

    admin_headers = _admin_headers(client, email="fb.admin8@example.com")
    resp = client.patch(
        f"/api/v1/feedback/{created['id']}", headers=admin_headers, json={"status": "RESOLVED"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "RESOLVED"


def test_update_status_requires_permission(client):
    student_headers = _auth_headers(client, "fb.student9@example.com", "STUDENT")
    created = client.post(
        "/api/v1/feedback", headers=student_headers, json={"category": "GENERAL", "message": "test"}
    ).json()["data"]

    other_student_headers = _auth_headers(client, "fb.student9b@example.com", "STUDENT")
    resp = client.patch(
        f"/api/v1/feedback/{created['id']}", headers=other_student_headers, json={"status": "RESOLVED"}
    )
    assert resp.status_code == 403


def test_update_nonexistent_feedback_404(client):
    admin_headers = _admin_headers(client, email="fb.admin10@example.com")
    resp = client.patch(
        "/api/v1/feedback/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
        json={"status": "REVIEWED"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "FEEDBACK_NOT_FOUND"


def test_support_agent_can_manage_feedback(client):
    _create_admin(email="fb.support11@example.com", password="SupportPass123", role_name="SUPPORT_AGENT")
    tokens = _login(client, email="fb.support11@example.com", password="SupportPass123").json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.get("/api/v1/feedback", headers=headers)
    assert resp.status_code == 200
