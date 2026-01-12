import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db

client = TestClient(app)


def setup_module(_module):
	init_db()


def test_health():
	resp = client.get("/health")
	assert resp.status_code == 200
	assert resp.json()["status"] == "ok"


def test_list_empty():
	resp = client.get("/terms/")
	assert resp.status_code == 200
	assert resp.json() == []


def test_create_term():
	resp = client.post("/terms/", json={"keyword": "API", "description": "Application Programming Interface"})
	assert resp.status_code == 201
	data = resp.json()
	assert data["keyword"] == "API"


def test_get_term():
	resp = client.get("/terms/API")
	assert resp.status_code == 200
	assert resp.json()["description"].startswith("Application Programming")


def test_conflict_create():
	resp = client.post("/terms/", json={"keyword": "API", "description": "Duplicate"})
	assert resp.status_code == 409


def test_update_term_keyword_and_description():
	resp = client.put("/terms/API", json={"keyword": "APIv2", "description": "Updated"})
	assert resp.status_code == 200
	data = resp.json()
	assert data["keyword"] == "APIv2"
	assert data["description"] == "Updated"


def test_get_updated_term():
	resp = client.get("/terms/APIv2")
	assert resp.status_code == 200


def test_delete_term():
	resp = client.delete("/terms/APIv2")
	assert resp.status_code == 204


def test_get_deleted_term():
	resp = client.get("/terms/APIv2")
	assert resp.status_code == 404
