import os

import pytest
from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect

from app import create_app, db
from app.models import Product
from config import TestConfig


@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"), reason="needs a Postgres TEST_DATABASE_URL")
def test_migrations_and_database():
    app = create_app(TestConfig)
    with app.app_context():
        upgrade()
        assert "product" in inspect(db.engine).get_table_names()
        product = Product(name="test", stock=1)
        product.set_price("5")
        db.session.add(product)
        db.session.commit()
        assert Product.query.count() == 1

        db.session.remove()
        downgrade(revision="base")
        assert "product" not in inspect(db.engine).get_table_names()

