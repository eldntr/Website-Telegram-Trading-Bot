# backend/app/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Tambahkan impor ini
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.db.database import init_db
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.tasks import periodic_check_open_trades
from app.core.automation import run_user_autotrade_cycle # <-- Import
from app.db.models import UserConfiguration # <-- Import


last_run_timestamps: dict[str, datetime] = {}

async def master_autotrade_scheduler():
    """
    Scheduler utama yang berjalan setiap menit untuk memicu siklus autotrade per pengguna.
    """
    while True:
        await asyncio.sleep(60) # Cek setiap 60 detik
        print("\n--- [Master Scheduler] Memeriksa jadwal autotrade ---")
        
        now = datetime.utcnow()
        # Dapatkan semua konfigurasi user yang mengaktifkan autotrade
        configs_to_run = await UserConfiguration.find(
            UserConfiguration.autotrade_enabled == True
        ).to_list()
        
        for config in configs_to_run:
            user_id = str(config.user_id.id)
            last_run = last_run_timestamps.get(user_id)
            
            # Cek apakah sudah waktunya untuk menjalankan siklus
            should_run = False
            if last_run is None:
                should_run = True # Jalankan pertama kali
            else:
                next_run_time = last_run + timedelta(minutes=config.autotrade_interval_minutes)
                if now >= next_run_time:
                    should_run = True
            
            if should_run:
                print(f"[Master Scheduler] Memicu siklus autotrade untuk user_id: {user_id}")
                asyncio.create_task(run_user_autotrade_cycle(user_id))
                last_run_timestamps[user_id] = now

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logika yang dieksekusi saat startup
    print("Starting up...")
    await init_db()
    print("Database connection initialized.")
    # Jalankan job periodik di background
    print("Starting periodic job for checking trades...")
    asyncio.create_task(periodic_check_open_trades())
    # --- BARU: Jalankan Master Scheduler ---
    print("Starting master autotrade scheduler...")
    asyncio.create_task(master_autotrade_scheduler())
    yield
    # Logika yang dieksekusi saat shutdown
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