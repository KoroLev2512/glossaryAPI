# Glossary API

Author: Yurii Korolev

FastAPI-based glossary service with SQLite storage, validated by Pydantic, and containerized. Static OpenAPI docs (JSON + HTML) are generated from the built-in FastAPI OpenAPI.

## Features
- CRUD operations on glossary terms
- Input validation and response schemas via Pydantic
- SQLite persistence via SQLModel/SQLAlchemy
- Auto-generated OpenAPI schema and static Swagger/ReDoc HTML
- Dockerfile and Docker Compose for containerized deployment

## Endpoints
- GET `/health` — health check
- GET `/terms/` — list all terms
- GET `/terms/{keyword}` — get a term by keyword
- POST `/terms/` — create a term
- PUT `/terms/{keyword}` — update a term (keyword and/or description)
- DELETE `/terms/{keyword}` — remove a term

<img width="1440" height="810" alt="image" src="https://github.com/user-attachments/assets/e5f1ab8d-dd58-49bf-ac93-7b93ed2c4c59" />


Interactive docs when running the service:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quickstart (Makefile)
Ensure you have `uv` installed (Python package manager) and Docker (optional for container runs).

```bash
# 1) Create venv and install dependencies
make install

# 2) Run the app locally (http://localhost:8000)
make run

# 3) Run tests
make test

# 4) Generate static OpenAPI docs (JSON + HTML in static_docs/)
make docs

# 5) Serve static docs (so JS loads without CORS/file:// issues)
make docs-serve
# Open http://localhost:8001/swagger.html or http://localhost:8001/redoc.html
```

Why serving matters: opening `file://` HTML directly blocks required JS APIs (e.g., `process`), causing errors like "Something went wrong... process is not defined". Use `make docs-serve` to host files over HTTP.

## Example requests
```bash
# Create a term
curl -X POST http://localhost:8000/terms/ \
  -H 'Content-Type: application/json' \
  -d '{"keyword": "API", "description": "Application Programming Interface"}'

# List terms
curl http://localhost:8000/terms/

# Get by keyword
curl http://localhost:8000/terms/API

# Update term
curl -X PUT http://localhost:8000/terms/API \
  -H 'Content-Type: application/json' \
  -d '{"keyword": "APIv2", "description": "Updated"}'

# Delete term
curl -X DELETE http://localhost:8000/terms/APIv2
```

## Static documentation
After `make docs`, open:
- `make docs-serve` then browse to:
  - `http://localhost:8001/swagger.html` (Swagger UI)
  - `http://localhost:8001/redoc.html` (ReDoc)
- Schema only: `static_docs/openapi.json`

## Docker
```bash
# Build the image
make docker-build

# Run the container (exposes :8000, mounts local sqlite DB)
make docker-run
# or vanilla Docker
# docker build -t glossaryapi:latest .
# docker run --rm -p 8000:8000 -v $(pwd)/glossary.db:/app/glossary.db glossaryapi:latest
```
<img width="1267" height="721" alt="image" src="https://github.com/user-attachments/assets/d83fb3f8-a6e5-47a4-851c-d58c05d3e271" />


## Docker Compose
```bash
# Start in detached mode
make compose-up

# Stop containers
make compose-down
```

## Notes
- The SQLite database file is `glossary.db` (mounted when running in Docker/Docker Compose).
- Static docs are generated from the FastAPI app routes; regenerate after any API changes using `make docs`.
