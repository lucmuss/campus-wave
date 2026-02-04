#!/bin/bash
set -e

echo "Starting Campus Wave application..."

# Activate virtual environment
source .venv/bin/activate

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('stopwords')"

# Set Flask environment
export FLASK_APP=server/localserver.py
export FLASK_DEBUG=1

# Run the Flask application
echo "Running Flask application..."
flask run --host=0.0.0.0 --port=8085
