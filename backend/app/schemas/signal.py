# backend/app/schemas/signal.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SignalOut(BaseModel):
    id: str = Field(..., alias="_id")
    coin_pair: str
    risk_level: Optional[str]
    entry_price: Optional[float]
    targets: List[Dict[str, Any]]
    stop_losses: List[Dict[str, Any]]
    timestamp: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }