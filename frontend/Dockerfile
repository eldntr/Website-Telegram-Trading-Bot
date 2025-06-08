# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Salin package.json dan package-lock.json terlebih dahulu untuk caching layer
COPY package*.json ./
RUN npm install

# Salin sisa kode aplikasi
COPY . .

# Expose port yang digunakan oleh Next.js
EXPOSE 3000

# Jalankan server development
CMD ["npm", "run", "dev"]