import datetime
import typing

from modules.routers.passports.models import UnitStatus
from modules.routers.tcd.models import ProtocolStatus

from ..types import Filter


async def parse_passports_filter(
    status: UnitStatus | None = None,
    name: str | None = None,
    date: datetime.datetime | None = None,
    types: str | None = None,
) -> Filter:
    clear_filter: Filter = {}

    if name is not None:
        if "url.today" in name:
            clear_filter["passport_short_url"] = name
        elif len(name) == 32:
            clear_filter["uuid"] = name
        elif len(name) == 13 and name.isnumeric():
            clear_filter["internal_id"] = name
        else:
            clear_filter["name"] = {"$regex": name}

    if date is not None:
        start, end = date.replace(hour=0, minute=0, second=0), date.replace(hour=23, minute=59, second=59)
        clear_filter["creation_time"] = {"$lt": end, "$gte": start}

    if types is not None:
        types_array: list[str] = types.split(",")
        clear_filter["types"] = {"$in": types_array}

    if status:
        clear_filter["status"] = status

    return clear_filter


async def parse_tcd_filters(
    status: ProtocolStatus | None = None,
    name: str | None = None,
    date: datetime.datetime | None = None,
) -> Filter:
    clear_filter: Filter = {}

    if status:
        clear_filter["status"] = status

    if name:
        clear_filter["$or"] = [{"protocol_name": {"$regex": name}, "default_serial_number": {"$regex": name}}]

    if date is not None:
        start, end = date.replace(hour=0, minute=0, second=0), date.replace(hour=23, minute=59, second=59)
        clear_filter["creation_time"] = {"$lt": end, "$gte": start}

    return clear_filter
