import typing as tp
from datetime import datetime
from uuid import uuid4
from enum import Enum

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
    passport_short_url: tp.Optional[str]
    passport_ipfs_cid: tp.Optional[str] = None
    is_in_db: tp.Optional[bool] = None
    featured_in_int_id: tp.Optional[str]
    biography: tp.Optional[tp.List[ProductionStageData]]
    components_internal_ids: tp.Optional[tp.List[str]]
    model: tp.Optional[str] = None
    date: datetime = Field(default_factory=lambda: datetime.now(), alias="creation_time")
    type: tp.Optional[str] = None
    parential_unit: tp.Optional[str] = None
    serial_number: tp.Optional[str] = None
    status: tp.Optional[UnitStatus] = None
    txn_hash: tp.Optional[str] = None


class PassportsOut(GenericResponse):
    count: int
    data: tp.List[Passport]


class PassportOut(GenericResponse):
    passport: tp.Optional[Passport]


class TypesOut(GenericResponse):
    data: tp.List[str]


class OrderBy(str, Enum):
    descending = "asc"
    ascending = "desc"
