import typing
from datetime import timedelta

import httpx
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from yaml import YAMLError

from ...dependencies.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token
from ...exceptions import (
    AuthException,
    ConnectionTimeoutException,
    IncorrectAddressException,
    ParserException,
    UnhandledException,
)
from ...utils import load_yaml
from .models import Token

router = APIRouter()


@router.get("/api/v1/status")
async def get_server_status() -> dict[str, str]:
    """Endpoint to get server status"""
    return {"status": "ok"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), keep_session: bool = True) -> dict[str, str]:
    """
    Endpoint for user-auth

    Returns bearer jwt token
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed to login user {form_data.username}")
        raise AuthException
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if keep_session:
        access_token_expires = timedelta(hours=1024)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/v1/ipfs_decode")
async def parse_ipfs_link(link: str) -> typing.Any:
    """Extracts saved passport from IPFS/Pinata"""
    if not link.startswith(("http://", "https://")):
        raise IncorrectAddressException

    try:
        async with httpx.AsyncClient() as client:
            request = await client.get(link)
            return await load_yaml(request.text)
    except httpx.ReadTimeout:
        raise ConnectionTimeoutException
    except YAMLError:
        raise ParserException
    except Exception as exception:
        raise UnhandledException(error=exception)


@router.get("/api/v1/validate")
async def validate_stages() -> list[bool]:
    pass
