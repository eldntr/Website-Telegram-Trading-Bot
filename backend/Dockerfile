# backend/Dockerfile

# Gunakan base image Python yang efisien
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Perbarui pip dan install dependensi
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi dari direktori 'backend' ke direktori kerja kontainer
COPY . /app

# Jalankan server Uvicorn. Host 0.0.0.0 membuatnya dapat diakses dari luar kontainer.
# --reload akan otomatis me-restart server jika ada perubahan kode, cocok untuk development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]