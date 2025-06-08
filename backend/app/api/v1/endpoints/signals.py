# backend/app/api/v1/endpoints/signals.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.api.dependencies import get_current_user
from app.db.models import User, NewSignal
from app.schemas.signal import SignalOut

router = APIRouter()

@router.get("/", response_model=List[SignalOut])
async def get_signals(
    risk_level: Optional[str] = Query(None, description="Filter by risk level (e.g., 'Normal', 'High')"),
    search: Optional[str] = Query(None, description="Search by coin pair (e.g., 'BTCUSDT')"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """
    Get new trading signals with optional filters.
    Requires authentication.
    """
    query = {}
    if risk_level:
        query['risk_level'] = {"$regex": risk_level, "$options": "i"} # Case-insensitive
    if search:
        query['coin_pair'] = {"$regex": search, "$options": "i"} # Case-insensitive search
        
    signals = await NewSignal.find(query).sort(-NewSignal.timestamp).limit(limit).to_list()
    return signals