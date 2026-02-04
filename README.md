# Campus Wave: Ontology-Based Audio Information Retrieval System

This project was created during the practical part of a master thesis at the University of Passau.

## Project Technologies
The project uses the following technologies:
- Chart.js
- Flask
- jQuery
- PocketSphinx
- Pydub
- Scikit-learn
- SpaCy
- TinyTag
- Whoosh
- YAML

## Development Setup

### Prerequisites
- Python 3.8+
- uv (modern Python package manager)

### Installation
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the project
just setup

# Start development server
just dev
```

### Available Commands
- `just setup` - Install dependencies and set up environment
- `just dev` - Start the development server
- `just format` - Format code with Ruff
- `just lint` - Check code quality with Ruff
- `just test` - Run tests with pytest
- `just check` - Run full quality check (lint + typecheck + test)
- `just docker-up` - Start Docker containers
- `just clean` - Clean up cache files

### Code Quality
This project uses modern Python tooling:
- **uv** for dependency management
- **Ruff** for linting and formatting (replaces Black, Flake8, isort)
- **pytest** for testing
- **mypy** for type checking
