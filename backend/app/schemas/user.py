# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --- User Schemas ---

# Properti untuk membuat user baru (registrasi)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

# Properti untuk ditampilkan ke client (tanpa password)
class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    created_at: datetime
    has_binance_keys: bool = False

    class Config:
        from_attributes = True  # <-- Diubah
        validate_by_name = True # <-- Diubah
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# --- BARU: Skema untuk memperbarui kunci Binance ---
class BinanceKeysUpdate(BaseModel):
    api_key: str = Field(..., min_length=10)
    api_secret: str = Field(..., min_length=10)


# --- Token Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None