import os
from fastapi import APIRouter, BackgroundTasks, Depends
from loguru import logger

from modules.models import User
from modules.routers.employees.models import Employee
from modules.routers.tcd.utils import post_ipfs_cid_to_datalog, push_to_ipfs_gateway
from ..passports.models import OrderBy

from ...database import MongoDbWrapper
from ...dependencies.filters import parse_tcd_filters
from ...dependencies.handlers import handle_protocol
from ...dependencies.security import get_current_employee, get_current_user
from ...exceptions import DatabaseException
from ...types import Filter
from .models import GenericResponse, PendingProtocolsOut, Protocol, ProtocolData, ProtocolOut, ProtocolsOut, TypesOut

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/protocols", response_model=ProtocolsOut)
async def get_protocols(
    page: int = 1,
    items: int = 20,
    filter: Filter = Depends(parse_tcd_filters),
    sort_by_date: OrderBy = OrderBy.ascending,
) -> ProtocolsOut:
    """
    Endpoint to get all issued protocols from database.
    You can't receive empty protocol templates here
    """
    try:
        protocols = await MongoDbWrapper().get_all_protocols(filter=filter)
        protocols_count = len(protocols)

        if sort_by_date == "asc":
            protocols.reverse()
        protocols = protocols[(page - 1) * items : page * items]

    except Exception as exception_message:
        logger.warning(f"Can't get all protocols from DB. Filter: {filter}")
        raise DatabaseException(error=exception_message) from exception_message
    return ProtocolsOut(count=protocols_count, data=protocols[(page - 1) * items : page * items])


@router.get("/protocols/types")
async def get_protocols_types() -> TypesOut:
    """Endpoint to get all possible protocol stages (types)"""
    types = ["Первая стадия испытаний пройдена", "Вторая стадия испытаний пройдена", "Протокол утверждён"]
    return TypesOut(data=types)


@router.get("/protocols/pending", response_model=PendingProtocolsOut)
async def get_pending_protocols() -> PendingProtocolsOut:
    """Get lists of all protocols ids pending approval"""
    try:
        pending = [protocol.protocol_id for protocol in await MongoDbWrapper().get_pending_protocols()]
    except Exception as exception_message:
        logger.error(f"Can't get pending protocols. {exception_message}")
        raise DatabaseException(detail=exception_message) from exception_message
    return PendingProtocolsOut(count=len(pending) if pending else 0, pending=pending)


@router.get("/protocols/{internal_id}")
async def get_concrete_protocol(internal_id: str, employee: Employee = Depends(get_current_employee)) -> ProtocolOut:
    """
    Endpoint to get information about concrete protocol.
    If unit don't have issued passport, it'll return empty protocol template.
    Otherwise, you'll get filled protocol from database.
    """
    protocol: Protocol | ProtocolData | None
    try:
        protocol = await MongoDbWrapper().get_concrete_protocol(internal_id=internal_id)
        unit = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
        if not unit:
            raise DatabaseException(detail=f"Unit with {internal_id} not found. Can't generate protocol for it")
        if not protocol:
            protocol = await MongoDbWrapper().get_concrete_protocol_prototype(associated_with_schema_id=unit.schema_id)
        if not protocol:
            raise DatabaseException(detail="Can't create protocol for unit {internal_id}, missing schema")
    except Exception as exception_message:
        logger.warning(f"Can't get protocol for unit {internal_id}, exc: {exception_message}")
        raise DatabaseException(detail=exception_message) from exception_message
    return ProtocolOut(serial_number=unit.serial_number, employee=employee, protocol=protocol)


@router.post("/protocols/{internal_id}", response_model=GenericResponse)
async def handle_protocol_update(protocol: ProtocolData = Depends(handle_protocol)) -> GenericResponse:
    """
    Endpoint to handle protocol events. If unit don't have issued protocol, it'll be created
    Otherwise, it'll be edited. Be careful, you can't edit immutable (approved) protocol,
    you need to delete it first.
    """
    try:
        await MongoDbWrapper().process_protocol(internal_id=protocol.associated_unit_id, data=protocol)
    except Exception as exception_message:
        logger.error(f"Can't process protocol for unit {protocol.associated_unit_id}. Exception: {exception_message}")
        logger.debug(f"Protocol: {protocol}")
        raise DatabaseException(detail=exception_message) from exception_message
    return GenericResponse()


@router.post("/protocols/{internal_id}/approve", response_model=GenericResponse)
async def approve_protocol(
    internal_id: str, background_tasks: BackgroundTasks, user: User = Depends(get_current_user)
) -> GenericResponse:
    """Endpoint to approve protocol (if unit already passed any checks)"""
    try:
        await MongoDbWrapper().approve_protocol(internal_id=internal_id)
        protocol = await MongoDbWrapper().get_concrete_protocol(internal_id=internal_id)
        if not protocol:
            raise ValueError(f"Protocol {internal_id} not found")
        if eval(os.getenv("USE_DATALOG", "False")):
            response = await push_to_ipfs_gateway(protocol=protocol, username=user.username)
            if ipfs_hash := response.ipfs_cid:
                background_tasks.add_task(post_ipfs_cid_to_datalog, internal_id, ipfs_hash)
    except Exception as exception_message:
        logger.error(f"Can't approve protocol for unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(detail=exception_message)

    return GenericResponse()


@router.delete("/protocols/{internal_id}", response_model=GenericResponse)
async def remove_protocol(internal_id: str) -> GenericResponse:
    """Endpoint to remove existing protocol information"""
    try:
        await MongoDbWrapper().remove_protocol(internal_id=internal_id)
    except Exception as exception_message:
        logger.error(f"Can't remove protocol for unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(detail=exception_message)
    return GenericResponse()
