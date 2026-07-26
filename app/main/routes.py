from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, SavedJob

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "")
    experience_level = request.args.get("experience_level", "")
    page = request.args.get("page", 1, type=int)

    query = Job.query.filter_by(is_active=True)

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Job.title.ilike(like), Job.skills_required.ilike(like),
                   Job.company_name.ilike(like))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    pagination = query.order_by(Job.created_at.desc()) \
        .paginate(page=page, per_page=current_app.config["JOBS_PER_PAGE"], error_out=False)

    return render_template("index.html", jobs=pagination.items, pagination=pagination,
                            q=q, location=location, job_type=job_type,
                            experience_level=experience_level)


@main_bp.route("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("job_detail.html", job=job)


@main_bp.route("/post-job", methods=["GET", "POST"])
@login_required
def post_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company_name = request.form.get("company_name", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "")
        experience_level = request.form.get("experience_level", "")
        skills_required = request.form.get("skills_required", "").strip()
        description = request.form.get("description", "").strip()
        external_link = request.form.get("external_link", "").strip() or None
        image_url = request.form.get("image_url", "").strip() or None

        error = None
        if not title or not company_name or not location or not description:
            error = "Title, company, location, and description are required."
        elif job_type not in current_app.config["JOB_TYPES"]:
            error = "Please choose a valid job type."
        elif experience_level not in current_app.config["EXPERIENCE_LEVELS"]:
            error = "Please choose a valid experience level."

        if error:
            flash(error, "error")
            return render_template("post_job.html", form=request.form)

        job = Job(
            posted_by=current_user.id,
            title=title,
            company_name=company_name,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            skills_required=skills_required,
            description=description,
            external_link=external_link,
            image_url=image_url,
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted — thanks for sharing it!", "success")
        return redirect(url_for("main.job_detail", job_id=job.id))

    return render_template("post_job.html", form={})


@main_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.posted_by != current_user.id:
        abort(403)

    if request.method == "POST":
        job.title = request.form.get("title", "").strip()
        job.company_name = request.form.get("company_name", "").strip()
        job.location = request.form.get("location", "").strip()
        job.job_type = request.form.get("job_type", job.job_type)
        job.experience_level = request.form.get("experience_level", job.experience_level)
        job.skills_required = request.form.get("skills_required", "").strip()
        job.description = request.form.get("description", "").strip()
        job.external_link = request.form.get("external_link", "").strip() or None
        job.image_url = request.form.get("image_url", "").strip() or None
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("main.job_detail", job_id=job.id))

    return render_template("post_job.html", form=job, editing=True, job=job)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    posted = current_user.jobs_posted.order_by(Job.created_at.desc()).all()
    saved = (Job.query.join(SavedJob, SavedJob.job_id == Job.id)
             .filter(SavedJob.user_id == current_user.id)
             .order_by(SavedJob.created_at.desc()).all())
    return render_template("dashboard.html", posted=posted, saved=saved)


@main_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.bio = request.form.get("bio", "").strip()[:280]
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("edit_profile.html")
