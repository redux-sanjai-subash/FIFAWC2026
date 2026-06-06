from pathlib import Path

from flask import Flask, jsonify

from .db import db
from .schema import ensure_schema
from .utils.world_cup_data import seed_matches_if_empty


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    instance_path = Path(app.root_path).parent / "instance"
    instance_path.mkdir(exist_ok=True)

    db.init_app(app)

    from .api import api_bp

    app.register_blueprint(api_bp)

    @app.get("/health")
    def health():
        return "ok"

    @app.get("/")
    def root():
        return jsonify({"service": app.config["APP_TITLE"], "api": "/api"})

    with app.app_context():
        db.create_all()
        ensure_schema()
        seed_matches_if_empty()

    return app
