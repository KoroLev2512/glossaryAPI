SHELL := /bin/bash
APP := glossaryapi
IMAGE := $(APP):latest
VENV := .venv
HOST := 0.0.0.0
PORT := 8000
DOCS_PORT := 8001

.PHONY: help install run test docs docs-serve docker-build docker-run compose-up compose-down clean generate-grpc run-grpc locust-rest locust-grpc locust-both

help:
	@echo "Common targets:"
	@echo "  make install      - create venv and install deps with uv"
	@echo "  make run          - run FastAPI app locally"
	@echo "  make test         - run pytest"
	@echo "  make docs         - generate static OpenAPI docs (json + html)"
	@echo "  make docs-serve   - serve static docs at http://localhost:$(DOCS_PORT)"
	@echo "  make docker-build - build Docker image"
	@echo "  make docker-run   - run Docker container (maps 8000, mounts sqlite)"
	@echo "  make compose-up   - run via docker compose"
	@echo "  make compose-down - stop compose"
	@echo "  make clean        - remove venv and caches"
	@echo ""
	@echo "gRPC targets:"
	@echo "  make generate-grpc - generate gRPC code from proto files"
	@echo "  make run-grpc      - run gRPC server on port 50051"
	@echo ""
	@echo "Load testing targets:"
	@echo "  make locust-rest   - run Locust tests for REST API (web UI on http://localhost:8089)"
	@echo "  make locust-grpc   - run Locust tests for gRPC API (web UI on http://localhost:8089)"
	@echo "  make locust-both   - run Locust tests for both REST and gRPC"

install: $(VENV)
	. $(VENV)/bin/activate && uv pip install -e . && uv pip install '.[dev]'

$(VENV):
	uv venv

run:
	$(VENV)/bin/uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

test:
	$(VENV)/bin/pytest -q

docs:
	$(VENV)/bin/python scripts/generate_docs.py

docs-serve:
	cd static_docs && python3 -m http.server $(DOCS_PORT)

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -p $(PORT):8000 -e HOST=$(HOST) -e PORT=8000 -v $(PWD)/glossary.db:/app/glossary.db $(IMAGE)

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

clean:
	rm -rf $(VENV) .pytest_cache __pycache__ *.pyc proto/*_pb2.py proto/*_pb2_grpc.py

generate-grpc:
	$(VENV)/bin/python scripts/generate_grpc.py

run-grpc:
	$(VENV)/bin/python -m app.grpc_server

locust-rest:
	$(VENV)/bin/locust -f locustfile_rest.py --host=http://localhost:8000

locust-grpc:
	$(VENV)/bin/locust -f locustfile_grpc.py --host=localhost:50051

locust-both:
	$(VENV)/bin/locust -f locustfile.py --host=http://localhost:8000
