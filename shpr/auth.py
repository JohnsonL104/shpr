import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .db import db
from .models import User
from sqlalchemy import select

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """Decorator to ensure the user is logged in before accessing a view."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Load the logged-in user from the session, if available."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        result = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        g.user = result


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user. Validates input and stores the user in the database."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            existing_user = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
            if existing_user is not None:
                error = f"User {username} is already registered."
            else:
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by validating credentials and storing the user ID in the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Log out the current user by clearing the session."""
    session.clear()
    return redirect(url_for("index"))
