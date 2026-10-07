from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.courses import find_course_by_id
from storage import load_courses

COURSES_FILE = "data/courses.json"


def courses(request):
    items = ""
    for course in load_courses(COURSES_FILE):
        text = f"{course.title} ({course.category}) — {course.total_lessons} уроков"
        items += (
            f'<li class="list-group-item">'
            f'<a href="/courses/{course.id}/">{text}</a>'
            f"</li>"
        )
    content = f"""
    <h1>Курсы</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Курсы", content))


def course_detail(request, course_id):
    try:
        course_id = int(course_id)
    except ValueError:
        content = f"""
        <h1 class="text-danger">Некорректный ID курса</h1>
        <p>ID должен быть числом, а получено: «{escape(course_id)}»</p>
        <a href="/courses/" class="btn btn-outline-secondary">
            ← к списку курсов
        </a>
        """
        return HttpResponse(
            page("Некорректный ID", content),
            status=400,
        )

    course = find_course_by_id(load_courses(COURSES_FILE), course_id)

    if course is None:
        content = """
        <h1 class="text-danger">Курс не найден</h1>
        <a href="/courses/" class="btn btn-outline-secondary">
            ← к списку курсов
        </a>
        """
        return HttpResponse(
            page("Курс не найден", content),
            status=404,
        )

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{course.title}</h5>
            <p class="card-text">
                <strong>ID:</strong> {course.id}
            </p>
            <p class="card-text">
                <strong>Категория:</strong> {course.category}
            </p>
            <p class="card-text">
                <strong>Количество уроков:</strong> {course.total_lessons}
            </p>
            <a href="/courses/" class="btn btn-outline-secondary">
                ← к списку курсов
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(course.title, content),
        status=200,
    )
