from flask import Blueprint, current_app, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash

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
    return render_template("admin/index.html", products = products)
