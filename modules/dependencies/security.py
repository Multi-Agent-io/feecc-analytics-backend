import os
import typing
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from modules.database import MongoDbWrapper
from modules.exceptions import CredentialsValidationException, ForbiddenActionException
from modules.models import User
from modules.routers.employees.models import Employee
from modules.routers.service.models import TokenData
from modules.routers.users.models import NewUser, UserWithPassword

SECRET_KEY = os.environ.get("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def create_access_token(
    data: dict[str, datetime | str],
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str) -> UserWithPassword | None:
    user_data = await MongoDbWrapper().get_concrete_user(username)
    if not user_data:
        return None
    if not verify_password(password, user_data.hashed_password):
        return None
    return user_data


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsValidationException
        token_data = TokenData(username=username)
    except JWTError:
        raise CredentialsValidationException
    user: UserWithPassword | None = await MongoDbWrapper().get_concrete_user(username=token_data.username)
    if user is None:
        raise CredentialsValidationException
    return User(**dict(user))


async def check_user_permissions(user: User = Depends(get_current_user)) -> None:
    if "write" not in user.rule_set:
        raise ForbiddenActionException


async def check_tcd_permissions(user: User = Depends(get_current_user)) -> None:
    if "approve" not in user.rule_set:
        raise ForbiddenActionException


async def create_new_user(user: NewUser) -> UserWithPassword:
    """New user's creation and validation of credentials fields"""
    if len(user.password) < 8:
        raise CredentialsValidationException(details="Password length less than 8 symbols")
    if len(user.username) < 4:
        raise CredentialsValidationException(details="Username length less than 4 symbols")
    return UserWithPassword(
        username=user.username, rule_set=user.rule_set, hashed_password=get_password_hash(user.password)
    )


async def get_current_employee(user: User = Depends(get_current_user)) -> Employee | None:
    if not user.associated_employee:
        return None
    return await MongoDbWrapper().get_concrete_employee(card_id=user.associated_employee)
