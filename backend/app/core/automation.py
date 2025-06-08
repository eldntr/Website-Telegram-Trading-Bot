# backend/app/core/automation.py
import asyncio
from datetime import datetime, timedelta
from app.db.models import User, UserConfiguration, NewSignal, Trade
from app.core.tasks import monitor_signal_for_entry, running_tasks

async def run_user_autotrade_cycle(user_id: str):
    """
    Menjalankan satu siklus autotrade penuh untuk satu pengguna:
    1. Baca sinyal baru dari DB.
    2. Evaluasi sinyal mana yang potensial.
    3. Aktifkan pemantauan untuk sinyal yang valid.
    """
    user = await User.get(user_id)
    config = await UserConfiguration.find_one(UserConfiguration.user_id.id == user.id)

    if not config or not config.autotrade_enabled:
        print(f"[Autotrade Cycle] Otomatisasi tidak aktif untuk user {user.email}. Melewatkan.")
        return

    print(f"[Autotrade Cycle] Memulai siklus untuk user: {user.email}")

    # 1. Dapatkan sinyal terbaru dari DB
    time_filter = datetime.utcnow() - timedelta(minutes=config.signal_validity_minutes)
    recent_signals = await NewSignal.find(
        NewSignal.timestamp >= time_filter
    ).sort(-NewSignal.timestamp).to_list()
    
    if not recent_signals:
        print(f"[Autotrade Cycle] Tidak ada sinyal baru ditemukan untuk {user.email}.")
        return

    # 2. Dapatkan trade aktif dan task pemantauan yang sedang berjalan untuk pengguna ini
    active_trades = await Trade.find(Trade.user_id.id == user.id, Trade.status == 'ACTIVE').to_list()
    active_symbols = {trade.symbol for trade in active_trades}
    
    user_running_tasks = {key for key in running_tasks if key.startswith(str(user.id))}

    print(f"[Autotrade Cycle] User {user.email} memiliki {len(active_symbols)} posisi aktif dan {len(user_running_tasks)} task pemantauan.")

    # 3. Evaluasi dan aktifkan sinyal
    for signal in recent_signals:
        # Jangan proses jika sudah punya posisi aktif untuk koin tersebut
        if signal.coin_pair in active_symbols:
            continue
            
        # Jangan proses jika sudah ada task pemantauan untuk sinyal tersebut
        task_id = f"{user_id}_{signal.id}"
        if task_id in running_tasks:
            continue
            
        # Di sini kita tidak mengevaluasi harga, karena itu tugas `monitor_signal_for_entry`.
        # Kita hanya memvalidasi apakah sinyal ini layak untuk dipantau.
        # Contoh: filter berdasarkan risk level jika ada di konfigurasi
        if config.prioritize_normal_risk and signal.risk_level and signal.risk_level.lower() != 'normal':
             # Jika mode prioritas normal aktif, lewati sinyal berisiko tinggi
             print(f"[Autotrade Cycle] Melewatkan sinyal {signal.coin_pair} (risk: {signal.risk_level}) untuk {user.email} karena mode prioritas normal.")
             continue

        print(f"[Autotrade Cycle] Mengaktifkan pemantauan untuk sinyal {signal.coin_pair} bagi user {user.email}")
        
        # Jalankan task pemantauan di background
        task = asyncio.create_task(monitor_signal_for_entry(str(user.id), str(signal.id)))
        running_tasks[task_id] = task

    print(f"[Autotrade Cycle] Siklus untuk user {user.email} selesai.")