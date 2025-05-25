from .db import db

class User(db.Model):
    """Represents a user in the application."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    items = db.relationship("Item", foreign_keys="Item.requestor_id",backref="requestor", lazy=True)
    completed_items = db.relationship("Item", foreign_keys="Item.completed_by_id", backref="completer", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

class Item(db.Model):
    """Represents an item in the shopping list."""
    id = db.Column(db.Integer, primary_key=True)
    requestor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __repr__(self):
        return f"<Item id={self.id} description={self.description[:20]} requestor_id={self.requestor_id}>"
