from employees import add_employee, find_employee, find_employee_by_id


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
    found = find_employee_by_id(employees, employee["id"])
    assert found is employee
