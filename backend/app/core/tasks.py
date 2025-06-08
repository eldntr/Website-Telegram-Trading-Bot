# backend/app/core/tasks.py
import asyncio
from typing import Dict
from beanie.odm.operators.update.general import Set
from datetime import datetime

from app.core.trader import AdaptedTradingStrategy, AdaptedTrader
from app.core.security import decrypt_data
from app.db.models import User, NewSignal, Trade, UserConfiguration
from app.binance.client import BinanceClient
from app.core.websockets import manager # <-- Import manager

# Dictionary untuk melacak task yang sedang berjalan untuk mencegah duplikasi
running_tasks: Dict[str, asyncio.Task] = {}

async def monitor_signal_for_entry(user_id: str, signal_id: str):
    """
    Background task untuk memantau sinyal hingga kondisi masuk terpenuhi atau kedaluwarsa.
    """
    task_id = f"{user_id}_{signal_id}"
    print(f"Memulai pemantauan untuk task: {task_id}")

    user = await User.get(user_id)
    signal = await NewSignal.get(signal_id)
    config = await UserConfiguration.find_one(UserConfiguration.user_id.id == user.id)

    if not all([user, signal, config]):
        print(f"Data tidak lengkap untuk task {task_id}. Menghentikan.")
        del running_tasks[task_id]
        return

    # Dekripsi kunci API
    try:
        api_key = decrypt_data(user.binance_api_key_encrypted)
        api_secret = decrypt_data(user.binance_api_secret_encrypted)
    except Exception as e:
        print(f"Gagal mendekripsi kunci API untuk user {user.email}: {e}")
        del running_tasks[task_id]
        return
        
    client = BinanceClient(api_key, api_secret)
    strategy = AdaptedTradingStrategy(client)
    trader = AdaptedTrader(client, config.usdt_per_trade)

    while True:
        # Cek apakah task masih seharusnya berjalan
        if task_id not in running_tasks:
            print(f"Task {task_id} dihentikan secara eksternal.")
            break
            
        is_valid, reason = strategy.evaluate_signal_for_entry(signal)
        print(f"[Task: {task_id}] Evaluasi: {is_valid}, Alasan: {reason}")
        
        if is_valid:
            print(f"Kondisi masuk untuk {signal.coin_pair} terpenuhi. Mengeksekusi trade...")
            execution_result = trader.execute_trade(signal)
            
            if execution_result.get("status") == "SUCCESS":
                print(f"Trade untuk {signal.coin_pair} berhasil dieksekusi.")
                # Buat dokumen trade baru di database
                new_trade = Trade(
                    user_id=user.id,
                    signal_id=signal.id,
                    symbol=signal.coin_pair,
                    status='ACTIVE',
                    entry_price=execution_result.get('entry_price'),
                    quantity=execution_result.get('quantity'),
                    buy_order_details=execution_result.get('buy_order'),
                    # Simpan orderListId dari OCO untuk tracking
                    sell_order_details=execution_result.get('oco_order'),
                    buy_fee=execution_result.get('buy_fee')
                )
                await new_trade.insert()
                
                await manager.send_personal_message(
                    {
                        "type": "TRADE_OPENED",
                        "data": {
                            "symbol": signal.coin_pair,
                            "entry_price": execution_result.get('entry_price')
                        }
                    },
                    user_id
                )
                print(f"Trade baru untuk {signal.coin_pair} disimpan ke DB.")
            else:
                print(f"Eksekusi trade GAGAL: {execution_result.get('reason')}")
            
            # Hentikan task setelah eksekusi (berhasil atau gagal)
            break
        
        # Hentikan jika alasan invalid bukan karena harga belum tercapai
        if not is_valid and "masih di atas Harga Entri" not in reason:
            print(f"Sinyal {signal.coin_pair} tidak lagi valid. Menghentikan pemantauan.")
            break
            
        await asyncio.sleep(60) # Tunggu 1 menit sebelum cek lagi

    # Hapus task dari daftar setelah selesai
    if task_id in running_tasks:
        del running_tasks[task_id]
    print(f"Pemantauan untuk task {task_id} selesai.")


async def periodic_check_open_trades():
    """
    Job periodik yang berjalan di background untuk memeriksa status semua trade 'ACTIVE'.
    """
    while True:
        print("\n--- [Job Periodik] Memeriksa status trade yang terbuka ---")
        active_trades = await Trade.find(Trade.status == 'ACTIVE').to_list()
        
        if not active_trades:
            print("Tidak ada trade aktif yang perlu diperiksa.")
        else:
            print(f"Ditemukan {len(active_trades)} trade aktif untuk diperiksa.")
        
        for trade in active_trades:
            try:
                user = await User.get(trade.user_id.id)
                if not user: continue

                api_key = decrypt_data(user.binance_api_key_encrypted)
                api_secret = decrypt_data(user.binance_api_secret_encrypted)
                client = BinanceClient(api_key, api_secret)

                order_list_id = trade.sell_order_details.get("orderListId", -1)
                
                # Cek status order OCO
                order_status = client._send_request("GET", "/orderList", {"orderListId": order_list_id}, signed=True)
                
                # Jika order sudah tidak ada (tereksekusi atau dibatalkan)
                if not order_status or order_status.get('listStatusType') in ['DONE', 'ALL_DONE']:
                    print(f"Trade {trade.symbol} untuk user {user.email} terdeteksi tertutup.")
                    
                    # Dapatkan detail trade penjualan dari riwayat
                    sell_trade_details = client._send_request("GET", "/myTrades", {"symbol": trade.symbol, "limit": 10}, signed=True)
                    
                    if sell_trade_details:
                        # Cari trade penjualan terakhir yang relevan
                        last_sell = sorted([t for t in sell_trade_details if not t['isBuyer']], key=lambda x: x['time'], reverse=True)
                        if last_sell:
                            final_sell = last_sell[0]
                            exit_price = float(final_sell['price'])
                            sell_fee = float(final_sell['commission'])
                            
                            # Hitung P/L
                            net_pl = (exit_price - trade.entry_price) * trade.quantity - (trade.buy_fee + sell_fee)
                            
                            # Tentukan status akhir
                            stop_loss_order = next((o for o in trade.sell_order_details['orders'] if 'STOP_LOSS' in o.get('type','')), None)
                            final_status = 'CLOSED_SL' if stop_loss_order and exit_price <= float(stop_loss_order.get('price')) else 'CLOSED_TP'

                            update_data = {
                                "status": final_status,
                                "exit_price": exit_price,
                                "sell_fee": sell_fee,
                                "net_profit_loss": net_pl,
                                "closed_at": datetime.utcnow()
                            }
                            await trade.update(Set(update_data))
                            
                            await manager.send_personal_message(
                                {
                                    "type": "TRADE_CLOSED",
                                    "data": {
                                        "symbol": trade.symbol,
                                        "status": final_status,
                                        "net_profit_loss": net_pl
                                    }
                                },
                                str(trade.user_id.id)
                            )
                            print(f"Trade {trade.symbol} berhasil ditutup dan diperbarui di DB. P/L: {net_pl:.4f}")
                        else:
                             print(f"Tidak dapat menemukan detail penjualan untuk {trade.symbol}")
                    else:
                        print(f"Gagal mengambil riwayat trade untuk {trade.symbol}")
            except Exception as e:
                print(f"Error saat memeriksa trade {trade.id} untuk user {trade.user_id.id}: {e}")
                continue # Lanjut ke trade berikutnya jika ada error

        await asyncio.sleep(300) # Tunggu 5 menit sebelum siklus berikutnya