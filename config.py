import os
from pathlib import Path

from dotenv import load_dotenv


BASEDIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASEDIR / "instance"

load_dotenv(BASEDIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "replace-me-with-a-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'fifawc.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_TITLE = "FIFAWC2026"
    MATCH_POINTS = 3
    POTM_POINTS = 2
    FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    FOOTBALL_DATA_BASE_URL = os.environ.get("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4")
    FOOTBALL_DATA_COMPETITION_CODE = os.environ.get("FOOTBALL_DATA_COMPETITION_CODE", "WC")
