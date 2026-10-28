import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

# Скрипт лежит в каталоге db, корень проекта — на уровень выше.
# Корень добавляется в пути поиска модулей, чтобы найти пакет настроек.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SOURCE_DB = BASE_DIR / "data" / "training.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "training.settings")
django.setup()

# Модели импортируются только после инициализации Django
from courses.models import Course  # noqa: E402
from employees.models import Employee  # noqa: E402
from enrollments.models import Enrollment  # noqa: E402


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        courses = connection.execute(
            """
            SELECT id, title, category, total_lessons
            FROM courses
            ORDER BY id
            """
        ).fetchall()
        employees = connection.execute(
            """
            SELECT id, full_name, department
            FROM employees
            ORDER BY id
            """
        ).fetchall()
        enrollments = connection.execute(
            """
            SELECT
                id, course_id, employee_id, deadline,
                lessons_completed, correct_answers, total_questions, is_cancelled
            FROM enrollments
            ORDER BY id
            """
        ).fetchall()

    # Запись в базу Django одной транзакцией: при ошибке перенос откатывается.
    # Сначала курсы и сотрудники, затем ссылающиеся на них назначения.
    with transaction.atomic():
        for row in courses:
            Course.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "title": row["title"],
                    "category": row["category"],
                    "total_lessons": row["total_lessons"],
                },
            )
        for row in employees:
            Employee.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "full_name": row["full_name"],
                    "department": row["department"],
                },
            )
        for row in enrollments:
            Enrollment.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "course_id": row["course_id"],
                    "employee_id": row["employee_id"],
                    # Строка YYYY-MM-DD преобразуется в date для DateField
                    "deadline": date.fromisoformat(row["deadline"]),
                    "lessons_completed": row["lessons_completed"],
                    "correct_answers": row["correct_answers"],
                    "total_questions": row["total_questions"],
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )

    print("Перенос данных завершён.")
    print(f"Курсов: {Course.objects.count()}")
    print(f"Сотрудников: {Employee.objects.count()}")
    print(f"Назначений: {Enrollment.objects.count()}")


if __name__ == "__main__":
    main()
