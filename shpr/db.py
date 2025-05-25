from flask_sqlalchemy import SQLAlchemy
import time
from sqlalchemy.exc import OperationalError
import click

db = SQLAlchemy()

def init_db(retries=5, delay=1):
    """Initialize the database, retrying if the database is not ready."""
    for attempt in range(retries):
        try:
            db.create_all()
            click.echo("Database initialized successfully.")  # Log success
            break
        except OperationalError as e:
            if attempt < retries - 1:
                time.sleep(delay)
                click.echo(f"Waiting for database to be ready, Retries remaining: {retries-attempt-1}")
            else:
                raise e

def init_app(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)

    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        with app.app_context():
            init_db()

        click.echo("Initialized the database.")
