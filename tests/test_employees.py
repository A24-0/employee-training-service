from models import Employee
from models.employees import add_employee, find_employee, find_employee_by_id


def test_employee_creation():
    employee = Employee(1, "Иванов Иван Иванович", "Отдел контроля качества")
    assert employee.id == 1
    assert employee.full_name == "Иванов Иван Иванович"
    assert employee.department == "Отдел контроля качества"


def test_add_employee():
    employees = []
    add_employee(employees, "Иванов Иван Иванович", "Отдел контроля качества")
    assert len(employees) == 1


def test_find_employee():
    employees = []
    add_employee(employees, "Иванов Иван Иванович", "Отдел контроля качества")
    assert find_employee(employees, "иванов")


def test_find_employee_by_id():
    employees = []
    employee = add_employee(employees, "Петров Пётр", "Отдел продаж")
    found = find_employee_by_id(employees, employee.id)
    assert found is employee
