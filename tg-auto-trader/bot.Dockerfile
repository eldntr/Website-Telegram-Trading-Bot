# Auto Trade Bot/bot.Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Salin file requirements.txt dan instal dependensi
COPY tg-auto-trader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi direktori tg-auto-trader ke dalam /app
COPY tg-auto-trader/ .

# Pindah ke direktori tg-auto-trader dan jalankan perintah autoloop
CMD ["sh", "-c", "cd tg-auto-trader && python main.py autoloop --limit 20 --initial-limit 200 --delay 300 --duration 0"]