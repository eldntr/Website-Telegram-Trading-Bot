# backend/app/core/account.py
from typing import Dict, Any, Optional
from binance.client import BinanceClient

class AdaptedAccountManager:
    """
    Mengelola fungsionalitas terkait akun Binance untuk API.
    """
    STABLECOINS = {'USDT', 'BUSD', 'USDC', 'DAI', 'TUSD'}

    def __init__(self, client: BinanceClient):
        self.client = client

    def get_account_summary(self) -> Optional[Dict[str, Any]]:
        """
        Menghasilkan ringkasan akun, termasuk aset yang dipegang dan total nilai dalam USDT.
        """
        account_info = self.client.get_account_info()
        if not account_info or 'balances' not in account_info:
            print("Gagal mendapatkan informasi akun atau 'balances' tidak ditemukan.")
            return None
            
        all_tickers = self.client.get_all_tickers()
        if not all_tickers:
            print("Gagal mengambil harga ticker. Tidak dapat menghitung total nilai.")
            return {"held_assets": [], "total_balance_usdt": 0.0, "error": "Gagal mengambil harga ticker."}

        # Konversi list ticker menjadi dictionary untuk lookup yang lebih cepat
        ticker_prices = {item['symbol']: float(item['price']) for item in all_tickers}

        total_balance_usdt = 0.0

        for asset in account_info['balances']:
            asset_name = asset['asset']
            total_balance = float(asset['free']) + float(asset['locked'])

            if total_balance > 0:
                asset_value_usdt = 0.0
                if asset_name in self.STABLECOINS:
                    asset_value_usdt = total_balance
                else:
                    ticker_usdt = f"{asset_name}USDT"
                    if ticker_usdt in ticker_prices:
                        price_usdt = ticker_prices[ticker_usdt]
                        asset_value_usdt = total_balance * price_usdt
                
                if asset_value_usdt > 0.01:
                    total_balance_usdt += asset_value_usdt
        
        return {
            "total_balance_usdt": round(total_balance_usdt, 2)
        }