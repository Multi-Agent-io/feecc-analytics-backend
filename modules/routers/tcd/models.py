from __future__ import annotations

import enum
import typing
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from ..employees.models import Employee


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class ProtocolStatus(str, enum.Enum):
    first = "Первая стадия испытаний пройдена"
    second = "Вторая стадия испытаний пройдена"
    third = "Протокол утверждён"

    @typing.no_type_check
    async def switch(self) -> ProtocolStatus:
        if self.value == self.first:
            return ProtocolStatus(self.second.value)
        return self

    @property
    async def is_approved(self) -> bool:
        return bool(self.value == self.third)


class ProtocolRow(BaseModel):
    name: str
    value: str
    deviation: str | None = None
    test1: str | None
    test2: str | None
    checked: bool = False


class Protocol(BaseModel):
    protocol_name: str
    protocol_schema_id: str
    associated_with_schema_id: str
    default_serial_number: str | None
    rows: list[ProtocolRow]


class TemplateProtocolsList(BaseModel):
    protocols: list[Protocol]


class ProtocolData(Protocol):
    protocol_id: str = Field(default_factory=lambda: uuid4().hex)
    associated_unit_id: str
    status: ProtocolStatus = ProtocolStatus.first
    creation_time: datetime = Field(default_factory=datetime.now)
    ipfs_cid: str | None = None
    txn_hash: str | None = None


class ProtocolOut(GenericResponse):
    serial_number: str | None
    employee: Employee | None
    protocol: ProtocolData | Protocol | TemplateProtocolsList


class ProtocolsOut(GenericResponse):
    count: int
    data: list[ProtocolData | Protocol]


class TypesOut(GenericResponse):
    data: list[str]


class IPFSGatewayResponse(BaseModel):
    status: int
    details: str
    ipfs_cid: str | None = None
    ipfs_link: str | None = None


class PendingProtocolsOut(GenericResponse):
    count: int
    pending: list[str]
