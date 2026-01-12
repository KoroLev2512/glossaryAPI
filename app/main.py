from contextlib import asynccontextmanager

from fastapi import FastAPI
from .routers import terms
from .db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
	init_db()
	yield


app = FastAPI(title="Glossary API", version="0.1.0", lifespan=lifespan)

app.include_router(terms.router, prefix="/terms", tags=["terms"])


@app.get("/health")
def health_check():
	return {"status": "ok"}
