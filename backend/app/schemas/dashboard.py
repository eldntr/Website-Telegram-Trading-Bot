# backend/app/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional

class DashboardSummary(BaseModel):
    total_net_pl: float
    total_trades_closed: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    current_portfolio_value: Optional[float] = None
    portfolio_error: Optional[str] = None