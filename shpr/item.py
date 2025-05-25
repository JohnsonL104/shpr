from flask import Blueprint, json
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from sqlalchemy.orm import aliased
from sqlalchemy import select

from .auth import login_required
from .db import db
from .models import Item, User
from .helper import is_mobile

bp = Blueprint("item", __name__)


@bp.route("/")
def index():
    """Display the list of items, optionally filtered by username or status."""
    username = request.args.get("username")
    status = request.args.get("status", "requested")

    CompletedByUser = aliased(User)
    query = (
        select(
            Item.id, Item.description, Item.created, Item.requestor_id, Item.link, Item.image, Item.completed_date, Item.completed_by_id,
            User.username.label("requestor"),
            CompletedByUser.username.label("completed_by")
        )
        .join(User, Item.requestor_id == User.id)
        .outerjoin(CompletedByUser, Item.completed_by_id == CompletedByUser.id)
    )

    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if status == "requested":
        query = query.filter(Item.completed_date.is_(None))
    elif status == "completed":
        query = query.filter(Item.completed_date.isnot(None))

    items = db.session.execute(query.order_by(Item.created.desc())).all()

    # Prepare items as dicts for template compatibility
    item_data = [
        {
            "id": item.id,
            "description": item.description,
            "created": item.created,
            "requestor_id": item.requestor_id,
            "requestor": item.requestor,
            "link": item.link,
            "image": item.image,
            "completed_date": item.completed_date,
            "completed_by_id": item.completed_by_id,
            "completed_by": item.completed_by if item.completed_by else None
        }
        for item in items
    ]
    return render_template("item/index.html", items=item_data, is_mobile=is_mobile())


def get_item(id, check_requestor=True):
    """Retrieve an item by ID, optionally checking if the current user is the requestor."""
    query = (
        select(Item, User)
        .join(User, Item.requestor_id == User.id)
        .filter(Item.id == id)
    )
    item = db.session.execute(query).first()
    if item is None:
        abort(404, f"Item id {id} doesn't exist.")
    item_obj, user_obj = item
    if check_requestor and item_obj.requestor_id != g.user.id:
        abort(403)
    # Return a dict for template compatibility
    return {
        "id": item_obj.id,
        "description": item_obj.description,
        "link": item_obj.link,
        "created": item_obj.created,
        "requestor_id": item_obj.requestor_id,
        "requestor": user_obj.username,
        "image": item_obj.image,
        "completed_date": item_obj.completed_date
    }


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new item and add it to the shopping list."""
    if request.method == "POST":
        description = request.form["description"]
        link = request.form["link"]
        error = None

        if not description:
            error = "Description is required."

        if error is not None:
            flash(error)
        else:
            item = Item(description=description, link=link, requestor_id=g.user.id)
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("item.index"))

    return render_template("item/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update an existing item in the shopping list."""
    item = get_item(id)
    if request.method == "POST":
        description = request.form["description"]
        link = request.form["link"]
        error = None

        if not description:
            error = "Description is required."

        if error is not None:
            flash(error)
        else:
            item_obj = db.session.execute(select(Item).where(Item.id == id)).scalar_one()
            item_obj.description = description
            item_obj.link = link
            db.session.commit()
            return redirect(url_for("item.index"))

    return render_template("item/update.html", item=item)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete an item from the shopping list."""
    item_obj = db.session.execute(select(Item).where(Item.id == id)).scalar_one_or_none()

    if item_obj is None:
        abort(404, f"Item id {id} doesn't exist.")

    db.session.delete(item_obj)
    db.session.commit()
    return redirect(url_for("item.index"))


@bp.route("/<int:id>/complete", methods=("POST",))
@login_required
def complete(id):
    """Mark an item as completed by the current user."""
    item = db.session.execute(select(Item).where(Item.id == id)).scalar_one_or_none()

    if item is None:
        abort(404, f"Item id {id} doesn't exist.")

    if item.completed_by_id is not None:
        abort(400, f"Item id {id} is already completed.")

    item.completed_date = db.func.now()
    item.completed_by_id = g.user.id
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}