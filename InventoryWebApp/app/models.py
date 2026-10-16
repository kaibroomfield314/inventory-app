from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from . import db


def _now():
    return datetime.now(UTC)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", back_populates="category")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(500), default="")
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", back_populates="products")
    updated_at = db.Column(db.DateTime(timezone=True), default=_now, onupdate=_now)

    def set_price(self, value):
        try:
            price = Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError("Price must be a number") from exc
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.price = price.quantize(Decimal("0.01"))

    def adjust_stock(self, delta):
        new_stock = (self.stock or 0) + int(delta)
        if new_stock < 0:
            raise ValueError("Stock cannot go below zero")
        self.stock = new_stock

    @property
    def in_stock(self):
        return (self.stock or 0) > 0


def search_products(text="", category_id=None):
    query = Product.query
    if text and text.strip():
        like = f"%{text.strip()}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.description.ilike(like)))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    return query.order_by(Product.name).all()
