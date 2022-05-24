from __future__ import annotations

import typing as tp
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class ProductionStage(BaseModel):
    name: str
    employee_name: tp.Optional[str]
    parent_unit_uuid: str
    session_start_time: tp.Optional[str]
    session_end_time: tp.Optional[str]
    ended_prematurely: bool
    video_hashes: tp.Optional[tp.List[str]]
    additional_info: tp.Optional[tp.Dict[tp.Any, tp.Any]]
    id: str = Field(default_factory=lambda: uuid4().hex)
    is_in_db: tp.Optional[bool]
    creation_time: datetime
    schema_stage_id: tp.Optional[str]

    completed: tp.Optional[bool]
    number: tp.Optional[int]

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
    unit_name: tp.Optional[str]
    parent_unit_internal_id: tp.Optional[str]


class ProductionStagesOut(GenericResponse):
    count: int
    data: tp.List[ProductionStage]


class ProductionStageOut(GenericResponse):
    stage: tp.Optional[ProductionStage]
