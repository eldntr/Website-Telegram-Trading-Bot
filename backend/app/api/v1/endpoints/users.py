# backend/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from beanie.odm.operators.update.general import Set

from app.schemas.user import UserOut, BinanceKeysUpdate
from app.db.models import User
from app.api.dependencies import get_current_user
from app.core.security import encrypt_data # <-- Import fungsi enkripsi

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    """
    user_dict = current_user.dict()
    user_dict['_id'] = str(user_dict['_id'])
    # Tambahkan field 'has_binance_keys' ke response
    user_dict['has_binance_keys'] = bool(current_user.binance_api_key_encrypted and current_user.binance_api_secret_encrypted)
    return UserOut(**user_dict)

# --- Endpoint Baru ---
@router.put("/me/binance-keys", status_code=status.HTTP_200_OK)
async def update_binance_keys(
    keys_in: BinanceKeysUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Add or update the user's Binance API keys securely.
    The keys will be encrypted before being stored.
    """
    try:
        # Enkripsi kunci API dan Secret
        encrypted_api_key = encrypt_data(keys_in.api_key)
        encrypted_api_secret = encrypt_data(keys_in.api_secret)

        # Update data pengguna di database
        update_data = {
            "binance_api_key_encrypted": encrypted_api_key,
            "binance_api_secret_encrypted": encrypted_api_secret
        }
        await current_user.update(Set(update_data))

        return {"message": "Binance API keys updated successfully."}
    except Exception as e:
        # Tangani kemungkinan error saat enkripsi atau update DB
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating keys: {e}"
        )