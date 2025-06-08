# backend/app/schemas/configuration.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConfigurationBase(BaseModel):
    usdt_per_trade: Optional[float] = Field(None, gt=0)
    trailing_enabled: Optional[bool] = None
    min_trailing_tp_level: Optional[int] = Field(None, ge=1)
    trailing_trigger_percentage: Optional[float] = Field(None, gt=0)
    stuck_trade_enabled: Optional[bool] = None
    stuck_trade_duration_hours: Optional[int] = Field(None, ge=1)
    prioritize_normal_risk: Optional[bool] = None
    filter_old_signals_enabled: Optional[bool] = None
    signal_validity_minutes: Optional[int] = Field(None, ge=1)

class ConfigurationUpdate(ConfigurationBase):
    pass

class ConfigurationOut(ConfigurationBase):
    user_id: str
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }