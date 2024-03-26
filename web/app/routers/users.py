from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..utils import hash_password, verify_password
from ..auth import create_access_token


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    """Register user account"""
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    user.password = hash_password(user.password)
    user_obj = models.User(**user.dict())
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {
        **user_obj.__dict__,
        "token": {
            "access_token": create_access_token(user_id=user_obj.id),
        }
    }


@router.post("/login", status_code=status.HTTP_200_OK)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> schemas.Token:
    """Login with email and password"""
    user_obj = db.query(models.User).filter(models.User.email == credentials.username).first()
    if user_obj and verify_password(plain=credentials.password, hashed=user_obj.password):
        return {
            "access_token": create_access_token(user_id=user_obj.id),
            "type": "bearer"
        }
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
