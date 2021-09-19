import os
import typing as tp
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from modules.exceptions import CredentialsValidationException

from .models import TokenData, User

SECRET_KEY = os.environ.get("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
fake_users = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$fBRc/pmRElhwnZ/MWdFny.CHk4yszGLOET5iI4yWUcztUybRwzewq",
        "is_admin": True,
    }
}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(username: str):
    if username in fake_users:
        user_dict = fake_users[username]
        return User(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    logger.info(f"got token {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(payload)
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsValidationException
        token_data = TokenData(username=username)
    except JWTError:
        raise CredentialsValidationException
    user: User = get_user(username=token_data.username)
    if user is None:
        raise CredentialsValidationException
    logger.info(f"user: {user}")
    return user
