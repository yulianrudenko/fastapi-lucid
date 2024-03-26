from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.selectors import get_user
from .db import get_db
from .config import settings
from . import models


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_MINUTES = 60 * 24 * 7
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(user_id: str | int) ->str:
    expires_at = datetime.now() + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    data = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(data, key=SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception
    user_id: str = payload.get("sub")
    if user_id is not None:
        user = get_user(id=user_id, db=db)
        if user is not None:
            return user
    raise credentials_exception
