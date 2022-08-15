from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class ProductionSchemaStage(BaseModel):
    name: str
    type: str | None = None
    description: str | None = None
    equipment: list[str] | None = None
    workplace: str | None = None
    duration_seconds: int | None = None
    stage_id: str


class ProductionSchema(BaseModel):
    schema_id: str = Field(default_factory=lambda: uuid4().hex)
    unit_name: str
    production_stages: list[ProductionSchemaStage] | None = None
    required_components_schema_ids: list[str] | None = None
    parent_schema_id: str | None = None
    schema_type: str

    # async def prepare_data(self) -> ProductionSchema:
    #     """Generate new sensitive data for schema"""
    #     return


class ProductionSchemasOut(GenericResponse):
    count: int
    data: list[ProductionSchema]


class ProductionSchemaOut(GenericResponse):
    prod_schema: ProductionSchema | None
