# backend/app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.db.models import User, Trade
from app.schemas.dashboard import DashboardSummary
from app.core.security import decrypt_data
from app.core.account import AdaptedAccountManager
from app.binance.client import BinanceClient

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """
    Mengambil data ringkasan teragregasi untuk dasbor pengguna.
    """
    # 1. Agregasi data dari database
    pipeline = [
        {
            "$match": {
                "user_id": current_user.id,
                "status": {"$in": ["CLOSED_TP", "CLOSED_SL", "CLOSED_MANUAL"]},
                "net_profit_loss": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_net_pl": {"$sum": "$net_profit_loss"},
                "total_trades_closed": {"$sum": 1},
                "winning_trades": {
                    "$sum": {
                        "$cond": [{"$gte": ["$net_profit_loss", 0]}, 1, 0]
                    }
                }
            }
        }
    ]
    
    aggregation_result = await Trade.aggregate(pipeline).to_list(1)
    
    if aggregation_result:
        summary = aggregation_result[0]
        total_trades = summary['total_trades_closed']
        winning_trades = summary['winning_trades']
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        db_summary = {
            "total_net_pl": summary.get('total_net_pl', 0),
            "total_trades_closed": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2)
        }
    else:
        # Default jika tidak ada riwayat trade
        db_summary = {
            "total_net_pl": 0, "total_trades_closed": 0, "winning_trades": 0, 
            "losing_trades": 0, "win_rate": 0
        }

    # 2. Ambil nilai portofolio dari Binance
    portfolio_value = None
    portfolio_error = None
    if current_user.binance_api_key_encrypted:
        try:
            api_key = decrypt_data(current_user.binance_api_key_encrypted)
            api_secret = decrypt_data(current_user.binance_api_secret_encrypted)
            client = BinanceClient(api_key, api_secret)
            manager = AdaptedAccountManager(client)
            portfolio_summary = manager.get_account_summary()
            if portfolio_summary:
                portfolio_value = portfolio_summary.get('total_balance_usdt')
        except Exception as e:
            print(f"Error fetching portfolio value for user {current_user.email}: {e}")
            portfolio_error = "Could not fetch portfolio value from Binance. Check your API keys."
    else:
        portfolio_error = "Binance API keys are not set."

    # 3. Gabungkan hasil dan kembalikan
    return DashboardSummary(
        **db_summary,
        current_portfolio_value=portfolio_value,
        portfolio_error=portfolio_error
    )