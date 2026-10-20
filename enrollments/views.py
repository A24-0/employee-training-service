from datetime import date

from django.shortcuts import render

from db.database import fetch_all, fetch_one
from models import Course, Employee, Enrollment


def _enrollment_from_row(row):
    course = Course(
        row["course_id"],
        row["course_title"],
        row["category"],
        row["total_lessons"],
    )
    employee = Employee(
        row["employee_id"],
        row["employee_name"],
        row["department"],
    )
    enrollment = Enrollment(
        row["id"],
        course,
        employee,
        date.fromisoformat(row["deadline"]),
        row["total_questions"],
    )
    enrollment.record_progress(row["lessons_completed"], row["correct_answers"])
    enrollment.is_cancelled = bool(row["is_cancelled"])
    return enrollment


def enrollments(request):
    enrollments_list = fetch_all(
        """
        SELECT
            enrollments.id,
            strftime('%d.%m.%Y', enrollments.deadline) AS deadline,
            enrollments.is_cancelled,
            courses.title AS course_title,
            employees.full_name AS employee_name
        FROM enrollments
        JOIN courses ON enrollments.course_id = courses.id
        JOIN employees ON enrollments.employee_id = employees.id
        ORDER BY enrollments.deadline
        """
    )
    context = {
        "enrollments": enrollments_list,
    }
    return render(request, "enrollments/enrollment_list.html", context)


def enrollment_detail(request, enrollment_id):
    row = fetch_one(
        """
        SELECT
            enrollments.*,
            courses.title AS course_title,
            courses.category,
            courses.total_lessons,
            employees.full_name AS employee_name,
            employees.department
        FROM enrollments
        JOIN courses ON enrollments.course_id = courses.id
        JOIN employees ON enrollments.employee_id = employees.id
        WHERE enrollments.id = ?
        """,
        [enrollment_id],
    )
    enrollment = _enrollment_from_row(row) if row else None
    context = {
        "enrollment": enrollment,
    }
    return render(
        request,
        "enrollments/enrollment_detail.html",
        context,
        status=404 if enrollment is None else 200,
    )


def statistics(request):
    summary = fetch_one(
        """
        SELECT
            COUNT(*) AS courses_count,
            MIN(total_lessons) AS min_lessons,
            MAX(total_lessons) AS max_lessons,
            ROUND(AVG(total_lessons), 1) AS avg_lessons
        FROM courses
        """
    )
    active_count = fetch_one(
        """
        SELECT COUNT(*) AS active_count
        FROM enrollments
        WHERE is_cancelled = 0
        """
    )["active_count"]
    by_course = fetch_all(
        """
        SELECT
            courses.title AS course_title,
            COUNT(enrollments.id) AS enrollments_count
        FROM courses
        LEFT JOIN enrollments
            ON courses.id = enrollments.course_id
            AND enrollments.is_cancelled = 0
        GROUP BY courses.id, courses.title
        ORDER BY enrollments_count DESC, courses.title
        """
    )
    by_department = fetch_all(
        """
        SELECT
            employees.department,
            COUNT(enrollments.id) AS enrollments_count
        FROM enrollments
        JOIN employees ON enrollments.employee_id = employees.id
        WHERE enrollments.is_cancelled = 0
        GROUP BY employees.department
        ORDER BY enrollments_count DESC
        """
    )
    popular = fetch_all(
        """
        SELECT
            courses.title AS course_title,
            COUNT(enrollments.id) AS enrollments_count
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.is_cancelled = 0
        GROUP BY courses.id, courses.title
        HAVING COUNT(enrollments.id) > 1
        ORDER BY enrollments_count DESC
        """
    )
    overdue = fetch_all(
        """
        SELECT
            enrollments.id,
            employees.full_name AS employee_name,
            courses.title AS course_title,
            strftime('%d.%m.%Y', enrollments.deadline) AS deadline
        FROM enrollments
        JOIN courses ON enrollments.course_id = courses.id
        JOIN employees ON enrollments.employee_id = employees.id
        WHERE enrollments.is_cancelled = 0
          AND enrollments.deadline < date('now')
          AND enrollments.lessons_completed < courses.total_lessons
        ORDER BY enrollments.deadline
        """
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
