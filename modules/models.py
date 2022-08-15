from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    username: str
    rule_set: list[str] = ["read"]
    associated_employee: str | None = None
