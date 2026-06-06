import os

from app import create_app
from app.db import db


app = create_app()

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8082")), debug=True)

