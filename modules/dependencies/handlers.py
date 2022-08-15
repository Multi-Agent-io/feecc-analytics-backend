import typing

from fastapi import Depends
from loguru import logger

from modules.routers.tcd.models import Protocol, ProtocolData

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException, ForbiddenActionException
from ..models import User
from .security import get_current_user


async def handle_protocol(internal_id: str, protocol: Protocol, user: User = Depends(get_current_user)) -> ProtocolData:
    if "approve" not in user.rule_set:
        raise ForbiddenActionException(
            details=f"You don't have access to process protocols. Your ruleset: {user.rule_set}"
        )
    logger.info(f"Processing protocol for unit {internal_id} with {len(protocol.rows)} rows")

    passport = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
    if not passport:
        raise DatabaseException(details=f"Unit with id {internal_id} not found. Can't create protocol")

    latest_protocol = await MongoDbWrapper().get_concrete_protocol(internal_id=internal_id)
    if not latest_protocol:
        logger.debug(f"Creating new protocol for unit {internal_id}")
        return ProtocolData(**protocol.dict(), associated_unit_id=internal_id)

    logger.info(f"Found protocol for unit {internal_id}, status {latest_protocol.status}. Protocol will be updated")
    latest_protocol.rows = protocol.rows
    return latest_protocol


async def check_passport(internal_id: str) -> None:
    passport = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
    if not passport:
        # TODO: Create special exception for handling missing passports
        raise ValueError(f"Passport {internal_id} not found")
