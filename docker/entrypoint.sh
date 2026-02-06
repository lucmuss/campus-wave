#!/bin/bash
set -e

echo "Starting Campus Wave application..."

# Download NLTK data
echo "Downloading NLTK data..."
uv run python -c "import nltk; nltk.download('stopwords', quiet=True)"

# Set Flask environment
export FLASK_APP=server/localserver.py
export FLASK_DEBUG=1

if [ "${RUN_TESTS:-false}" = "true" ]; then
  echo "Running tests..."
  uv run pytest --tb=short -q
fi

# Run the Flask application
echo "Running Flask application..."
uv run flask run --host=0.0.0.0 --port=8085
