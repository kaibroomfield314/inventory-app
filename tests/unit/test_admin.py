
from werkzeug.security import generate_password_hash

from app import db
from app.models import Product

# helpers
def login(app, client):
    app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("secret")
    return client.post("/admin/login", data={"username": "admin", "password": "secret"})

def make_product():
    product = Product(name="product test", stock=2)
    product.set_price("100")
    db.session.add(product)
    db.session.commit()
    return product

# auth tests
def test_login_works(app, client):
    response = login(app, client)
    assert response.status_code == 302 # HTTP 302 FOUND
    assert response.headers["Location"] == "/admin/"
    assert client.get("/admin/").status_code == 200

def test_admin_login_link_only_appears_on_homepage(app, client):
    assert b"Admin Login" in client.get("/").data

    login(app, client)
    assert b"Admin Login" not in client.get("/admin/").data

def test_wrong_password(app, client):
    app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("secret")
    response = client.post("/admin/login", data={"username": "admin", "password": "wrong"})
    assert b"Wrong username or password" in response.data
    assert client.get("/admin/").status_code == 302

def test_wrong_username(app, client):
    app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("secret")
    response = client.post("/admin/login", data={"username": "bob", "password": "secret"})
    assert b"Wrong username or password" in response.data
    assert client.get("/admin/").status_code == 302

def test_logout(app, client):
  login(app, client)
  client.get("/admin/logout")
  assert client.get("/admin/").status_code == 302
  
def test_admin_requires_login(app, client):
  assert client.get("/admin/").status_code == 302
  
def test_actions_require_login(app, client):
    product = make_product()
    client.post(f"/admin/products/{product.id}/edit", data={"name": "test", "price": "1", "stock": "1"})
    client.post(f"/admin/products/{product.id}/stock", data={"change": "1"})
    client.post(f"/admin/products/{product.id}/delete")
    saved = db.session.get(Product, product.id)
    assert saved is not None
    assert saved.name == "product test"
    assert saved.stock == 2

# product tests
def test_admin_table_lists_products(app, client):
  login(app,client)
  make_product()
  assert b"product test" in client.get("/admin/").data

def test_add_product(app, client):
  login(app, client)
  assert client.get("/admin/products/new").status_code == 200 # HTTP 200 OK
  client.post("/admin/products/new", data={"name": "SSD Test", "price": "99", "stock": "3"})
  assert Product.query.filter_by(name="SSD Test").count() == 1

def test_edit_product(app, client):
    login(app, client)
    product = make_product()
    client.post(f"/admin/products/{product.id}/edit", data={"name": "name test", "price": "5", "stock": "1"})
    assert db.session.get(Product, product.id).name == "name test"

def test_delete_product(app, client):
    login(app, client)
    product = make_product()
    other = make_product()
    client.post(f"/admin/products/{product.id}/delete")
    assert db.session.get(Product, product.id) is None
    assert db.session.get(Product, other.id) is not None

def test_stock_buttons(app, client):
    login(app, client)
    product = make_product()
    client.post(f"/admin/products/{product.id}/stock", data={"change": "1"})
    assert db.session.get(Product, product.id).stock == 3
    for _ in range(5):
        client.post(f"/admin/products/{product.id}/stock", data={"change": "-1"})
    assert db.session.get(Product, product.id).stock == 0
