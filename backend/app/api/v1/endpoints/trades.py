# backend/app/api/v1/endpoints/trades.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List

from app.api.dependencies import get_current_user
from app.core.tasks import monitor_signal_for_entry, running_tasks
from app.db.models import User, NewSignal, Trade
from app.schemas.trade import TradeActivate, TradeOut
from app.core.security import decrypt_data
from app.binance.client import BinanceClient

router = APIRouter()

@router.get("/", response_model=List[TradeOut])
async def get_trades(
    status: str = 'ACTIVE', # Default untuk mendapatkan trade aktif
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar trade pengguna, bisa difilter berdasarkan status.
    """
    trades = await Trade.find(
        Trade.user_id.id == current_user.id,
        Trade.status == status.upper()
    ).to_list()

    # Konversi manual untuk response model
    response = []
    for trade in trades:
        trade_dict = trade.dict()
        trade_dict['_id'] = str(trade.id)
        trade_dict['user_id'] = str(trade.user_id.id)
        response.append(trade_dict)
    return response

@router.post("/activate", status_code=status.HTTP_202_ACCEPTED)
async def activate_trade_monitoring(
    trade_in: TradeActivate,
    current_user: User = Depends(get_current_user)
):
    """
    Memicu pemantauan sinyal di background untuk dieksekusi.
    """
    signal = await NewSignal.get(trade_in.signal_id)
    if not signal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found.")

    # Cek apakah sudah ada trade aktif untuk sinyal ini oleh user ini
    existing_trade = await Trade.find_one(
        Trade.user_id.id == current_user.id,
        Trade.symbol == signal.coin_pair,
        Trade.status == 'ACTIVE'
    )
    if existing_trade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You already have an active trade for {signal.coin_pair}.")

    task_id = f"{current_user.id}_{signal.id}"
    if task_id in running_tasks:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Monitoring for this signal is already active.")

    # Jalankan task di background
    task = asyncio.create_task(monitor_signal_for_entry(str(current_user.id), str(signal.id)))
    running_tasks[task_id] = task
    
    return {"message": "Signal monitoring activated in the background."}

@router.post("/{trade_id}/close-manual", response_model=TradeOut)
async def close_trade_manually(
    trade_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Menutup trade yang aktif secara manual dengan market sell.
    """
    trade = await Trade.get(trade_id)
    if not trade or str(trade.user_id.id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found or you do not have permission.")
    
    if trade.status != 'ACTIVE':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trade is not active.")

    api_key = decrypt_data(current_user.binance_api_key_encrypted)
    api_secret = decrypt_data(current_user.binance_api_secret_encrypted)
    client = BinanceClient(api_key, api_secret)

    order_list_id = trade.sell_order_details.get("orderListId", -1)
    
    # 1. Batalkan OCO order yang ada
    print(f"Membatalkan OCO {order_list_id} untuk {trade.symbol}...")
    client.cancel_oco_order(symbol=trade.symbol, order_list_id=order_list_id)
    await asyncio.sleep(1) # Jeda singkat

    # 2. Lakukan Market Sell
    print(f"Melakukan market sell untuk {trade.quantity} {trade.symbol}...")
    sell_result = client.place_market_sell_order(symbol=trade.symbol, quantity=trade.quantity)
    if not sell_result or sell_result.get('status') != 'FILLED':
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to execute market sell on Binance.")

    # 3. Hitung biaya dan P/L, lalu update DB
    exit_price = float(sell_result['cummulativeQuoteQty']) / float(sell_result['executedQty'])
    sell_fee = sum(float(f['commission']) for f in sell_result.get('fills', []))
    net_pl = (exit_price - trade.entry_price) * trade.quantity - (trade.buy_fee + sell_fee)
    
    update_data = {
        "status": "CLOSED_MANUAL",
        "exit_price": exit_price,
        "sell_order_details": sell_result,
        "sell_fee": sell_fee,
        "net_profit_loss": net_pl,
        "closed_at": datetime.utcnow()
    }
    await trade.update(Set(update_data))

    updated_trade = await Trade.get(trade.id)
    trade_dict = updated_trade.dict()
    trade_dict['_id'] = str(updated_trade.id)
    trade_dict['user_id'] = str(updated_trade.user_id.id)
    return trade_dict