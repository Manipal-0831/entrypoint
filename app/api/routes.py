from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Comment, SavedJob

api_bp = Blueprint("api", __name__)


@api_bp.route("/jobs/<int:job_id>/save", methods=["POST"])
@login_required
def toggle_save(job_id):
    job = Job.query.get_or_404(job_id)

    existing = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first()
    if existing:
        db.session.delete(existing)
        saved = False
    else:
        db.session.add(SavedJob(user_id=current_user.id, job_id=job.id))
        saved = True
    db.session.commit()

    return jsonify(saved=saved, save_count=job.save_count())


@api_bp.route("/jobs/<int:job_id>/comments", methods=["POST"])
@login_required
def add_comment(job_id):
    job = Job.query.get_or_404(job_id)
    data = request.get_json(silent=True) or request.form
    body = (data.get("body") or "").strip()

    if not body:
        return jsonify(error="Comment can't be empty."), 400
    if len(body) > 300:
        return jsonify(error="Keep comments under 300 characters."), 400

    comment = Comment(body=body, author=current_user, job=job)
    db.session.add(comment)
    db.session.commit()

    return jsonify(
        id=comment.id,
        body=comment.body,
        name=current_user.name,
        comment_count=job.comment_count(),
    )


@api_bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
def toggle_job_active(job_id):
    job = Job.query.get_or_404(job_id)
    if job.posted_by != current_user.id:
        return jsonify(error="Only the person who posted this job can close it."), 403

    job.is_active = not job.is_active
    db.session.commit()
    return jsonify(is_active=job.is_active)
