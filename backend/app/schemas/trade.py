# backend/app/schemas/trade.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TradeActivate(BaseModel):
    signal_id: str

class TradeOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    signal_id: str
    symbol: str
    status: str
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    quantity: Optional[float] = None
    buy_fee: Optional[float] = None
    sell_fee: Optional[float] = None
    net_profit_loss: Optional[float] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # <-- Diubah
        validate_by_name = True # <-- Diubah
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }