import typing
from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from ..stages.models import ProductionStageData


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class UnitStatus(str, Enum):
    production = "production"
    built = "built"
    revision = "revision"
    approved = "approved"
    finalized = "finalized"


class Passport(BaseModel):
    schema_id: str
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    internal_id: str
    passport_short_url: str | None
    passport_ipfs_cid: str | None = None
    is_in_db: bool | None = None
    featured_in_int_id: str | None
    biography: list[ProductionStageData] | None
    components_internal_ids: list[str] | None
    model: str | None = None
    date: datetime = Field(default_factory=lambda: datetime.now(), alias="creation_time")
    type: str | None = None
    parential_unit: str | None = None
    serial_number: str | None = None
    status: UnitStatus | None = None
    txn_hash: str | None = None


class PassportsOut(GenericResponse):
    count: int
    data: list[Passport]


class PassportOut(GenericResponse):
    passport: Passport | None


class TypesOut(GenericResponse):
    data: list[str]


class OrderBy(str, Enum):
    descending = "asc"
    ascending = "desc"
