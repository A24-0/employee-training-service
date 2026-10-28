import re
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q
from django.db.models.functions import Round
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from courses.models import Course
from employees.models import Employee
from enrollments.models import Enrollment

PAGE_SIZE = 5

# Допустимые значения параметра sort и соответствующие поля модели:
# пользовательский ввод не передаётся в order_by() напрямую
SORT_FIELDS = {
    "deadline": "deadline",
    "-deadline": "-deadline",
    "course": "course__title",
    "employee": "employee__full_name",
}
DEFAULT_SORT = "deadline"


def enrollments(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    course_id = request.GET.get("course", "").strip()
    employee_id = request.GET.get("employee", "").strip()
    status = request.GET.get("status", "").strip()
    deadline = request.GET.get("deadline", "").strip()
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    error = None

    enrollments_list = Enrollment.objects.all()

    # Поиск по ФИО сотрудника — строковому полю связанной модели
    # (iregex вместо icontains — см. courses.views.courses)
    if query:
        enrollments_list = enrollments_list.filter(
            employee__full_name__iregex=re.escape(query),
        )
    # Фильтрация по внешним ключам
    if course_id.isdigit():
        enrollments_list = enrollments_list.filter(course_id=int(course_id))
    if employee_id.isdigit():
        enrollments_list = enrollments_list.filter(employee_id=int(employee_id))
    if status == "active":
        enrollments_list = enrollments_list.filter(is_cancelled=False)
    elif status == "cancelled":
        enrollments_list = enrollments_list.filter(is_cancelled=True)
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            enrollments_list = enrollments_list.filter(deadline__lte=deadline_date)

    # Названия курса и сотрудника берутся из связанных таблиц;
    # id добавлен в сортировку для стабильного порядка
    enrollments_list = (
        enrollments_list
        .annotate(
            course_title=F("course__title"),
            employee_name=F("employee__full_name"),
        )
        .order_by(SORT_FIELDS[sort], "id")
        .values(
            "id",
            "deadline",
            "is_cancelled",
            "course_title",
            "employee_name",
        )
    )

    paginator = Paginator(enrollments_list, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "enrollments": page_obj,
        "page_obj": page_obj,
        "query": query,
        "selected_course": course_id,
        "selected_employee": employee_id,
        "status": status,
        "deadline": deadline,
        "sort": sort,
        "courses": Course.objects.order_by("title"),
        "employees": Employee.objects.order_by("full_name"),
        "error": error,
    }
    return render(request, "enrollments/enrollment_list.html", context)


def enrollment_detail(request: HttpRequest, enrollment_id: int) -> HttpResponse:
    # Курс и сотрудник загружаются вместе с назначением одним запросом
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("course", "employee"),
        pk=enrollment_id,
    )
    context = {
        "enrollment": enrollment,
    }
    return render(request, "enrollments/enrollment_detail.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    summary = Course.objects.aggregate(
        courses_count=Count("id"),
        min_lessons=Min("total_lessons"),
        max_lessons=Max("total_lessons"),
        avg_lessons=Round(Avg("total_lessons"), 1),
    )
    active_count = Enrollment.objects.filter(is_cancelled=False).count()

    # Запрос строится от Course, поэтому курсы без назначений тоже попадают
    # в результат (аналог LEFT JOIN); отменённые назначения не считаются
    by_course = (
        Course.objects
        .annotate(
            course_title=F("title"),
            enrollments_count=Count(
                "enrollments",
                filter=Q(enrollments__is_cancelled=False),
            ),
        )
        .values("course_title", "enrollments_count")
        .order_by("-enrollments_count", "course_title")
    )
    # Группировка активных назначений по отделу сотрудника
    by_department = (
        Enrollment.objects
        .filter(is_cancelled=False)
        .values(department=F("employee__department"))
        .annotate(enrollments_count=Count("id"))
        .order_by("-enrollments_count", "department")
    )
    # Условие на результат агрегации (аналог HAVING)
    popular = by_course.filter(enrollments_count__gt=1)
    overdue = (
        Enrollment.objects
        .filter(
            is_cancelled=False,
            deadline__lt=timezone.localdate(),
            lessons_completed__lt=F("course__total_lessons"),
        )
        .annotate(
            employee_name=F("employee__full_name"),
            course_title=F("course__title"),
        )
        .values("id", "employee_name", "course_title", "deadline")
        .order_by("deadline")
    )
    context = {
        "summary": summary,
        "active_count": active_count,
        "by_course": by_course,
        "by_department": by_department,
        "popular": popular,
        "overdue": overdue,
    }
    return render(request, "enrollments/statistics.html", context)
