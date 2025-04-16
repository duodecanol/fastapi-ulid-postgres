# FastAPI ULID PostgreSQL Integration

A demonstration project showcasing the integration of [ULID (Universally Unique Lexicographically Sortable Identifier)](https://github.com/ulid/spec) with FastAPI and PostgreSQL.

## What is ULID?

ULID (Universally Unique Lexicographically Sortable Identifier) is a modern alternative to UUID. ULIDs have several advantages over UUIDs:

- **Lexicographically sortable**: ULIDs sort by time, making them ideal for database indexes
- **Case-insensitive**: ULIDs use Crockford's base32 encoding for better readability
- **URL-safe**: No special characters, making them safe for URLs
- **Monotonicity**: ULIDs can be generated in a way that guarantees monotonicity
- **Timestamp**: First 48 bits are a timestamp, allowing for time-based sorting

## Key Features

- Custom SQLAlchemy types for ULID integration with PostgreSQL
- Pydantic models for ULID validation in API requests/responses
- CRUD operations using ULID as identifiers
- API endpoints that handle ULID identifiers
- Asynchronous database operations with SQLAlchemy 2.0

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (with async support)
- Pydantic
- python-ulid
- Alembic for migrations
- uv package manager

## Project Structure

```
fastapi-ulid-postgres/
├── app/                          # Application code
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Application configuration
│   │   └── database.py           # Database setup
│   ├── models/                   # SQLAlchemy models
│   │   ├── types.py              # Custom ULID types for SQLAlchemy
│   │   └── character.py          # Example model using ULID
│   ├── schemas/                  # Pydantic schemas
│   │   ├── ulid.py               # ULID Pydantic model
│   │   └── character.py          # Example schema using ULID
│   ├── api/                      # API routes
│   │   └── v1/endpoints/         # API endpoints
│   │       └── characters.py     # Example endpoints using ULID
│   ├── crud/                     # CRUD operations
│   │   ├── base.py               # Base CRUD with ULID support
│   │   └── character.py          # Example CRUD operations
│   └── utils/                    # Utility functions
├── alembic/                      # Database migrations
├── tests/                        # Tests
├── pyproject.toml                # Project metadata and dependencies
└── README.md                     # Project documentation
```

## Key Implementation Details

### Custom SQLAlchemy Types for ULID

The project implements custom SQLAlchemy types for ULID in `app/models/types.py`:

- `UserDefinedULIDType`: A custom SQLAlchemy type that maps ULID to a PostgreSQL type
- `DifferedULIDType`: A type decorator that allows storing ULID in different PostgreSQL column types (UUID, BYTEA, CHAR)
- `_ULIDScalarCoercible`: A mixin that provides coercion methods for different ULID formats

### Pydantic Model for ULID

The project implements a custom Pydantic model for ULID validation in `app/schemas/ulid.py`:

- `ULID`: A Pydantic model that validates and serializes ULID values
- Support for various input formats (string, bytes, int)
- Proper serialization to string for API responses

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL
- uv package manager
- Docker and Docker Compose (optional)

### Installation

#### Local Development

1. Clone the repository
2. Install dependencies:
   ```
   uv venv
   source .venv/bin/activate
   uv sync
   ```
3. Set up the database:
   ```
   alembic upgrade head
   ```
4. Run the application:
   ```
   uv run python -m app.main
   ```

#### Using Docker Compose

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Start the services:
   ```
   docker compose up -d
   ```
   This will start both the PostgreSQL database and the FastAPI application.
4. To stop the services:
   ```
   docker compose down
   ```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

If you want to migrate your database, you should run following commands:

```bash
# To perform all pending migrations.
alembic upgrade head

# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"
```

### Reverting migrations

If you want to revert migrations, you should run:

```bash
# revert previous version
alembic downgrade -1

# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
alembic downgrade base
```

### Migration generation

To generate migrations you should run:

```bash
# For automatic change detection.
alembic revision --autogenerate -m "YOUR COMMENT"

# For empty file generation.
alembic revision
```

