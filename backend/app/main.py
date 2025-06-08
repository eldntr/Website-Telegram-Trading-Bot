# backend/app/main.py
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. Import Middleware
from app.db.database import init_db
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.tasks import periodic_check_open_trades

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    print("Database connection initialized.")
    print("Starting periodic job for checking trades...")
    asyncio.create_task(periodic_check_open_trades())
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- 2. Tambahkan Konfigurasi CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Izinkan origin dari frontend Anda
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua method (GET, POST, etc.)
    allow_headers=["*"],  # Izinkan semua header
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}