FROM python:3.11-slim

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=.venv

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY . .

# Install dependencies
RUN uv venv && uv sync --frozen

# Make entrypoint executable
RUN chmod +x docker/entrypoint.sh

# Expose port
EXPOSE 8085

# Run entrypoint
CMD ["./docker/entrypoint.sh"]
