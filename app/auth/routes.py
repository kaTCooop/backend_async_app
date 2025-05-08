from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .dependencies import get_db, authenticate_user, create_access_token, get_user
from .token_models import Token
from .schemas import UserCreate, UserResponse
from .utils import get_password_hash  # Import get_password_hash here

from .database import models, meta, engine


User = models.UserBase
router = APIRouter()


@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup", response_model=UserResponse, include_in_schema=False)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Функция по сути не используется, но может быть использована для самостоятельной регистрации пользователя, без администратора
    db_user = get_user(db, username=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    hashed_password = get_password_hash(user.password)

    users = meta.tables['users']
    length = Session(bind=engine).scalar(select(func.count()).select_from(users))


    db_user = User(
        user_id=length + 1,
        email=user.email,
        password=hashed_password,
        full_name=user.full_name,
        user_type=0
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user = db_user.to_dict()
    return db_user
