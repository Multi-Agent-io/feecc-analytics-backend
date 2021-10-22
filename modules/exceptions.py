import typing as tp

from fastapi import HTTPException, status
from loguru import logger
from starlette.status import HTTP_408_REQUEST_TIMEOUT


class AuthException(HTTPException):
    """Exception caused by authorization failure"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Incorrect username or password"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class CredentialsValidationException(HTTPException):
    """Exception caused by credentials (login/pass) validation"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class ConnectionTimeoutException(HTTPException):
    """Connection timed out"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_408_REQUEST_TIMEOUT
        self.detail = "Timeout"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class IncorrectAddressException(HTTPException):
    """Exception caused by calling parsing on non ipfs/pinata instance"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Can't parse given address. It must starts with http(s)://"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class ParserException(HTTPException):
    """Exception caused by parsing on non yaml-like file"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = "Can't parse given document. Looks like it's not YAML-like"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class UnhandledException(HTTPException):
    """An unhandled exception occurred"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = f"An error occured: {kwargs.get('error', None) or 'unhandled'}"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class ForbiddenActionException(HTTPException):
    """An unhandled exception occurred"""

    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = f"insufficient permissions for current user"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")
