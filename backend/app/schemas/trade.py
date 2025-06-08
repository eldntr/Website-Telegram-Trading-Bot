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
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }