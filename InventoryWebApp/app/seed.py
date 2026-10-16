import click

from . import db
from .models import Category, Product

SAMPLE = {
    "Graphics Cards": [("RTX 4060 8GB", "499.00", 6), ("RX 7800 XT 16GB", "849.00", 2)],
    "Processors": [("Ryzen 5 7600", "299.00", 10), ("Core i7-14700K", "629.00", 0)],
    "Storage": [("1TB NVMe SSD", "119.00", 25), ("4TB HDD", "159.00", 8)],
}


@click.command("seed")
def seed_command():
    """Load sample products if the table is empty."""
    if Product.query.first():
        click.echo("Already seeded")
        return
    for category_name, items in SAMPLE.items():
        category = Category(name=category_name)
        db.session.add(category)
        for name, price, stock in items:
            product = Product(name=name, description=f"{name} – sample listing", stock=stock, category=category)
            product.set_price(price)
            db.session.add(product)
    db.session.commit()
    click.echo("Seeded sample catalogue")
