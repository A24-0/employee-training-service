from django.shortcuts import render

from db.database import fetch_all, fetch_one


def courses(request):
    courses_list = fetch_all(
        """
        SELECT id, title, category, total_lessons
        FROM courses
        ORDER BY title
        """
    )
    context = {
        "courses": courses_list,
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, course_id):
    course = fetch_one(
        """
        SELECT id, title, category, total_lessons
        FROM courses
        WHERE id = ?
        """,
        [course_id],
    )
    context = {
        "course": course,
    }
    return render(
        request,
        "courses/course_detail.html",
        context,
        status=404 if course is None else 200,
    )


def available_courses(request):
    employees = fetch_all(
        """
        SELECT id, full_name, department
        FROM employees
        ORDER BY full_name
        """
    )
    employee_id = request.GET.get("employee", "")
    courses_list = []
    if employee_id.isdigit():
        courses_list = fetch_all(
            """
            SELECT id, title, category, total_lessons
            FROM courses
            WHERE id NOT IN (
                SELECT course_id
                FROM enrollments
                WHERE employee_id = ?
                  AND is_cancelled = 0
            )
            ORDER BY title
            """,
            [int(employee_id)],
        )
    context = {
        "employees": employees,
        "employee_id": employee_id,
        "courses": courses_list,
    }
    return render(request, "courses/available.html", context)
