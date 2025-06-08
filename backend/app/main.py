# backend/app/main.py
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.tasks import periodic_check_open_trades # <-- Ditambahkan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logika yang dieksekusi saat startup
    print("Starting up...")
    await init_db()
    print("Database connection initialized.")
    # --- BARU: Jalankan job periodik di background ---
    print("Starting periodic job for checking trades...")
    asyncio.create_task(periodic_check_open_trades())
    yield
    # Logika yang dieksekusi saat shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}