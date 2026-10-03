from django.http import HttpResponse

from homepage.views import page
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
    items = ""
    for enrollment in _load_enrollments():
        status = "отменено" if enrollment.is_cancelled else "активно"
        badge = "bg-secondary" if enrollment.is_cancelled else "bg-success"
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/enrollments/{enrollment.id}/">
                {enrollment.employee.full_name} — {enrollment.course.title}
            </a>
            <span class="badge {badge}">{status}</span>
        </li>
        """
    content = f"""
    <h1>Назначения курсов</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Назначения курсов", content))


def enrollment_detail(request, enrollment_id):
    enrollment = find_enrollment_by_id(_load_enrollments(), enrollment_id)

    if enrollment is None:
        content = """
        <h1 class="text-danger">Назначение не найдено</h1>
        <a href="/enrollments/" class="btn btn-outline-secondary">
            ← к списку назначений
        </a>
        """
        return HttpResponse(
            page("Назначение не найдено", content),
            status=404,
        )

    status = "отменено" if enrollment.is_cancelled else "активно"
    badge = "bg-secondary" if enrollment.is_cancelled else "bg-success"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">
                Назначение №{enrollment.id}
            </h5>
            <p class="card-text">
                Сотрудник: {enrollment.employee.full_name}
            </p>
            <p class="card-text">
                Курс: {enrollment.course.title}
            </p>
            <p class="card-text">
                Срок сдачи: {enrollment.deadline.isoformat()}
            </p>
            <p class="card-text">
                Прогресс: {enrollment.lessons_completed} из
                {enrollment.course.total_lessons} уроков
            </p>
            <p class="card-text">
                Статус:
                <span class="badge {badge}">{status}</span>
            </p>
            <p class="card-text">
                Итог: {enrollment.status()}
            </p>
            <a href="/enrollments/" class="btn btn-outline-secondary">
                ← к списку назначений
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Назначение №{enrollment.id}", content),
        status=200,
    )
