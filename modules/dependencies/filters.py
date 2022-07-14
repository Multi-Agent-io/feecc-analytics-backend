import datetime
import typing as tp


from modules.routers.tcd.models import ProtocolStatus
from modules.routers.passports.models import UnitStatus
from ..types import Filter


async def parse_passports_filter(
    status: tp.Optional[UnitStatus] = None,
    name: tp.Optional[str] = None,
    date: tp.Optional[datetime.datetime] = None,
    types: tp.Optional[str] = None,
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
        types_array: tp.List[str] = types.split(",")
        clear_filter["types"] = {"$in": types_array}

    if status:
        clear_filter["status"] = status

    return clear_filter


async def parse_tcd_filters(
    status: tp.Optional[ProtocolStatus] = None,
    name: tp.Optional[str] = None,
    date: tp.Optional[datetime.datetime] = None,
) -> Filter:
    clear_filter: Filter = {}

    if status:
        clear_filter["status"] = status

    if name:
        clear_filter["default_serial_number"] = {"$regex": name}

    if date is not None:
        start, end = date.replace(hour=0, minute=0, second=0), date.replace(hour=23, minute=59, second=59)
        clear_filter["creation_time"] = {"$lt": end, "$gte": start}

    return clear_filter
