# ───── Stage 1: Build base with Poetry ─────
FROM python:3.13-slim AS base

# Set environment variables
ENV POETRY_VERSION=1.8.2 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

# Create app directory
WORKDIR /app

# Copy only poetry files first for layer caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (virtualenv is inside container)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi


# ───── Stage 2: Production image ─────
FROM base AS prod

COPY . /app

WORKDIR /app

EXPOSE 80

CMD ["uvicorn", "src.app:app","--host", "0.0.0.0", "--port", "80"]