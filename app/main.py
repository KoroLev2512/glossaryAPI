from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from .routers import terms, graph
from .db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
	init_db()
	yield


app = FastAPI(title="Glossary API", version="0.1.0", lifespan=lifespan)

app.include_router(terms.router, prefix="/terms", tags=["terms"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])

# Подключение статических файлов для фронтенда
static_dir = Path("static")
if static_dir.exists():
	app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
	"""Главная страница - визуализация графа"""
	index_path = Path("static/index.html")
	if index_path.exists():
		return FileResponse("static/index.html")
	return JSONResponse({
		"message": "Glossary API",
		"docs": "/docs",
		"graph_api": "/graph/graph",
		"note": "Frontend not found. Use /docs for API documentation."
	})


@app.get("/health")
def health_check():
	return {"status": "ok"}
