from datetime import date, timedelta

from enrollments import (
    calculate_status,
    cancel_enrollment,
    create_enrollment,
    is_course_available,
)


def test_is_course_available_when_empty():
    assert is_course_available([], employee_id=1, course_id=1)


def test_create_enrollment():
    enrollments = []
    deadline = date.today() + timedelta(days=7)
    enrollment = create_enrollment(enrollments, 1, 1, deadline, 20)
    assert enrollment is not None
    assert len(enrollments) == 1


def test_duplicate_enrollment_forbidden():
    enrollments = []
    deadline = date.today() + timedelta(days=7)
    create_enrollment(enrollments, 1, 1, deadline, 20)
    duplicate = create_enrollment(enrollments, 1, 1, deadline, 20)
    assert duplicate is None


def test_cancel_enrollment_frees_course():
    enrollments = []
    deadline = date.today() + timedelta(days=7)
    enrollment = create_enrollment(enrollments, 1, 1, deadline, 20)
    cancel_enrollment(enrollments, enrollment["id"])
    assert is_course_available(enrollments, 1, 1)


def test_calculate_status_not_finished():
    assert "не все уроки" in calculate_status(90, True, False)


def test_calculate_status_success():
    assert "отлично" in calculate_status(95, True, True)
