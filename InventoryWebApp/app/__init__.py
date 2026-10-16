import json
import logging
import time

from flask import Flask, g, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401  (registers tables)
    from .admin import bp as admin_bp
    from .catalogue import bp as catalogue_bp
    from .health import bp as health_bp
    from .seed import seed_command

    app.register_blueprint(catalogue_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(health_bp)
    app.cli.add_command(seed_command)

    access_log = logging.getLogger("access")
    access_log.setLevel(logging.INFO)
    access_log.propagate = False
    if not access_log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        access_log.addHandler(handler)

    @app.before_request
    def start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def log_request(response):
        started = g.get("start", time.perf_counter())
        access_log.info(json.dumps({
            "type": "access",
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "version": app.config["APP_VERSION"],
        }))
        return response

    @app.context_processor
    def inject_globals():
        return {"app_version": app.config["APP_VERSION"], "app_env": app.config["APP_ENV"]}

    return app
