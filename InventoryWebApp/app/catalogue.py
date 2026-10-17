from flask import Blueprint, render_template, request

from . import db
from .models import Category, Product, search_products

bp = Blueprint("catalogue", __name__)


@bp.get("/")
def index():
    text = request.args.get("q", "")
    category_id = request.args.get("category", type=int)
    return render_template(
        "catalogue/index.html",
        products=search_products(text, category_id),
        categories=Category.query.order_by(Category.name).all(),
        q=text,
        selected=category_id,
    )


@bp.get("/products/<int:product_id>")
def detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("catalogue/detail.html", product=product)
