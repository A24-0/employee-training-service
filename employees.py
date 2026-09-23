"""Функции для работы с сотрудниками."""

from typing import List, Optional


def add_employee(employees: List[dict], full_name: str, department: str) -> dict:
    """Создать сотрудника и добавить его в коллекцию."""
    employee_id = max((e["id"] for e in employees), default=0) + 1
    employee = {
        "id": employee_id,
        "full_name": full_name,
        "department": department,
    }
    employees.append(employee)
    return employee


def find_employee(employees: List[dict], query: str) -> List[dict]:
    """Найти сотрудников по подстроке имени."""
    query = query.lower()
    return [e for e in employees if query in e["full_name"].lower()]


def find_employee_by_id(
    employees: List[dict],
    employee_id: int,
) -> Optional[dict]:
    """Найти сотрудника по идентификатору."""
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None


def show_employees(employees: List[dict]) -> None:
    """Вывести список сотрудников."""
    if not employees:
        print("Сотрудники не найдены")
        return
    for employee in employees:
        print(
            f"[{employee['id']}] {employee['full_name']} "
            f"({employee['department']})"
        )
