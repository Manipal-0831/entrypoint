import json
from tests.conftest import register, login, post_job


def test_home_redirects_to_login(client):
    resp = client.get("/")
    assert resp.status_code in (301, 302)


def test_register_and_login(client):
    resp = register(client)
    assert resp.status_code == 200
    assert b"EntryPoint" in resp.data

    client.get("/logout")
    resp = login(client)
    assert resp.status_code == 200


def test_duplicate_email_rejected(client):
    register(client, email="ada@example.com")
    client.get("/logout")
    resp = register(client, email="ada@example.com")
    assert b"already exists" in resp.data


def test_anyone_can_post_a_job(client):
    register(client)
    resp = post_job(client)
    assert resp.status_code == 200
    assert b"Junior Python Developer" in resp.data


def test_invalid_experience_level_rejected(client):
    register(client)
    resp = post_job(client, experience_level="Senior (10 yrs)")
    assert b"valid experience level" in resp.data


def test_search_by_keyword(client):
    register(client)
    post_job(client, title="Junior Python Developer", skills_required="Python")
    post_job(client, title="QA Fresher", skills_required="Manual Testing")

    resp = client.get("/?q=Python")
    assert b"Junior Python Developer" in resp.data
    assert b"QA Fresher" not in resp.data


def test_search_by_fresher_level(client):
    register(client)
    post_job(client, title="Intern Role", experience_level="Internship")
    post_job(client, title="Fresher Role", experience_level="Fresher (0 yrs)")

    resp = client.get("/?experience_level=Internship")
    assert b"Intern Role" in resp.data
    assert b"Fresher Role" not in resp.data


def test_save_toggle(client):
    register(client)
    post_job(client)

    resp = client.post("/api/jobs/1/save")
    data = json.loads(resp.data)
    assert data["saved"] is True
    assert data["save_count"] == 1

    resp = client.post("/api/jobs/1/save")
    data = json.loads(resp.data)
    assert data["saved"] is False


def test_comment_on_job(client):
    register(client)
    post_job(client)

    resp = client.post("/api/jobs/1/comments", json={"body": "Anyone applied?"})
    data = json.loads(resp.data)
    assert data["comment_count"] == 1
    assert data["body"] == "Anyone applied?"


def test_only_owner_can_close_job(client):
    register(client, name="Ada", email="ada@example.com")
    post_job(client)
    client.get("/logout")

    register(client, name="Grace", email="grace@example.com")
    resp = client.post("/api/jobs/1/toggle")
    assert resp.status_code == 403


def test_owner_can_close_job(client):
    register(client, name="Ada", email="ada@example.com")
    post_job(client)

    resp = client.post("/api/jobs/1/toggle")
    data = json.loads(resp.data)
    assert data["is_active"] is False
