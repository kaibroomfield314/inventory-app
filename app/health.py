from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from . import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        database = "ok"
    except Exception as exc:  # report, don't crash
        current_app.logger.error("Database check failed: %s", exc)
        database = "error"
    body = {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "version": current_app.config["APP_VERSION"],
        "environment": current_app.config["APP_ENV"],
    }
    return jsonify(body), 200 if database == "ok" else 503
