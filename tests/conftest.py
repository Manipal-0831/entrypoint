import pytest
from app import create_app
from app.config import Config
from app.extensions import db as _db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, name="Ada", email="ada@example.com", password="hunter22"):
    return client.post("/register", data={
        "name": name, "email": email, "password": password,
    }, follow_redirects=True)


def login(client, email="ada@example.com", password="hunter22"):
    return client.post("/login", data={
        "email": email, "password": password,
    }, follow_redirects=True)


def post_job(client, **overrides):
    data = {
        "title": "Junior Python Developer",
        "company_name": "Acme Corp",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "experience_level": "Fresher (0 yrs)",
        "skills_required": "Python, SQL",
        "description": "Great first job for a fresher.",
        "external_link": "",
        "image_url": "",
    }
    data.update(overrides)
    return client.post("/post-job", data=data, follow_redirects=True)
