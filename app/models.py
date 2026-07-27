from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db, login_manager, bcrypt


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(280), default="")
    created_at = db.Column(db.DateTime, default=utcnow)

    jobs_posted = db.relationship("Job", backref="poster", lazy="dynamic",
        cascade="all, delete-orphan")
    saved = db.relationship("SavedJob", backref="user", lazy="dynamic",
        cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="author", lazy="dynamic",
        cascade="all, delete-orphan")
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_saved(self, job):
        return self.saved.filter_by(job_id=job.id).count() > 0

    def __repr__(self):
        return f"<User {self.email}>"


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    title = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)          # Full-time / Internship / Contract
    experience_level = db.Column(db.String(20), nullable=False)  # Fresher (0 yrs) / 0-1 yrs / Internship
    skills_required = db.Column(db.String(300), default="")
    description = db.Column(db.Text, nullable=False)
    external_link = db.Column(db.String(400))   # link to apply / original posting
    image_url = db.Column(db.String(400))       # e.g. a screenshot of a WhatsApp/flyer post
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    saves = db.relationship("SavedJob", backref="job", lazy="dynamic",
        cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="job", lazy="dynamic",
        cascade="all, delete-orphan", order_by="Comment.created_at")

    def save_count(self):
        return self.saves.count()

    def comment_count(self):
        return self.comments.count()

    def __repr__(self):
        return f"<Job {self.title} @ {self.company_name}>"


class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="uq_saved_user_job"),)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
