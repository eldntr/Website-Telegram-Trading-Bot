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
    # BARU: Menambahkan status apakah kunci API sudah diatur atau belum
    has_binance_keys: bool = False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
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