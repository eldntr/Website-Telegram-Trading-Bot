# backend/app/db/database.py
import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import settings
from app.db.models import User, UserConfiguration, NewSignal, Trade # <-- Ditambahkan

async def init_db():
    """
    Initializes the database connection and Beanie ODM.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    
    # Ping server untuk memastikan koneksi berhasil
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

    database = client[settings.MONGO_DB_NAME]
    
    await init_beanie(
        database=database,
        document_models=[
            User,
            UserConfiguration,
            NewSignal, # <-- Ditambahkan
            Trade      # <-- Ditambahkan
        ]
    )