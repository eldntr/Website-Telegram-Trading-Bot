# backend/app/api/v1/endpoints/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.core.websockets import manager
from app.api.dependencies import get_current_user # Kita akan membuat fungsi baru untuk WS
from app.core.config import settings
from app.db.models import User
from jose import jwt, JWTError
from pydantic import ValidationError

router = APIRouter()

async def get_current_user_from_token(token: str = Query(...)) -> User:
    """
    Dependensi untuk otentikasi pengguna dari token di query param WebSocket.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
    except (JWTError, ValidationError):
        return None
        
    user = await User.find_one(User.email == email)
    return user


@router.websocket("/user-feed")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user = await get_current_user_from_token(token)
    if user is None:
        await websocket.close(code=1008)
        return

    user_id = str(user.id)
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Tetap terhubung, bisa ditambahkan logika untuk menerima pesan dari client jika perlu
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)