import os
import time
import typing

import redis
from loguru import logger
from pydantic import BaseModel, parse_obj_as

from modules.routers.employees.models import Employee

from .singleton import SingletonMeta


class RedisCacher(metaclass=SingletonMeta):
    @logger.catch(reraise=True)
    def __init__(self) -> None:
        REDIS_HOST = os.environ.get("REDIS_HOST")
        if not REDIS_HOST:
            raise ConnectionError("REDIS_HOST not specified")

        self._client = redis.Redis(host=REDIS_HOST, socket_connect_timeout=3)

    async def _is_in_cache(self, query: tuple[str, str]) -> bool:
        """Check if query is available in cache"""
        return bool(self._client.exists(str(query)))

    async def _cache_to_redis(self, query: tuple[str, str], data: BaseModel) -> None:
        """Save employee data to redis"""
        ttl = 1000**2
        self._client.set(
            name=str(query),
            value=repr(data.dict()),
            exat=int(time.time()) + ttl,
        )
        logger.debug(f"Cached to redis. Set to expire after {ttl // 60}m.")

    async def _unpack_from_redis(self, query: tuple[str, str], model: type[BaseModel]) -> BaseModel | None:
        """Het data to redis"""
        cached_data = self._client.get(name=str(query))
        if not cached_data:
            return None
        data = eval(cached_data)
        logger.debug(f"Unpacked employee {data} from cache")
        return parse_obj_as(model, data)

    async def cache_employees(self, employees: typing.Iterable[Employee]) -> None:
        for employee in employees:
            employee_sha = await employee.encode_sha256()
            if not await self._is_in_cache(query=("employees", employee_sha)):
                await self._cache_to_redis(query=("employees", employee_sha), data=employee)

    async def get_employee(self, hashed_employee: str) -> Employee | None:
        query = ("employees", hashed_employee)

        if await self._is_in_cache(query=query):
            employee = await self._unpack_from_redis(query=query, model=Employee)
            return employee  # type:ignore
        return None
