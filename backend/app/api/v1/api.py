# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, configurations, signals, trades, dashboard, websockets

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include user routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Rute dari Tahap 2
api_router.include_router(configurations.router, prefix="/configurations", tags=["Configurations"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])

# --- Rute Baru untuk Tahap Ini ---
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# --- Rute Baru untuk Tahap Ini ---
api_router.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])