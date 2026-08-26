from tests.test_admin_users import _admin_headers
from tests.test_curriculum import _auth_headers

FAKE_PNG = b"\x89PNG\r\n\x1a\nfake-png-bytes-for-tests"


def _upload_banner(client, headers, *, title="Result Showcase", link_url="", display_order=0, content=FAKE_PNG):
    return client.post(
        "/api/v1/banners",
        headers=headers,
        data={"title": title, "link_url": link_url, "display_order": display_order},
        files={"file": ("banner.png", content, "image/png")},
    )


def test_admin_can_upload_banner(client):
    headers = _admin_headers(client, email="banner.admin1@example.com")
    resp = _upload_banner(client, headers, title="Board Results 2026", link_url="https://example.com/results")
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Board Results 2026"
    assert data["link_url"] == "https://example.com/results"
    assert data["is_active"] is True


def test_non_admin_cannot_upload_banner(client):
    headers = _auth_headers(client, "banner.student1@example.com", "STUDENT")
    resp = _upload_banner(client, headers)
    assert resp.status_code == 403


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/banners",
        data={"title": "No auth", "link_url": "", "display_order": 0},
        files={"file": ("banner.png", FAKE_PNG, "image/png")},
    )
    assert resp.status_code == 401


def test_unsupported_file_type_rejected(client):
    headers = _admin_headers(client, email="banner.admin2@example.com")
    resp = client.post(
        "/api/v1/banners",
        headers=headers,
        data={"title": "Bad type", "link_url": "", "display_order": 0},
        files={"file": ("banner.txt", b"not an image", "text/plain")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_public_listing_shows_only_active_banners_in_order(client):
    headers = _admin_headers(client, email="banner.admin3@example.com")
    first = _upload_banner(client, headers, title="Second Banner", display_order=2).json()["data"]
    second = _upload_banner(client, headers, title="First Banner", display_order=1).json()["data"]
    hidden = _upload_banner(client, headers, title="Hidden Banner", display_order=0).json()["data"]
    client.patch(f"/api/v1/banners/{hidden['id']}", headers=headers, json={"is_active": False})

    resp = client.get("/api/v1/banners/public")
    assert resp.status_code == 200
    titles = [b["title"] for b in resp.json()["data"]]
    assert "Hidden Banner" not in titles
    assert titles.index("First Banner") < titles.index("Second Banner")
    assert first["id"] and second["id"]


def test_public_listing_requires_no_auth(client):
    # No Authorization header at all — this is what the anonymous home page uses.
    resp = client.get("/api/v1/banners/public")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_admin_listing_requires_permission(client):
    headers = _auth_headers(client, "banner.student2@example.com", "STUDENT")
    resp = client.get("/api/v1/banners", headers=headers)
    assert resp.status_code == 403


def test_banner_image_is_publicly_downloadable(client):
    headers = _admin_headers(client, email="banner.admin4@example.com")
    banner = _upload_banner(client, headers, content=FAKE_PNG).json()["data"]

    resp = client.get(f"/api/v1/banners/{banner['id']}/image")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content == FAKE_PNG


def test_admin_can_update_and_delete_banner(client):
    headers = _admin_headers(client, email="banner.admin5@example.com")
    banner = _upload_banner(client, headers, title="Original").json()["data"]

    update_resp = client.patch(
        f"/api/v1/banners/{banner['id']}", headers=headers, json={"title": "Updated", "is_active": False}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()["data"]
    assert updated["title"] == "Updated"
    assert updated["is_active"] is False

    delete_resp = client.delete(f"/api/v1/banners/{banner['id']}", headers=headers)
    assert delete_resp.status_code == 204

    list_resp = client.get("/api/v1/banners", headers=headers)
    assert banner["id"] not in [b["id"] for b in list_resp.json()["data"]]


def test_update_nonexistent_banner_404(client):
    headers = _admin_headers(client, email="banner.admin6@example.com")
    resp = client.patch(
        "/api/v1/banners/00000000-0000-0000-0000-000000000000", headers=headers, json={"title": "X"}
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "BANNER_NOT_FOUND"
