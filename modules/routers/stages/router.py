import typing

from fastapi import APIRouter, Depends

from ...database import MongoDbWrapper
from ...dependencies.security import check_user_permissions, get_current_user
from ...exceptions import DatabaseException
from .models import GenericResponse, ProductionStage, ProductionStageOut, ProductionStagesOut

router = APIRouter(dependencies=[Depends(get_current_user)], deprecated=True)


@router.get("/", response_model=ProductionStagesOut | GenericResponse)  # type:ignore
async def get_production_stages(page: int = 1, items: int = 20, decode_employees: bool = False) -> ProductionStagesOut:
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_stages(uuid="Deprecated")
    documents_count = await MongoDbWrapper().count_stages()
    try:
        if decode_employees:
            for stage in stages:
                if not isinstance(stage.employee_name, str):
                    continue
                stage.employee_name = await MongoDbWrapper().decode_employee(stage.employee_name)  # type: ignore
        return ProductionStagesOut(count=documents_count, data=stages[(page - 1) * items : page * items])
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)


@router.post("/", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_stage(stage: ProductionStage) -> GenericResponse:
    try:
        await MongoDbWrapper().add_stage(stage)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new production stage")


@router.delete("/{stage_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def remove_stage(stage_id: str) -> GenericResponse:
    try:
        await MongoDbWrapper().remove_stage(stage_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail=f"Deleted stage with id {stage_id}")


@router.get("/{stage_id}", response_model=typing.Union[ProductionStageOut, GenericResponse])  # type:ignore
async def get_stage_by_id(stage_id: str) -> ProductionStageOut | GenericResponse:
    """Endpoint to get information about concrete production stage"""
    try:
        stage = await MongoDbWrapper().get_concrete_stage(stage_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    if stage is None:
        return GenericResponse(status_code=404, detail="Not found")
    return ProductionStageOut(stage=stage)


@router.patch(
    "/{stage_id}",
    response_model=GenericResponse,
    dependencies=[Depends(check_user_permissions)],
)
async def patch_stage(stage_id: str, new_data: ProductionStage) -> GenericResponse:
    """
    Endpoint to edit production stages. You're unable to edit such fields as:
    "parent_unit_uuid","session_start_time","session_end_time","id","is_in_db","creation_time".
    But you may send "string" anyways, backend will remove it before update in db.
    """
    try:
        await MongoDbWrapper().edit_stage(stage_id=stage_id, new_stage_data=new_data)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully patched stage")
