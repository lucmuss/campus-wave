# Campus Wave

Campus Wave is an ontology-based audio information retrieval system created in the context of academic work at the University of Passau.

## Features

- Audio filtering and preprocessing pipeline.
- Speech recognition with PocketSphinx.
- Keyword ranking and similarity computation.
- Flask-based web UI for search and administration.
- uv + Justfile based local developer workflow.

## Requirements

- Python 3.11 or newer.
- `uv` installed: <https://docs.astral.sh/uv/>

## Installation

```bash
uv venv
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra dev --frozen
cp -n .env.example .env
```

## Configuration

All secrets must come from environment variables or a local `.env` file.

Required variables:

- `FLASK_SECRET_KEY`
- `ADMINISTRATION_PASSWORD`

Example:

```bash
cp .env.example .env
```

Then edit `.env` and replace placeholder values.

## Usage

Start the application:

```bash
just dev
```

The Flask server listens on `http://127.0.0.1:8085`.

## Examples

- CLI/example scripts: `examples/`
- Extended setup and release docs: `docs/`

## Development Workflow

```bash
just setup
just format
just check
just ci
```

Key tasks:

- `just format`: apply Ruff formatting and fixes.
- `just lint`: Ruff + Black + Flake8 checks.
- `just typecheck`: MyPy checks.
- `just test`: run Pytest.
- `just ci`: local CI simulation (`lint -> typecheck -> test -> build`).

## Git Workflow

- Create short-lived branches from `master`.
- Open pull requests for every change.
- CI must pass before merge.
- Use tagged releases (`vX.Y.Z`) for PyPI and binary publishing.

Detailed workflow is documented in `docs/development.md`.

## Release

1. Update version in `pyproject.toml`.
2. Run `just ci`.
3. Create and push a git tag: `vX.Y.Z`.
4. GitHub Actions publishes artifacts (PyPI workflow + binary workflow).

## Troubleshooting

- Missing NLTK stopwords: run `uv run python -c "import nltk; nltk.download('stopwords')"`
- Dependency lock mismatch: run `UV_PROJECT_ENVIRONMENT=.venv uv sync --extra dev --frozen`
- Stale cache/build files: run `just clean`

## License

MIT License. See `LICENSE`.
