import re

from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from courses.forms import CourseForm
from courses.models import Course
from employees.models import Employee
from enrollments.models import Enrollment


def courses(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    courses_list = Course.objects.annotate(
        active_count=Count(
            "enrollments",
            filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
        )
    ).order_by("title")
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


def course_detail(request: HttpRequest, slug: str) -> HttpResponse:
    # Страница курса открывается по слагу, а не по числовому id
    course = get_object_or_404(Course, slug=slug)
    # Обратная связь related_name="enrollments": активные назначения курса
    active_enrollments = (
        course.enrollments.active()
        .select_related("employee")
        .order_by("deadline")
    )
    context = {
        "course": course,
        "active_enrollments": active_enrollments,
    }
    return render(request, "courses/course_detail.html", context)


def course_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # request.FILES нужен для загрузки обложки
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            return redirect(course.get_absolute_url())
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})


def available_courses(request: HttpRequest) -> HttpResponse:
    employees = Employee.objects.order_by("full_name")
    employee_id = request.GET.get("employee", "").strip()
    courses_list = Course.objects.none()
    error = None
    if employee_id:
        if employee_id.isdigit() and Employee.objects.filter(pk=int(employee_id)).exists():
            # Курсы, на которые у сотрудника есть активное назначение
            assigned_course_ids = (
                Enrollment.objects.active()
                .filter(employee_id=int(employee_id))
                .values_list("course_id", flat=True)
            )
            courses_list = (
                Course.objects.exclude(pk__in=assigned_course_ids)
                .annotate(
                    active_count=Count(
                        "enrollments",
                        filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                    )
                )
                .order_by("title")
            )
        else:
            error = "Выберите сотрудника из списка."
    context = {
        "employees": employees,
        "employee_id": employee_id,
        "courses": courses_list,
        "error": error,
    }
    return render(request, "courses/available.html", context)
