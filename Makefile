.PHONY: setup dev test lint check

DEV_PASSWORD_HASH = $(shell .venv/bin/python -c "from werkzeug.security import generate_password_hash as g; print(g('$(admin)'))")

setup:
	uv venv --clear -p 3.12 .venv
	uv pip install -p .venv -r requirements-dev.txt

dev:
	.venv/bin/flask db upgrade
	.venv/bin/flask seed
	ADMIN_PASSWORD_HASH='$(DEV_PASSWORD_HASH)' .venv/bin/flask run --debug

test:
	.venv/bin/pytest tests/unit -q --cov=app --cov-report=term-missing --cov-fail-under=70

lint:
	.venv/bin/ruff check .

check: lint test
