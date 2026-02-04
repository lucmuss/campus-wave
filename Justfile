set shell := ["bash", "-c"]

default:
    @just --list

# Initialize project (uv-based)
setup:
    uv sync
    cp -n .env.example .env || true

# Start development environment (runs docker/entrypoint.sh)
dev:
    bash docker/entrypoint.sh

# Format code (Ruff)
format:
    uv run ruff format server controller model
    uv run ruff check --fix server controller model

# Lint code (read-only)
lint:
    uv run ruff check server controller model
    uv run ruff format --check server controller model

# Type check
typecheck:
    uv run mypy server controller model

# Run tests
test:
    uv run pytest

# Full quality check (lint + typecheck + test)
check: lint typecheck test

# Start Docker containers (deployment testing)
docker-up:
    docker-compose up -d --build
    docker-compose logs -f

# Stop Docker containers
docker-down:
    docker-compose down

# Clean artifacts
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .coverage htmlcov .ruff_cache