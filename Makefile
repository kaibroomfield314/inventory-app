.PHONY: setup dev test lint integration check

admin ?= admin
DEV_PASSWORD_HASH = $(shell .venv/bin/python -c "from werkzeug.security import generate_password_hash as g; print(g('$(admin)'))")
CI_DB_URL = postgresql+psycopg://test:test@localhost:5433/inventory_test
export PATH := $(CURDIR)/.venv/bin:$(PATH)


setup:
	uv venv --clear -p 3.12 .venv
	uv pip install -p .venv -r requirements-dev.txt

dev:
	flask db upgrade
	flask seed
	ADMIN_PASSWORD_HASH='$(DEV_PASSWORD_HASH)' flask run --debug

test:
	pytest tests/unit -q --cov=app --cov-report=term-missing --cov-fail-under=70

lint:
	ruff check .

integration:
	-docker rm -f ci-pg
	docker run -d --rm --name ci-pg -p 5433:5432 -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=inventory_test postgres:16
	until docker exec ci-pg pg_isready -h 127.0.0.1 -U test -q; do sleep 1; done
	TEST_DATABASE_URL=postgresql+psycopg://test:test@localhost:5433/inventory_test .venv/bin/pytest tests/integration -v
	docker rm -f ci-pg

check: lint test integration
