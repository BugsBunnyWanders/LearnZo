# LearnZo Backend

AI-native adaptive learning platform backend service built with FastAPI, SQLAlchemy 2.x, PostgreSQL, and Alembic.

## Getting Started

### Prerequisites
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

### Installation
```bash
# Sync all dependencies including dev tools
uv sync --all-extras
```

### Running the Development Server
```bash
uv run uvicorn app.main:app --reload --port 8000
```

### Running Tests
```bash
uv run pytest
```

### Code Formatting & Linting
```bash
uv run ruff check .
uv run ruff format .
```

