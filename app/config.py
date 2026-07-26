import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Central app configuration, driven by environment variables so the
    same code runs locally (SQLite) and in production (MySQL)."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me-in-production")

    # DATABASE_URL examples:
    #   MySQL:  mysql+pymysql://user:password@host:3306/entrypoint
    #   SQLite: sqlite:///entrypoint.db   (default, zero setup, local only)
    _default_sqlite = "sqlite:///" + os.path.join(basedir, "entrypoint.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _default_sqlite)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # avoids "MySQL server has gone away" on cold starts
        "pool_recycle": 280,
    }

    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    JOBS_PER_PAGE = 15

    EXPERIENCE_LEVELS = ["Fresher (0 yrs)", "0-1 yrs", "Internship"]
    JOB_TYPES = ["Full-time", "Internship", "Contract"]
