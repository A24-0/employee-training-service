"""Класс Employee и функции для работы с коллекцией сотрудников."""

from typing import List, Optional


class Employee:
    """Сотрудник компании."""

    def __init__(
        self,
        employee_id: int,
        full_name: str,
        department: str,
    ) -> None:
        """Создать объект сотрудника."""
        self.id = employee_id
        self.full_name = full_name
        self.department = department

    @classmethod
    def from_data(cls, data: dict) -> "Employee":
        """Создать сотрудника из набора данных (например, из JSON)."""
        return cls(data["id"], data["full_name"], data["department"])

    def __str__(self) -> str:
        """Вернуть строковое представление сотрудника."""
        return f"[{self.id}] {self.full_name} ({self.department})"


def add_employee(
    employees: List[Employee],
    full_name: str,
    department: str,
) -> Employee:
    """Создать объект Employee и добавить его в коллекцию."""
    employee_id = max((e.id for e in employees), default=0) + 1
    employee = Employee(employee_id, full_name, department)
    employees.append(employee)
    return employee


def find_employee(employees: List[Employee], query: str) -> List[Employee]:
    """Найти сотрудников по подстроке имени."""
    query = query.lower()
    return [e for e in employees if query in e.full_name.lower()]


def find_employee_by_id(
    employees: List[Employee],
    employee_id: int,
) -> Optional[Employee]:
    """Найти сотрудника по идентификатору."""
    for employee in employees:
        if employee.id == employee_id:
            return employee
    return None


def show_employees(employees: List[Employee]) -> None:
    """Вывести список сотрудников."""
    if not employees:
        print("Сотрудники не найдены")
        return
    for employee in employees:
        print(employee)
