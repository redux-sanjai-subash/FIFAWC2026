from datetime import datetime

from .db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    favorite_team = db.Column(db.String(80), nullable=True)

    predictions = db.relationship("Prediction", backref="user", lazy=True, cascade="all, delete-orphan")
    mvp_prediction = db.relationship("MvpPrediction", backref="user", uselist=False, lazy=True, cascade="all, delete-orphan")


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.String(80), nullable=False)
    team_b = db.Column(db.String(80), nullable=False)
    kickoff_time = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(80), nullable=True)
    venue = db.Column(db.String(120), nullable=True)
    api_match_id = db.Column(db.Integer, nullable=True)
    winner = db.Column(db.String(80), nullable=True)
    potm_winner = db.Column(db.String(120), nullable=True)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)

    predictions = db.relationship("Prediction", backref="match", lazy=True, cascade="all, delete-orphan")


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    prediction = db.Column(db.String(80), nullable=False)
    potm_prediction = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "match_id", name="uq_prediction_user_match"),
    )


class MvpPrediction(db.Model):
    __tablename__ = "mvp_predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    player_name = db.Column(db.String(120), nullable=False)
