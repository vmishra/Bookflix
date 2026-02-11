from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.router import api_router
from app.api.ws import ws_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.covers_path, exist_ok=True)
    yield


app = FastAPI(
    title="Bookflix API",
    description="Netflix for Books - API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount covers as static files
app.mount("/covers", StaticFiles(directory=settings.covers_path), name="covers")

app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
