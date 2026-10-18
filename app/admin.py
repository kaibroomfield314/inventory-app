from flask import Blueprint, current_app, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from . import db
from .models import Product

bp = Blueprint("admin", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password_hash = current_app.config["ADMIN_PASSWORD_HASH"]
        username_ok = request.form["username"] == current_app.config["ADMIN_USERNAME"]
        if username_ok and password_hash and check_password_hash(password_hash, request.form["password"]):
            session["admin"] = True
            return redirect("/admin/")
        flash("Wrong username or password")
    return render_template("admin/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@bp.route("/")
def index():
    if not session.get("admin"): 
      return redirect("/admin/login")
    products = Product.query.order_by(Product.name).all()
    return render_template("admin/index.html", products=products)

@bp.route("/products/new", methods=["GET", "POST"])
@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id=None):
    if not session.get("admin"):
        return redirect("/admin/login")
    if product_id:
        product = db.get_or_404(Product, product_id)
    else:
        product = Product()

    if request.method == "POST":
        try:
            product.name = request.form["name"].strip()
            product.set_price(request.form["price"])
            product.stock = int(request.form["stock"])
            if product.name == "" or product.stock < 0:
                raise ValueError
        except ValueError:
            db.session.rollback()
            flash("Enter a name, a valid price and a stock of 0 or more")
            return render_template("admin/product_form.html", product=product)
        db.session.add(product)
        db.session.commit()
        flash(f"Saved {product.name}")
        return redirect("/admin/")

    return render_template("admin/product_form.html", product=product)
