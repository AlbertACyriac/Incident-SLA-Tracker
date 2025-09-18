# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)

    # env-driven config (works locally + on Render)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
    db_url = os.environ.get("DATABASE_URL", "sqlite:///incident_tracker.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # import models (for migrations)
    from app import models  # noqa: F401

    # blueprints
    from app.auth.routes import auth_bp
    from app.clients.routes import clients_bp
    from app.slas.routes import slas_bp
    from app.incidents.routes import incidents_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(slas_bp, url_prefix="/slas")
    app.register_blueprint(incidents_bp, url_prefix="/incidents")

    try:
        from app.main.routes import main_bp
        app.register_blueprint(main_bp)  # "/"
    except Exception:
        pass

    # handy CLI to create admin on any host if shell is available
    import click
    from app.models import User
    @app.cli.command("create-admin")
    @click.argument("email")
    @click.argument("password")
    def create_admin(email, password):
        if User.query.filter_by(email=email).first():
            click.echo("User already exists")
            return
        u = User(name="Admin", email=email, role="admin")
        from werkzeug.security import generate_password_hash
        u.password_hash = generate_password_hash(password)
        db.session.add(u); db.session.commit()
        click.echo(f"Admin created: {email}")

    return app
