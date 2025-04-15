# Character Chat Settings Management System

A management system for character chat prompt settings with chatting session and messages store.

## Features

- Flexible settings management
  - Dynamic addition/removal of settings
  - Settings templates, specifications, and instances
- Character information management
- Chat session management
- Chat message storage
- API compatible with Langgraph and langchain.RemoteRunnable

## Tech Stack

- Python 3.12
- PostgreSQL
- SQLAlchemy (ORM)
- FastAPI
- uv package manager

## Project Structure

```
character-chat-settings/
├── app/                          # Application code
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core functionality
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── api/                      # API routes
│   ├── crud/                     # CRUD operations
│   └── services/                 # Business logic
├── alembic/                      # Database migrations
├── tests/                        # Tests
├── pyproject.toml                # Project metadata and dependencies
└── README.md                     # Project documentation
```

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
   uv pip install -e .
   ```
3. Set up the database:
   ```
   alembic upgrade head
   ```
4. Run the application:
   ```
   uvicorn app.main:get_app --reload
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.



## Migrations

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
