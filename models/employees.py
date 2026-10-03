from typing import List, Optional


class Employee:

    def __init__(
        self,
        employee_id: int,
        full_name: str,
        department: str,
    ) -> None:
        self.id = employee_id
        self.full_name = full_name
        self.department = department

    @classmethod
    def from_data(cls, data: dict) -> "Employee":
        return cls(data["id"], data["full_name"], data["department"])

    def __str__(self) -> str:
        return f"[{self.id}] {self.full_name} ({self.department})"


def add_employee(
    employees: List[Employee],
    full_name: str,
    department: str,
) -> Employee:
    employee_id = max((e.id for e in employees), default=0) + 1
    employee = Employee(employee_id, full_name, department)
    employees.append(employee)
    return employee


def find_employee(employees: List[Employee], query: str) -> List[Employee]:
    query = query.lower()
    return [e for e in employees if query in e.full_name.lower()]


def find_employee_by_id(
    employees: List[Employee],
    employee_id: int,
) -> Optional[Employee]:
    for employee in employees:
        if employee.id == employee_id:
            return employee
    return None


def show_employees(employees: List[Employee]) -> None:
    if not employees:
        print("Сотрудники не найдены")
        return
    for employee in employees:
        print(employee)
