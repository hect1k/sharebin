from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.database import get_db
from app.models.models import User
from app.services import user_service


def get_db_dep():
    yield from get_db()


settings = Settings()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db_dep),
) -> Optional[User]:

    if token is None:
        return None

    credentials_exception = HTTPException(
        status_code=403,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = user_service.get_user_by_email(db, email)
    if not user:
        raise credentials_exception
    if not user.verified:
        raise HTTPException(status_code=401, detail="Please verify your email!")
    return user
