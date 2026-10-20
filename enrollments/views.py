from django.shortcuts import render

from models.enrollments import find_enrollment_by_id
from storage import load_courses, load_employees, load_enrollments

COURSES_FILE = "data/courses.json"
EMPLOYEES_FILE = "data/employees.json"
ENROLLMENTS_FILE = "data/enrollments.json"


def _load_enrollments():
    courses = load_courses(COURSES_FILE)
    employees = load_employees(EMPLOYEES_FILE)
    return load_enrollments(ENROLLMENTS_FILE, courses, employees)


def enrollments(request):
    context = {
        "enrollments": _load_enrollments(),
    }
    return render(request, "enrollments/enrollment_list.html", context)


def enrollment_detail(request, enrollment_id):
    enrollment = find_enrollment_by_id(_load_enrollments(), enrollment_id)
    context = {
        "enrollment": enrollment,
    }
    return render(
        request,
        "enrollments/enrollment_detail.html",
        context,
        status=404 if enrollment is None else 200,
    )
