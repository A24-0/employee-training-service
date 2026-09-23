"""Функции сохранения и загрузки объектов в формате JSON."""

import json
from datetime import date
from typing import List

from models import Course, Employee, Enrollment
from models.courses import find_course_by_id
from models.employees import find_employee_by_id


def _load(filename: str) -> list:
    """Загрузить список данных из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Предупреждение: файл {filename} повреждён, используется пустой список")
        return []


def _save(filename: str, data: list) -> None:
    """Сохранить список данных в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_courses(filename: str) -> List[Course]:
    """Загрузить курсы из JSON-файла и преобразовать их в объекты Course."""
    return [Course.from_data(item) for item in _load(filename)]


def save_courses(filename: str, courses: List[Course]) -> None:
    """Сохранить объекты Course в JSON-файл."""
    data = [
        {
            "id": course.id,
            "title": course.title,
            "category": course.category,
            "total_lessons": course.total_lessons,
        }
        for course in courses
    ]
    _save(filename, data)


def load_employees(filename: str) -> List[Employee]:
    """Загрузить сотрудников из JSON-файла и создать объекты Employee."""
    return [Employee.from_data(item) for item in _load(filename)]


def save_employees(filename: str, employees: List[Employee]) -> None:
    """Сохранить объекты Employee в JSON-файл."""
    data = [
        {
            "id": employee.id,
            "full_name": employee.full_name,
            "department": employee.department,
        }
        for employee in employees
    ]
    _save(filename, data)


def load_enrollments(
    filename: str,
    courses: List[Course],
    employees: List[Employee],
) -> List[Enrollment]:
    """Загрузить назначения курсов и восстановить связи с Course и Employee."""
    enrollments = []
    for item in _load(filename):
        course = find_course_by_id(courses, item["course_id"])
        employee = find_employee_by_id(employees, item["employee_id"])
        if course is None or employee is None:
            continue
        enrollment = Enrollment(
            item["id"],
            course,
            employee,
            date.fromisoformat(item["deadline"]),
            item["total_questions"],
        )
        enrollment.lessons_completed = item["lessons_completed"]
        enrollment.correct_answers = item["correct_answers"]
        enrollment.is_cancelled = item["is_cancelled"]
        enrollments.append(enrollment)
    return enrollments


def save_enrollments(filename: str, enrollments: List[Enrollment]) -> None:
    """Сохранить объекты Enrollment в JSON-файл (по идентификаторам связей)."""
    data = [
        {
            "id": enrollment.id,
            "course_id": enrollment.course.id,
            "employee_id": enrollment.employee.id,
            "deadline": enrollment.deadline.isoformat(),
            "lessons_completed": enrollment.lessons_completed,
            "correct_answers": enrollment.correct_answers,
            "total_questions": enrollment.total_questions,
            "is_cancelled": enrollment.is_cancelled,
        }
        for enrollment in enrollments
    ]
    _save(filename, data)
