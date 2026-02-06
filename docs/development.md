# Development Workflow

## Branching

- Branch from `master`.
- Naming recommendation: `feature/<topic>`, `fix/<topic>`, `chore/<topic>`.
- Keep pull requests small and focused.

## Local Workflow

```bash
just setup
just format
just check
```

## Pre-Commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## CI Expectations

CI runs lint, type checks, tests, and build.

- Lint/typecheck/build run in containerized reusable workflows.
- Tests run on Linux, macOS, and Windows with Python 3.11 and 3.12.

## Secrets

Never commit secrets. Use environment variables or local `.env`.
