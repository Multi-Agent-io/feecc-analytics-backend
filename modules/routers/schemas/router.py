import typing

from fastapi import APIRouter, Depends

from modules.database import MongoDbWrapper
from modules.dependencies.security import check_user_permissions, get_current_user
from modules.exceptions import DatabaseException

from .models import GenericResponse, ProductionSchema, ProductionSchemaOut, ProductionSchemasOut

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=ProductionSchemasOut | GenericResponse)  # type:ignore
async def get_all_production_schemas(page: int = 1, items: int = 20) -> ProductionSchemasOut:
    """
    Endpoint to get all production schemas.
    Pagination:
        page: number of page (default 1);
        items: number of items on single page (default 20);
    """
    try:
        schemas_count = await MongoDbWrapper().count_schemas()
        schemas = await MongoDbWrapper().get_all_schemas()
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return ProductionSchemasOut(count=schemas_count, data=schemas[(page - 1) * items : page * items])


@router.get("/{schema_id}", response_model=ProductionSchemasOut | GenericResponse)  # type:ignore
async def get_concrete_production_schema(schema_id: str) -> ProductionSchemaOut | GenericResponse:
    """
    Endpoint to get concrete production schema by its schema_id field or null if not exists
    """
    try:
        schema = await MongoDbWrapper().get_concrete_schema(schema_id)
    except ValueError as e:
        return GenericResponse(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise DatabaseException(error=e)
    return ProductionSchemaOut(prod_schema=schema)


@router.post("/", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def create_new_production_schema(schema: ProductionSchema) -> GenericResponse:
    """
    Endpoint to create new production schema.
    don't send "schema_id" field, it'll be overridden!
    """
    try:
        await MongoDbWrapper().add_schema(schema)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail=f"Created new schema with id {schema.schema_id}")


@router.delete("/{schema_id}", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def delete_production_schema(schema_id: str) -> GenericResponse:
    """
    Endpoint to delete single production schema by its schema_id field
    """
    try:
        await MongoDbWrapper().remove_schema(schema_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted schema")


@router.patch("/{schema_id}", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def edit_production_schema(schema_id: str, new_schema: ProductionSchema) -> GenericResponse:
    """
    Endpoint to edit production schemas You're now unable to edit such fields as: "schema_id", "parent_schema_id",
    "required_components_schema_ids", but you may send them anyways, backend will remove it
    """
    try:
        await MongoDbWrapper().edit_schema(schema_id, new_schema)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Patched schema")
