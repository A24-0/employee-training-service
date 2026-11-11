from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q
from django.db.models.functions import Round
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from courses.models import Course
from employees.models import Employee
from enrollments.forms import EnrollmentFilterForm, EnrollmentForm
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
    # Форма получает GET-параметры и проверяет их типы и допустимость
    form = EnrollmentFilterForm(request.GET or None)
    enrollments_list = Enrollment.objects.with_related()

    if form.is_valid():
        cleaned = form.cleaned_data
        query = cleaned.get("q")
        course = cleaned.get("course")
        employee = cleaned.get("employee")
        status = cleaned.get("status")
        deadline = cleaned.get("deadline")
        sort = cleaned.get("sort") or DEFAULT_SORT

        # Поиск по ФИО сотрудника — строковому полю связанной модели
        # (iregex вместо icontains: см. courses.views.courses)
        if query:
            enrollments_list = enrollments_list.filter(
                employee__full_name__iregex=query,
            )
        if course:
            enrollments_list = enrollments_list.filter(course=course)
        if employee:
            enrollments_list = enrollments_list.filter(employee=employee)
        if status:
            enrollments_list = enrollments_list.filter(status=status)
        if deadline:
            enrollments_list = enrollments_list.filter(deadline__lte=deadline)
    else:
        sort = DEFAULT_SORT

    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT

    # Названия курса и сотрудника берутся из связанных таблиц одним запросом;
    # id добавлен в сортировку для стабильного порядка
    enrollments_list = (
        enrollments_list
        .annotate(
            course_title=F("course__title"),
            employee_name=F("employee__full_name"),
        )
        .order_by(SORT_FIELDS[sort], "id")
    )

    paginator = Paginator(enrollments_list, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "enrollments": page_obj,
        "page_obj": page_obj,
        "form": form,
        "sort": sort,
        "courses": Course.objects.order_by("title"),
        "employees": Employee.objects.order_by("full_name"),
    }
    return render(request, "enrollments/enrollment_list.html", context)


def enrollment_detail(request: HttpRequest, enrollment_id: int) -> HttpResponse:
    # Курс и сотрудник загружаются вместе с назначением одним запросом
    enrollment = get_object_or_404(
        Enrollment.objects.with_related(),
        pk=enrollment_id,
    )
    context = {
        "enrollment": enrollment,
    }
    return render(request, "enrollments/enrollment_detail.html", context)


def _has_active_conflict(form: EnrollmentForm) -> bool:
    """Проверяет, есть ли у сотрудника активное назначение на этот курс."""
    employee = form.cleaned_data.get("employee")
    course = form.cleaned_data.get("course")
    if not employee or not course:
        return False
    conflicts = Enrollment.objects.active().filter(
        employee=employee,
        course=course,
    )
    # При редактировании назначение не должно конфликтовать само с собой
    if form.instance.pk:
        conflicts = conflicts.exclude(pk=form.instance.pk)
    return conflicts.exists()


def enrollment_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            if _has_active_conflict(form):
                # Общая ошибка формы, а не ошибка отдельного поля
                form.add_error(
                    None,
                    "У сотрудника уже есть активное назначение на этот курс.",
                )
            else:
                enrollment = form.save()
                messages.success(
                    request,
                    f"Назначение №{enrollment.pk} создано.",
                )
                return redirect("enrollments:detail", enrollment_id=enrollment.pk)
    else:
        form = EnrollmentForm()
    return render(
        request,
        "enrollments/enrollment_form.html",
        {"form": form, "is_edit": False},
    )


def enrollment_edit(request: HttpRequest, enrollment_id: int) -> HttpResponse:
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    if request.method == "POST":
        # instance связывает форму с существующим объектом
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            if _has_active_conflict(form):
                form.add_error(
                    None,
                    "У сотрудника уже есть активное назначение на этот курс.",
                )
            else:
                form.save()
                messages.success(request, "Изменения сохранены.")
                return redirect("enrollments:detail", enrollment_id=enrollment.pk)
    else:
        form = EnrollmentForm(instance=enrollment)
    return render(
        request,
        "enrollments/enrollment_form.html",
        {"form": form, "is_edit": True, "enrollment": enrollment},
    )


@require_POST
def enrollment_cancel(request: HttpRequest, enrollment_id: int) -> HttpResponse:
    # Отмена меняет статус, запись остаётся в базе
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    if enrollment.status == Enrollment.Status.CANCELLED:
        messages.info(request, "Назначение уже отменено.")
    else:
        enrollment.cancel()
        messages.success(request, "Назначение отменено.")
    return redirect("enrollments:detail", enrollment_id=enrollment.pk)


def statistics(request: HttpRequest) -> HttpResponse:
    summary = Course.objects.aggregate(
        courses_count=Count("id"),
        min_lessons=Min("total_lessons"),
        max_lessons=Max("total_lessons"),
        avg_lessons=Round(Avg("total_lessons"), 1),
    )
    # Подсчёт по статусам через методы пользовательского менеджера
    active_count = Enrollment.objects.active().count()
    cancelled_count = Enrollment.objects.cancelled().count()
    completed_count = Enrollment.objects.completed().count()
    overdue_count = Enrollment.objects.overdue().count()

    # Запрос строится от Course, поэтому курсы без назначений тоже попадают
    # в результат (аналог LEFT JOIN); считаются назначения по статусам
    by_course = (
        Course.objects
        .annotate(
            course_title=F("title"),
            enrollments_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
            ),
            completed_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.COMPLETED),
            ),
        )
        .values("course_title", "enrollments_count", "completed_count")
        .order_by("-enrollments_count", "course_title")
    )
    # Группировка активных назначений по отделу сотрудника
    by_department = (
        Enrollment.objects.active()
        .values(department=F("employee__department"))
        .annotate(enrollments_count=Count("id"))
        .order_by("-enrollments_count", "department")
    )
    # Условие на результат агрегации (аналог HAVING)
    popular = by_course.filter(enrollments_count__gt=1)
    # Просроченные активные назначения
    overdue = (
        Enrollment.objects.overdue()
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
        "cancelled_count": cancelled_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
        "by_course": by_course,
        "by_department": by_department,
        "popular": popular,
        "overdue": overdue,
    }
    return render(request, "enrollments/statistics.html", context)
