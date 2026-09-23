"""Функции для работы с назначениями курсов (прохождением обучения)."""

from datetime import date
from typing import List, Optional


def check_lessons_completion(lessons_completed: int, total: int) -> str:
    """Проверяет, все ли уроки пройдены (функция из ПР1)."""
    if lessons_completed == total:
        return "Все уроки пройдены"
    return f"Пройдено {lessons_completed} из {total} уроков"


def calculate_status(
    accuracy: int,
    is_on_time: bool,
    all_lessons_done: bool,
) -> str:
    """Определяет итоговый статус прохождения курса (функция из ПР1)."""
    if not all_lessons_done:
        return "Курс не завершён: не все уроки пройдены"
    if accuracy < 80:
        return f"Тест не сдан. Результат: {accuracy}% (порог — 80%)"
    if not is_on_time:
        return "Курс пройден, но с нарушением сроков"
    if accuracy >= 90:
        return "Курс пройден на отлично! Сертификат выдан."
    return "Курс пройден успешно. Сертификат выдан."


def is_course_available(
    enrollments: List[dict],
    employee_id: int,
    course_id: int,
) -> bool:
    """Проверить, нет ли у сотрудника активного назначения на курс."""
    for enrollment in enrollments:
        if (
            enrollment["employee_id"] == employee_id
            and enrollment["course_id"] == course_id
            and not enrollment["is_cancelled"]
        ):
            return False
    return True


def create_enrollment(
    enrollments: List[dict],
    employee_id: int,
    course_id: int,
    deadline: date,
    total_questions: int,
) -> Optional[dict]:
    """Создать назначение курса сотруднику."""
    if not is_course_available(enrollments, employee_id, course_id):
        return None
    enrollment_id = max((e["id"] for e in enrollments), default=0) + 1
    enrollment = {
        "id": enrollment_id,
        "employee_id": employee_id,
        "course_id": course_id,
        "deadline": deadline.isoformat(),
        "lessons_completed": 0,
        "correct_answers": 0,
        "total_questions": total_questions,
        "is_cancelled": False,
    }
    enrollments.append(enrollment)
    return enrollment


def cancel_enrollment(enrollments: List[dict], enrollment_id: int) -> bool:
    """Отменить назначение курса."""
    for enrollment in enrollments:
        if enrollment["id"] == enrollment_id:
            enrollment["is_cancelled"] = True
            return True
    return False


def update_progress(
    enrollments: List[dict],
    enrollment_id: int,
    lessons_completed: int,
    correct_answers: int,
) -> bool:
    """Обновить прогресс прохождения курса."""
    for enrollment in enrollments:
        if enrollment["id"] == enrollment_id:
            enrollment["lessons_completed"] = lessons_completed
            enrollment["correct_answers"] = correct_answers
            return True
    return False


def get_enrollment_status(enrollment: dict, course: dict) -> str:
    """Сформировать текстовый статус назначения курса."""
    total_questions = enrollment["total_questions"]
    accuracy = (
        int(enrollment["correct_answers"] / total_questions * 100)
        if total_questions > 0
        else 0
    )
    all_lessons_done = (
        enrollment["lessons_completed"] == course["total_lessons"]
    )
    deadline = date.fromisoformat(enrollment["deadline"])
    is_on_time = date.today() <= deadline
    return calculate_status(accuracy, is_on_time, all_lessons_done)


def show_enrollments(
    enrollments: List[dict],
    courses: List[dict],
    employees: List[dict],
) -> None:
    """Вывести список назначений курсов."""
    if not enrollments:
        print("Назначения не найдены")
        return
    for enrollment in enrollments:
        course = next(
            (c for c in courses if c["id"] == enrollment["course_id"]), None
        )
        employee = next(
            (e for e in employees if e["id"] == enrollment["employee_id"]),
            None,
        )
        course_title = course["title"] if course else "?"
        employee_name = employee["full_name"] if employee else "?"
        cancelled = " (отменено)" if enrollment["is_cancelled"] else ""
        lessons_status = check_lessons_completion(
            enrollment["lessons_completed"], course["total_lessons"]
        ) if course else "?"
        print(
            f"[{enrollment['id']}] {employee_name} -> {course_title}, "
            f"срок: {enrollment['deadline']}, {lessons_status}{cancelled}"
        )
