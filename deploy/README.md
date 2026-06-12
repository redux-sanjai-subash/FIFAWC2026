# Deployment Notes

This MVP keeps the same Flask deployment philosophy as the original project:

- one Flask app
- one SQLite database
- Gunicorn as the app server
- Apache as the reverse proxy

Suggested flow on Amazon Linux:

1. Create a virtual environment and install `requirements.txt`
2. Set `SECRET_KEY`
3. If you want official fixture sync, set `FOOTBALL_DATA_API_KEY`
4. Start Gunicorn with `run:app`
5. Put Apache in front of Gunicorn using the sample vhost
6. Keep the SQLite database in `instance/fifawc.db` unless `DATABASE_URL` overrides it   - if you use PostgreSQL or MySQL via `DATABASE_URL`, you must install the DB driver in `.venv` (e.g. `psycopg2-binary` for Postgres)
For local development, you can place these values in a root `.env` file.
