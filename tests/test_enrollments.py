from datetime import date, timedelta

from models import Course, Employee
from models.enrollments import (
    Enrollment,
    cancel_enrollment,
    create_enrollment,
    is_course_available,
)


def make_course() -> Course:
    return Course(1, "Основы Python", "Разработка", 10)


def make_employee() -> Employee:
    return Employee(1, "Иванов Иван Иванович", "Отдел контроля качества")


def test_is_course_available_when_empty():
    assert is_course_available([], make_employee(), make_course())


def test_create_enrollment():
    enrollments = []
    deadline = date.today() + timedelta(days=7)
    enrollment = create_enrollment(
        enrollments, make_employee(), make_course(), deadline, 20
    )
    assert enrollment is not None
    assert len(enrollments) == 1


def test_duplicate_enrollment_forbidden():
    enrollments = []
    employee = make_employee()
    course = make_course()
    deadline = date.today() + timedelta(days=7)
    create_enrollment(enrollments, employee, course, deadline, 20)
    duplicate = create_enrollment(enrollments, employee, course, deadline, 20)
    assert duplicate is None


def test_cancel_enrollment_frees_course():
    enrollments = []
    employee = make_employee()
    course = make_course()
    deadline = date.today() + timedelta(days=7)
    enrollment = create_enrollment(enrollments, employee, course, deadline, 20)
    cancel_enrollment(enrollments, enrollment.id)
    assert is_course_available(enrollments, employee, course)


def test_enrollment_str_and_composition():
    enrollment = Enrollment(
        1, make_course(), make_employee(), date.today(), 20
    )
    assert enrollment.course.title in str(enrollment)
    assert enrollment.employee.full_name in str(enrollment)


def test_calculate_status_not_finished():
    assert "не все уроки" in Enrollment.calculate_status(90, True, False)


def test_calculate_status_success():
    assert "отлично" in Enrollment.calculate_status(95, True, True)


def test_enrollment_status_uses_progress():
    deadline = date.today() + timedelta(days=7)
    enrollment = Enrollment(1, make_course(), make_employee(), deadline, 20)
    enrollment.record_progress(10, 18)
    assert "отлично" in enrollment.status()
