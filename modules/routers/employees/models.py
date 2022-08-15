import hashlib
import typing

from pydantic import BaseModel


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: str = "Success"


class Employee(BaseModel):
    rfid_card_id: str
    name: str
    position: str
    passport_code: str | None = None

    async def compose(self) -> str:
        return " ".join([self.rfid_card_id, self.name, self.position])

    async def encode_sha256(self) -> str:
        employee_passport_string: str = await self.compose()
        employee_passport_string_encoded: bytes = employee_passport_string.encode()
        employee_passport_code: str = hashlib.sha256(employee_passport_string_encoded).hexdigest()
        return employee_passport_code


class EncodedEmployee(BaseModel):
    encoded_name: str


class EmployeesOut(GenericResponse):
    count: int
    data: list[Employee] | None


class EmployeeOut(GenericResponse):
    employee: Employee | None
