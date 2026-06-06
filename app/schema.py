from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from .db import db


def ensure_schema():
    inspector = inspect(db.engine)

    if "matches" not in inspector.get_table_names():
        return

    match_columns = {column["name"] for column in inspector.get_columns("matches")}
    additions = {
        "stage": "ALTER TABLE matches ADD COLUMN stage VARCHAR(80)",
        "venue": "ALTER TABLE matches ADD COLUMN venue VARCHAR(120)",
        "api_match_id": "ALTER TABLE matches ADD COLUMN api_match_id INTEGER",
        "potm_winner": "ALTER TABLE matches ADD COLUMN potm_winner VARCHAR(120)",
    }

    for column_name, statement in additions.items():
        if column_name not in match_columns:
            try:
                db.session.execute(text(statement))
            except OperationalError as error:
                if "duplicate column name" not in str(error).lower():
                    raise

    if "predictions" in inspector.get_table_names():
        prediction_columns = {column["name"] for column in inspector.get_columns("predictions")}
        if "potm_prediction" not in prediction_columns:
            try:
                db.session.execute(text("ALTER TABLE predictions ADD COLUMN potm_prediction VARCHAR(120)"))
            except OperationalError as error:
                if "duplicate column name" not in str(error).lower():
                    raise

    db.session.commit()
