from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, bcrypt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_helpers():
        from datetime import datetime, timezone
        return {
            "now": datetime.now(timezone.utc),
            "EXPERIENCE_LEVELS": app.config["EXPERIENCE_LEVELS"],
            "JOB_TYPES": app.config["JOB_TYPES"],
        }

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    return app
