set shell := ["bash", "-c"]

default:
    @just --list

setup:
    uv venv
    UV_PROJECT_ENVIRONMENT=.venv uv sync --extra dev --frozen
    cp -n .env.example .env || true

dev:
    bash docker/entrypoint.sh

format:
    uv run ruff format campus_wave controller model server tests
    uv run ruff check --fix campus_wave controller model server tests

lint:
    uv run ruff check campus_wave controller model server tests
    uv run ruff format --check campus_wave controller model server tests
    uv run --with black black --check campus_wave controller model server tests
    uv run --with flake8 flake8 . --max-line-length=100 --extend-ignore=E203,W503

typecheck:
    uv run mypy campus_wave controller model server

test:
    uv run pytest

build:
    uv run --with build python -m build
    uv run --with twine twine check dist/*

check: lint typecheck test

ci: check build

docker-up:
    docker compose up -d --build
    docker compose logs -f

docker-down:
    docker compose down

clean:
    find . -type d -name "__pycache__" -prune -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov build dist *.egg-info
