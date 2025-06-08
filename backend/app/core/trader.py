# backend/app/core/trader.py
import time
from typing import Dict, Any, Tuple
from binance.client import BinanceClient
from app.db.models import NewSignal

class AdaptedTradingStrategy:
    """
    Mengadaptasi strategi dari bot orisinal untuk digunakan dalam API.
    """
    def __init__(self, binance_client: BinanceClient):
        self.client = binance_client

    def evaluate_signal_for_entry(self, signal: NewSignal) -> Tuple[bool, str]:
        """
        Mengevaluasi apakah kondisi untuk masuk pasar terpenuhi.
        Mengembalikan (True, "Alasan") jika valid, (False, "Alasan") jika tidak.
        """
        coin_pair = signal.coin_pair
        entry_price = signal.entry_price

        if not coin_pair or entry_price is None:
            return (False, "Sinyal tidak memiliki coin_pair atau entry_price.")

        current_price = self.client.get_current_price(coin_pair)
        if current_price is None:
            return (False, f"Gagal mendapatkan harga terkini untuk {coin_pair}.")

        # Cek apakah harga sudah jatuh di bawah SL
        try:
            stop_loss_price = signal.stop_losses[0]['price']
            if current_price < stop_loss_price:
                return (False, f"Harga saat ini ({current_price}) sudah di bawah SL1 ({stop_loss_price}).")
        except (IndexError, KeyError, TypeError):
            return (False, "Data Stop Loss 1 tidak ditemukan pada sinyal.")
        
        if current_price <= entry_price:
            return (True, f"Kondisi masuk terpenuhi: Harga saat ini ({current_price}) <= Harga Entri ({entry_price}).")
        else:
            return (False, f"Harga saat ini ({current_price}) masih di atas Harga Entri ({entry_price}).")


class AdaptedTrader:
    """
    Mengadaptasi logika eksekusi trade.
    """
    def __init__(self, client: BinanceClient, usdt_per_trade: float):
        self.client = client
        self.usdt_per_trade = usdt_per_trade

    def execute_trade(self, signal: NewSignal) -> Dict[str, Any]:
        """
        Mengeksekusi pembelian dan menempatkan order OCO.
        Mengembalikan dictionary yang berisi hasil eksekusi.
        """
        coin_pair = signal.coin_pair
        base_asset = coin_pair.replace("USDT", "")

        print(f"Memulai proses pembelian untuk {coin_pair}...")
        buy_order = self.client.place_market_buy_order(symbol=coin_pair, quote_order_qty=self.usdt_per_trade)
        
        if not buy_order or buy_order.get('status') != 'FILLED':
            return {"status": "FAIL", "reason": "Market buy order gagal dieksekusi.", "details": buy_order}

        # Ekstrak detail dari order yang terisi
        initial_filled_qty = float(buy_order['executedQty'])
        avg_price = float(buy_order['cummulativeQuoteQty']) / initial_filled_qty
        
        # Hitung biaya dari 'fills'
        buy_fee = 0.0
        fee_asset = ''
        if 'fills' in buy_order and buy_order['fills']:
            for fill in buy_order['fills']:
                buy_fee += float(fill['commission'])
            fee_asset = buy_order['fills'][0]['commissionAsset']
        
        print(f"Berhasil membeli {initial_filled_qty:.6f} {base_asset} @ ~${avg_price:.4f}")
        print(f"Total Biaya Pembelian: {buy_fee} {fee_asset}")

        time.sleep(2) # Beri waktu agar balance di Binance terupdate

        try:
            tp_price = signal.targets[3]['price']  # Gunakan TP4 sebagai target akhir
            sl_price = signal.stop_losses[0]['price']
        except (IndexError, KeyError):
            return {"status": "CRITICAL_FAIL", "reason": "Data TP4 atau SL1 tidak ditemukan pada sinyal.", "buy_order": buy_order}
            
        print(f"Menempatkan OCO Order: TP=${tp_price}, SL=${sl_price}")
        oco_order = self.client.place_oco_sell_order(
            symbol=coin_pair,
            quantity=initial_filled_qty, # Gunakan kuantitas yang sudah dibeli
            take_profit_price=tp_price,
            stop_loss_price=sl_price
        )

        if not oco_order:
            return {"status": "CRITICAL_FAIL", "reason": "Aset berhasil dibeli tetapi GAGAL menempatkan OCO.", "buy_order": buy_order}
        
        return {
            "status": "SUCCESS",
            "reason": "Pembelian dan penempatan OCO berhasil.",
            "buy_order": buy_order,
            "oco_order": oco_order,
            "buy_fee": buy_fee,
            "fee_asset": fee_asset,
            "entry_price": avg_price,
            "quantity": initial_filled_qty,
        }