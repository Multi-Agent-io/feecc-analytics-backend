import typing as tp

from fastapi import APIRouter, Depends

from ...database import MongoDbWrapper
from ...dependencies.security import check_user_permissions, get_current_user
from ...exceptions import DatabaseException, NotFoundException
from .models import Employee, EmployeeOut, EmployeesOut, EncodedEmployee, GenericResponse

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=tp.Union[EmployeesOut, GenericResponse])  # type:ignore
async def get_all_employees(page: int = 1, items: int = 20) -> EmployeesOut:
    """
    Endpoint to get list of all employees from :start: to :limit:. By default, from 0 to 20.
    """
    employees = await MongoDbWrapper().get_all_employees()
    documents_count = await MongoDbWrapper().count_employees()
    return EmployeesOut(count=documents_count, data=employees[(page - 1) * items : page * items])


@router.post("/", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_employee(employee_data: Employee) -> GenericResponse:
    """Endpoint to create new employee"""
    try:
        employee_data.passport_code = await employee_data.encode_sha256()
        await MongoDbWrapper().add_employee(employee_data)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new employee")


@router.delete("/{rfid_card_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def delete_employee(rfid_card_id: str) -> GenericResponse:
    """Endpoint to delete employee from database"""
    try:
        await MongoDbWrapper().remove_employee(rfid_card_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail=f"Removed employee with card id {rfid_card_id}")


@router.get("/{rfid_card_id}", response_model=tp.Union[EmployeeOut, GenericResponse])  # type:ignore
async def get_employee_by_card_id(rfid_card_id: str) -> tp.Union[EmployeeOut, GenericResponse]:
    """Endpoint to get information about concrete employee by his rfid card id"""
    try:
        employee = await MongoDbWrapper().get_concrete_employee(card_id=rfid_card_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    if employee is None:
        raise NotFoundException(detail=f"Employee with id {rfid_card_id} not found")
    return EmployeeOut(employee=employee)


@router.patch("/{rfid_card_id}", response_model=GenericResponse)
async def patch_employee(rfid_card_id: str, new_data: Employee) -> GenericResponse:
    """Endpoint to edit employees."""
    try:
        await MongoDbWrapper().edit_employee(rfid_card_id=rfid_card_id, new_employee_data=new_data)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully patched employee")


@router.post("/decode", response_model=tp.Union[EmployeeOut, GenericResponse])  # type:ignore
async def decode_existing_employee(encoded_employee: EncodedEmployee) -> EmployeeOut:
    """Decode an employee by encoded name"""
    try:
        employee = await MongoDbWrapper().get_concrete_employee(passport_code=encoded_employee.encoded_name)
        if not employee:
            raise NotFoundException(
                detail=f"Employee with code {encoded_employee.encoded_name[:3]}...{encoded_employee.encoded_name[-3:]} not found",
            )
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return EmployeeOut(employee=employee)
