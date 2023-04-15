"""Defines Model for Items Entity"""
from db import db

class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)

    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items",
                           secondary="item_tags")