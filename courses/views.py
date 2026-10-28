import re

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from courses.models import Course
from employees.models import Employee
from enrollments.models import Enrollment


def courses(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    courses_list = Course.objects.order_by("title")
    if query:
        # Поиск без учёта регистра сразу по двум строковым полям.
        # В SQLite icontains не учитывает регистр только для латиницы,
        # поэтому для кириллицы используется iregex с экранированным вводом
        pattern = re.escape(query)
        courses_list = courses_list.filter(
            Q(title__iregex=pattern) | Q(category__iregex=pattern)
        )
    context = {
        "courses": courses_list,
        "query": query,
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request: HttpRequest, course_id: int) -> HttpResponse:
    course = get_object_or_404(Course, pk=course_id)
    # Обратная связь related_name="enrollments": активные назначения курса
    active_enrollments = (
        course.enrollments
        .filter(is_cancelled=False)
        .select_related("employee")
        .order_by("deadline")
    )
    context = {
        "course": course,
        "active_enrollments": active_enrollments,
    }
    return render(request, "courses/course_detail.html", context)


def available_courses(request: HttpRequest) -> HttpResponse:
    employees = Employee.objects.order_by("full_name")
    employee_id = request.GET.get("employee", "").strip()
    courses_list = Course.objects.none()
    error = None
    if employee_id:
        if employee_id.isdigit() and Employee.objects.filter(pk=int(employee_id)).exists():
            # Курсы, на которые у сотрудника есть активное назначение
            assigned_course_ids = Enrollment.objects.filter(
                employee_id=int(employee_id),
                is_cancelled=False,
            ).values_list("course_id", flat=True)
            courses_list = Course.objects.exclude(
                pk__in=assigned_course_ids,
            ).order_by("title")
        else:
            error = "Выберите сотрудника из списка."
    context = {
        "employees": employees,
        "employee_id": employee_id,
        "courses": courses_list,
        "error": error,
    }
    return render(request, "courses/available.html", context)
