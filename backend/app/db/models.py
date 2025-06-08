# backend/app/db/models.py
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta
from beanie import Document, Link, Indexed
from pydantic import Field, EmailStr

# --- Model dari Tahap 1 ---
class User(Document):
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    binance_api_key_encrypted: Optional[str] = None
    binance_api_secret_encrypted: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class UserConfiguration(Document):
    user_id: Link[User]
    usdt_per_trade: float = 11.0
    trailing_enabled: bool = False
    min_trailing_tp_level: int = 1
    trailing_trigger_percentage: float = 0.005
    stuck_trade_enabled: bool = False
    stuck_trade_duration_hours: int = 6
    prioritize_normal_risk: bool = True
    filter_old_signals_enabled: bool = True
    signal_validity_minutes: int = 30
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    autotrade_enabled: bool = False
    autotrade_interval_minutes: int = Field(default=5, ge=3) # Minimal 3 menit

    class Settings:
        name = "user_configurations"

# --- Model Baru untuk Tahap 2 ---

# Model untuk membaca data dari koleksi 'new_signals' yang ada
class NewSignal(Document):
    id: str = Field(..., alias="_id")
    raw_text: str
    timestamp: datetime
    message_id: Optional[int] = None
    coin_pair: str
    risk_rank: Optional[str] = None
    risk_level: Optional[str] = None
    entry_price: Optional[float] = None
    targets: List[Dict[str, Any]] = []
    stop_losses: List[Dict[str, Any]] = []
    message_type: str

    class Settings:
        name = "new_signals"
        use_cache = True
        cache_expiration_time = timedelta(minutes=10)
        cache_capacity = 512


# Model untuk koleksi 'trades' sesuai SDD
class Trade(Document):
    user_id: Link[User]
    signal_id: str  # Referensi ke _id dari 'new_signals'
    symbol: Indexed(str)
    status: Indexed(str)  # ('ACTIVE', 'CLOSED_TP', 'CLOSED_SL', 'CLOSED_MANUAL', 'ERROR')
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    quantity: Optional[float] = None
    buy_order_details: Optional[Dict[str, Any]] = None
    sell_order_details: Optional[Dict[str, Any]] = None
    buy_fee: Optional[float] = None
    sell_fee: Optional[float] = None
    net_profit_loss: Optional[float] = None
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    class Settings:
        name = "trades"