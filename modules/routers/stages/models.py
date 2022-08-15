from __future__ import annotations

import typing
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class ProductionStage(BaseModel):
    name: str
    employee_name: str | None = None
    parent_unit_uuid: str
    session_start_time: str | None
    session_end_time: str | None
    ended_prematurely: bool
    video_hashes: list[str] | None = []
    additional_info: dict[typing.Any, typing.Any] | None
    id: str = Field(default_factory=lambda: uuid4().hex)
    is_in_db: bool | None
    creation_time: datetime
    schema_stage_id: str | None

    completed: bool | None
    number: int | None

    async def clear(self, number: int) -> ProductionStage:
        return ProductionStage(
            name=self.name,
            parent_unit_uuid=self.parent_unit_uuid,
            ended_prematurely=False,
            is_in_db=True,
            creation_time=datetime.now(),
            session_start_time=None,
            session_end_time=None,
            completed=False,
            number=number,
            additional_info={"reworked": True},
            schema_stage_id=self.schema_stage_id,
        )


class ProductionStageData(ProductionStage):
    unit_name: str | None
    parent_unit_internal_id: str | None


class ProductionStagesOut(GenericResponse):
    count: int
    data: list[ProductionStage]


class ProductionStageOut(GenericResponse):
    stage: ProductionStage | None
