import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger

from modules.dependencies.handlers import check_passport

from ...database import MongoDbWrapper
from ...dependencies.filters import parse_passports_filter
from ...dependencies.security import check_user_permissions, get_current_employee, get_current_user
from ...exceptions import DatabaseException
from ...types import Filter
from ..employees.models import Employee
from .models import GenericResponse, OrderBy, Passport, PassportOut, PassportsOut, TypesOut

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=tp.Union[PassportsOut, GenericResponse])  # type:ignore
async def get_all_passports(
    page: int = 1,
    items: int = 20,
    sort_by_date: OrderBy = OrderBy.ascending,
    filters: Filter = Depends(parse_passports_filter),
) -> PassportsOut:
    """
    Endpoint to get list of all issued units from :start: to :limit:. By default, from 0 to 20.
    """
    logger.debug(f"Filter: {filters}, sorting by date {sort_by_date}")
    try:
        passports = await MongoDbWrapper().get_passports(filters)
        documents_count = len(passports)

        if sort_by_date == "asc":
            passports.reverse()
        passports = passports[(page - 1) * items : page * items]

        for passport in passports:
            schema = await MongoDbWrapper().get_concrete_schema(schema_id=passport.schema_id)
            passport.type = schema.schema_type
            passport.model = schema.unit_name or passport.model
            if schema.parent_schema_id:
                passport.parential_unit = (
                    await MongoDbWrapper().get_concrete_schema(schema_id=schema.parent_schema_id)
                ).unit_name
    except Exception as exception_message:
        logger.error(
            f"Failed to get units from page {page} (count: {items}, filter: {filters}). Exception: {exception_message}"
        )
        raise DatabaseException(error=exception_message)

    return PassportsOut(count=documents_count, data=passports)


@router.get(
    "/types",
    dependencies=[Depends(check_user_permissions)],
    response_model=tp.Union[TypesOut, GenericResponse],  # type:ignore
)
async def get_all_possible_types() -> TypesOut:
    try:
        types = await MongoDbWrapper().get_all_types()
        logger.debug(types)
    except Exception as exception_message:
        logger.error(f"Failed to get unit types from db: Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return TypesOut(data=list(types))


@router.post("/", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_passport(passport: Passport) -> GenericResponse:
    """Endpoint to create a new unit"""
    try:
        await MongoDbWrapper().add_passport(passport)
    except Exception as exception_message:
        logger.error(f"Failed to create new unit ({passport.dict()}). Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new unit")


@router.delete("/{internal_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def delete_passport(internal_id: str) -> GenericResponse:
    """Endpoint to delete an existing unit from database"""
    try:
        await MongoDbWrapper().remove_passport(internal_id)
    except Exception as exception_message:
        logger.error(f"Failed to delete unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted unit")


@router.get("/{internal_id}", response_model=tp.Union[PassportOut, GenericResponse])  # type:ignore
async def get_passport_by_internal_id(internal_id: str) -> tp.Union[PassportOut, GenericResponse]:
    """Endpoint to get information about concrete issued unit"""
    try:
        passport = await MongoDbWrapper().get_concrete_passport(internal_id)
        if passport is None:
            logger.error(f"Unknown unit {internal_id}")
            return GenericResponse(status_code=404, detail="Not found")

        schema = await MongoDbWrapper().get_concrete_schema(schema_id=passport.schema_id)
        passport.model = schema.unit_name or passport.model
        passport.type = schema.schema_type
        if schema.parent_schema_id:
            parential_unit = await MongoDbWrapper().get_concrete_schema(schema_id=schema.parent_schema_id)
            passport.parential_unit = parential_unit.unit_name

    except Exception as exception_message:
        logger.error(f"Failed to get unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return PassportOut(passport=passport)


@router.post("/{internal_id}/serial")
async def update_serial_number(internal_id: str, serial_number: str) -> GenericResponse:
    """
    Update passport's serial number
    """
    try:
        current_serial_number: tp.Optional[str] = await MongoDbWrapper().get_passport_serial_number(
            internal_id=internal_id
        )
        if current_serial_number != serial_number:
            await MongoDbWrapper().update_serial_number(internal_id=internal_id, serial_number=serial_number)

    except Exception as exception_message:
        logger.error(f"An error occured while updating serial number {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse()


@router.patch("/{internal_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def patch_passport(internal_id: str, new_data: Passport) -> GenericResponse:
    """
    Edit concrete unit data.
    Ignored fields: {"uuid", "internal_id", "is_in_db", "featured_in_int_id"}. Send null instead.
    """
    try:
        await MongoDbWrapper().edit_passport(internal_id=internal_id, new_passport_data=new_data)
    except Exception as exception_message:
        logger.error(f"Failed to patch unit {internal_id} with data {new_data.dict()}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully patched unit")


@router.post("/{internal_id}/revision", response_model=GenericResponse)
async def send_for_revision(internal_id: str, stages_ids: tp.List[str]) -> GenericResponse:
    """
    Endpoint to sent current unit for revision by selected stages ids.
    Empty copy of those stages will be created. Unit status will change to 'revision'.
    """
    logger.info(f"Sending unit {internal_id} for revision")
    try:
        await MongoDbWrapper().send_unit_for_revision(internal_id=internal_id, stage_ids=stages_ids)
        await MongoDbWrapper().update_passport_status(internal_id=internal_id, status="revision")
    except Exception as exception_message:
        logger.error(f"Failed to send unit {internal_id} for revision. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully sent unit for revision")


@router.post("/{internal_id}/revision/cancel", response_model=GenericResponse, dependencies=[Depends(check_passport)])
async def cancel_revision_stage(
    internal_id: str, stage_id: str, employee: tp.Optional[Employee] = Depends(get_current_employee)
) -> GenericResponse:
    """
    Endpoint to cancel revision for selected stages.
    If it's the only stage sent for revision, current unit will change its status to 'built',
    otherwise nothing will be changed
    """
    logger.info(f"Canceling revision for stage {stage_id} of unit {internal_id} by employee {employee or 'Unknown'}")
    try:
        await MongoDbWrapper().cancel_revision(stage_id=stage_id, employee=employee)
    except Exception as exception_message:
        logger.error(f"Failed to cancel revision for unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)

    return GenericResponse(detail=f"Marked stage {stage_id} as canceled")
