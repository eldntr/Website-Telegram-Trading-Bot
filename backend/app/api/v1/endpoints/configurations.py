# backend/app/api/v1/endpoints/configurations.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.api.dependencies import get_current_user
from app.db.models import User, UserConfiguration
from app.schemas.configuration import ConfigurationOut, ConfigurationUpdate

router = APIRouter()

@router.get("/", response_model=ConfigurationOut)
async def get_configuration(current_user: User = Depends(get_current_user)):
    """
    Get the trading configuration for the current user.
    """
    config = await UserConfiguration.find_one(UserConfiguration.user_id.id == current_user.id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found.")
    
    # Konversi Link ke string ID untuk response model
    config_dict = config.dict()
    config_dict['user_id'] = str(config.user_id.id)
    return config_dict


@router.put("/", response_model=ConfigurationOut)
async def update_configuration(
    config_in: ConfigurationUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update the trading configuration for the current user.
    """
    config = await UserConfiguration.find_one(UserConfiguration.user_id.id == current_user.id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found.")
        
    update_data = config_in.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided.")
        
    update_data['updated_at'] = datetime.utcnow()
    
    await config.update({"$set": update_data})
    
    # Muat ulang data yang sudah diupdate untuk respons
    updated_config = await UserConfiguration.get(config.id)
    updated_config_dict = updated_config.dict()
    updated_config_dict['user_id'] = str(updated_config.user_id.id)
    return updated_config_dict