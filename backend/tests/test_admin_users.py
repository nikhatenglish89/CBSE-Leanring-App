from app.core.security import hash_password
from app.modules.auth import repository as auth_repo
from app.modules.users import repository as users_repo
from tests.conftest import TestingSessionLocal, solve_captcha
from tests.test_curriculum import _auth_headers, _get_seeded_class_and_subject


def _create_admin(email="admin.users@example.com", password="AdminPass123", role_name="ADMIN"):
    db = TestingSessionLocal()
    try:
        role = auth_repo.get_role_by_name(db, role_name)
        users_repo.create_user(
            db,
            email=email,
            password_hash=hash_password(password),
            full_name="Admin User",
            phone=None,
            role_id=role.id,
        )
    finally:
        db.close()


def _admin_headers(client, email="admin.users@example.com", password="AdminPass123"):
    _create_admin(email, password, role_name="ADMIN")
    tokens = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password, **solve_captcha(client)}
    ).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _super_admin_headers(client, email="superadmin.users@example.com", password="SuperAdminPass123"):
    _create_admin(email, password, role_name="SUPER_ADMIN")
    tokens = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password, **solve_captcha(client)}
    ).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_admin_can_create_student_account(client):
    headers = _admin_headers(client, email="admin.create.student@example.com")
    resp = client.post(
        "/api/v1/users",
        json={"email": "new.student@example.com", "full_name": "New Student", "role": "STUDENT"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["email"] == "new.student@example.com"
    assert data["role"] == "STUDENT"
    assert data["must_reset_password"] is True
    assert len(data["temporary_password"]) >= 8


def test_admin_can_create_teacher_account(client):
    headers = _admin_headers(client, email="admin.create.teacher@example.com")
    resp = client.post(
        "/api/v1/users",
        json={"email": "new.teacher@example.com", "full_name": "New Teacher", "role": "TEACHER"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["role"] == "TEACHER"
    assert data["must_reset_password"] is True


def test_create_user_duplicate_email_conflicts(client):
    headers = _admin_headers(client, email="admin.create.dup@example.com")
    client.post(
        "/api/v1/users",
        json={"email": "dup.user@example.com", "full_name": "Dup", "role": "STUDENT"},
        headers=headers,
    )
    resp = client.post(
        "/api/v1/users",
        json={"email": "dup.user@example.com", "full_name": "Dup Again", "role": "STUDENT"},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_non_admin_cannot_create_user(client):
    headers = _auth_headers(client, "student.no.create@example.com", "STUDENT")
    resp = client.post(
        "/api/v1/users",
        json={"email": "sneaky@example.com", "full_name": "Sneaky", "role": "STUDENT"},
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_create_user_requires_auth(client):
    resp = client.post(
        "/api/v1/users", json={"email": "noauth@example.com", "full_name": "No Auth", "role": "STUDENT"}
    )
    assert resp.status_code == 401


def test_admin_created_account_must_reset_password_then_login_normally(client):
    headers = _admin_headers(client, email="admin.reset.flow@example.com")
    created = client.post(
        "/api/v1/users",
        json={"email": "resetflow.student@example.com", "full_name": "Reset Flow", "role": "STUDENT"},
        headers=headers,
    ).json()["data"]
    temp_password = created["temporary_password"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetflow.student@example.com", "password": temp_password, **solve_captcha(client)},
    )
    assert login.status_code == 200
    student_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    me = client.get("/api/v1/users/me", headers=student_headers).json()["data"]
    assert me["must_reset_password"] is True

    change = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": temp_password, "new_password": "BrandNewPass456"},
        headers=student_headers,
    )
    assert change.status_code == 200

    me_after = client.get("/api/v1/users/me", headers=student_headers).json()["data"]
    assert me_after["must_reset_password"] is False

    # old temp password no longer works, new one does
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetflow.student@example.com", "password": temp_password, **solve_captcha(client)},
    )
    assert old_login.status_code == 401
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "resetflow.student@example.com",
            "password": "BrandNewPass456",
            **solve_captcha(client),
        },
    )
    assert new_login.status_code == 200


def test_admin_can_list_and_filter_users_by_role(client):
    headers = _admin_headers(client, email="admin.list@example.com")
    _auth_headers(client, "listed.student@example.com", "STUDENT")
    _auth_headers(client, "listed.teacher@example.com", "TEACHER")

    students = client.get("/api/v1/users", params={"role": "STUDENT"}, headers=headers).json()["data"]
    assert any(u["email"] == "listed.student@example.com" for u in students)
    assert all(u["role"] == "STUDENT" for u in students)

    teachers = client.get("/api/v1/users", params={"role": "TEACHER"}, headers=headers).json()["data"]
    assert any(u["email"] == "listed.teacher@example.com" for u in teachers)
    assert all(u["role"] == "TEACHER" for u in teachers)


def test_admin_can_search_users(client):
    headers = _admin_headers(client, email="admin.search@example.com")
    _auth_headers(client, "findme.search@example.com", "STUDENT")

    resp = client.get("/api/v1/users", params={"search": "findme"}, headers=headers)
    assert resp.status_code == 200
    assert any(u["email"] == "findme.search@example.com" for u in resp.json()["data"])


def test_admin_can_view_student_detail(client):
    headers = _admin_headers(client, email="admin.detail.student@example.com")
    student_headers = _auth_headers(client, "detail.student@example.com", "STUDENT")
    student_id = client.get("/api/v1/users/me", headers=student_headers).json()["data"]["id"]

    resp = client.get(f"/api/v1/users/{student_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "STUDENT"
    assert "current_class_id" in data
    assert "date_of_birth" in data


def test_admin_can_view_teacher_detail_with_course_count(client):
    headers = _admin_headers(client, email="admin.detail.teacher@example.com")
    teacher_headers = _auth_headers(client, "detail.teacher@example.com", "TEACHER")
    teacher_id = client.get("/api/v1/users/me", headers=teacher_headers).json()["data"]["id"]

    class_id, subject_id = _get_seeded_class_and_subject(client, teacher_headers)
    client.post(
        "/api/v1/courses",
        json={"class_id": class_id, "subject_id": subject_id, "title": "Detail Course"},
        headers=teacher_headers,
    )

    resp = client.get(f"/api/v1/users/{teacher_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "TEACHER"
    assert data["course_count"] == 1
    assert data["teacher_verified"] is False


def test_non_admin_cannot_view_user_detail(client):
    a_headers = _auth_headers(client, "peeker.student@example.com", "STUDENT")
    b_headers = _auth_headers(client, "target.student@example.com", "STUDENT")
    target_id = client.get("/api/v1/users/me", headers=b_headers).json()["data"]["id"]

    resp = client.get(f"/api/v1/users/{target_id}", headers=a_headers)
    assert resp.status_code == 403


def test_get_user_detail_not_found(client):
    headers = _admin_headers(client, email="admin.notfound@example.com")
    resp = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000", headers=headers)
    assert resp.status_code == 404


def test_super_admin_can_create_admin_account(client):
    headers = _super_admin_headers(client, email="superadmin.create.admin@example.com")
    resp = client.post(
        "/api/v1/users",
        json={"email": "new.admin@example.com", "full_name": "New Admin", "role": "ADMIN"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["role"] == "ADMIN"
    assert data["must_reset_password"] is True
    assert len(data["temporary_password"]) >= 8


def test_regular_admin_cannot_create_admin_account(client):
    headers = _admin_headers(client, email="admin.no.escalate@example.com")
    resp = client.post(
        "/api/v1/users",
        json={"email": "blocked.admin@example.com", "full_name": "Blocked Admin", "role": "ADMIN"},
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_super_admin_can_still_create_student_and_teacher(client):
    headers = _super_admin_headers(client, email="superadmin.create.rest@example.com")
    student_resp = client.post(
        "/api/v1/users",
        json={"email": "sa.student@example.com", "full_name": "SA Student", "role": "STUDENT"},
        headers=headers,
    )
    assert student_resp.status_code == 201
    teacher_resp = client.post(
        "/api/v1/users",
        json={"email": "sa.teacher@example.com", "full_name": "SA Teacher", "role": "TEACHER"},
        headers=headers,
    )
    assert teacher_resp.status_code == 201


def test_admin_created_admin_account_must_reset_password(client):
    headers = _super_admin_headers(client, email="superadmin.reset.flow@example.com")
    created = client.post(
        "/api/v1/users",
        json={"email": "resetflow.admin@example.com", "full_name": "Reset Flow Admin", "role": "ADMIN"},
        headers=headers,
    ).json()["data"]
    temp_password = created["temporary_password"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetflow.admin@example.com", "password": temp_password, **solve_captcha(client)},
    )
    assert login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    me = client.get("/api/v1/users/me", headers=admin_headers).json()["data"]
    assert me["must_reset_password"] is True

    # the newly created admin can itself create student/teacher accounts,
    # but not another admin until it resets its own password? -- no such
    # restriction exists; only role determines this, not reset status.
    change = client.post(
        "/api/v1/auth/change-password",
        headers=admin_headers,
        json={"current_password": temp_password, "new_password": "BrandNewAdminPass456"},
    )
    assert change.status_code == 200


def test_list_users_filters_by_admin_role(client):
    headers = _super_admin_headers(client, email="superadmin.list.admins@example.com")
    _create_admin(email="listed.admin@example.com", role_name="ADMIN")

    resp = client.get("/api/v1/users", params={"role": "ADMIN"}, headers=headers)
    assert resp.status_code == 200
    assert any(u["email"] == "listed.admin@example.com" for u in resp.json()["data"])
    assert all(u["role"] == "ADMIN" for u in resp.json()["data"])


def test_admin_can_verify_and_unverify_teacher(client):
    admin_headers = _admin_headers(client, email="admin.verify.teacher@example.com")
    teacher_headers = _auth_headers(client, "teacher.toverify@example.com", "TEACHER")
    teacher_id = client.get("/api/v1/users/me", headers=teacher_headers).json()["data"]["id"]

    me_before = client.get("/api/v1/users/me", headers=teacher_headers).json()["data"]
    assert me_before["is_verified"] is False

    verify_resp = client.post(f"/api/v1/users/{teacher_id}/verify", headers=admin_headers)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["data"]["is_verified"] is True

    me_after = client.get("/api/v1/users/me", headers=teacher_headers).json()["data"]
    assert me_after["is_verified"] is True

    detail = client.get(f"/api/v1/users/{teacher_id}", headers=admin_headers).json()["data"]
    assert detail["teacher_verified"] is True

    unverify_resp = client.post(f"/api/v1/users/{teacher_id}/unverify", headers=admin_headers)
    assert unverify_resp.status_code == 200
    assert unverify_resp.json()["data"]["is_verified"] is False


def test_admin_can_verify_and_unverify_student(client):
    admin_headers = _admin_headers(client, email="admin.verify.student@example.com")
    student_headers = _auth_headers(client, "student.toverify@example.com", "STUDENT")
    student_id = client.get("/api/v1/users/me", headers=student_headers).json()["data"]["id"]

    verify_resp = client.post(f"/api/v1/users/{student_id}/verify", headers=admin_headers)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["data"]["is_verified"] is True

    detail = client.get(f"/api/v1/users/{student_id}", headers=admin_headers).json()["data"]
    assert detail["student_verified"] is True

    unverify_resp = client.post(f"/api/v1/users/{student_id}/unverify", headers=admin_headers)
    assert unverify_resp.status_code == 200
    assert unverify_resp.json()["data"]["is_verified"] is False


def test_non_admin_cannot_verify_user(client):
    student_a = _auth_headers(client, "student.a.noverify@example.com", "STUDENT")
    student_b_headers = _auth_headers(client, "student.b.noverify@example.com", "STUDENT")
    student_b_id = client.get("/api/v1/users/me", headers=student_b_headers).json()["data"]["id"]

    resp = client.post(f"/api/v1/users/{student_b_id}/verify", headers=student_a)
    assert resp.status_code == 403


def test_verify_requires_auth(client):
    resp = client.post("/api/v1/users/00000000-0000-0000-0000-000000000000/verify")
    assert resp.status_code == 401


def test_verify_nonexistent_user_404(client):
    headers = _admin_headers(client, email="admin.verify.404@example.com")
    resp = client.post("/api/v1/users/00000000-0000-0000-0000-000000000000/verify", headers=headers)
    assert resp.status_code == 404


def test_verify_rejects_non_student_teacher_role(client):
    admin_headers = _admin_headers(client, email="admin.verify.badrole@example.com")
    other_admin_id_headers = _admin_headers(client, email="admin.target.badrole@example.com")
    other_admin_id = client.get("/api/v1/users/me", headers=other_admin_id_headers).json()["data"]["id"]

    resp = client.post(f"/api/v1/users/{other_admin_id}/verify", headers=admin_headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_ROLE"
