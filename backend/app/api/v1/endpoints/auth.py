# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.user import UserCreate, UserOut, Token
from app.db.models import User, UserConfiguration

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    """
    Registers a new user in the system.
    """
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    hashed_pwd = hash_password(user_in.password)
    new_user = User(email=user_in.email, password_hash=hashed_pwd)
    await new_user.insert()

    # Create default configuration for the new user
    default_config = UserConfiguration(user_id=new_user.id)
    await default_config.insert()
    
    # We need to manually convert the ObjectId to a string for the Pydantic model
    user_dict = new_user.dict()
    user_dict['_id'] = str(user_dict['_id'])
    return UserOut(**user_dict)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}