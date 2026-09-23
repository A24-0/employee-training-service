"""Функции для работы с учебными курсами."""

from typing import List, Optional


def add_course(
    courses: List[dict],
    title: str,
    category: str,
    total_lessons: int,
) -> dict:
    """Создать курс и добавить его в коллекцию."""
    course_id = max((c["id"] for c in courses), default=0) + 1
    course = {
        "id": course_id,
        "title": title,
        "category": category,
        "total_lessons": total_lessons,
    }
    courses.append(course)
    return course


def find_course(courses: List[dict], query: str) -> List[dict]:
    """Найти курсы по подстроке названия."""
    query = query.lower()
    return [c for c in courses if query in c["title"].lower()]


def find_course_by_id(courses: List[dict], course_id: int) -> Optional[dict]:
    """Найти курс по идентификатору."""
    for course in courses:
        if course["id"] == course_id:
            return course
    return None


def check_course_lessons(course: dict, min_lessons: int) -> bool:
    """Проверить, что в курсе не меньше min_lessons уроков."""
    return course["total_lessons"] >= min_lessons


def filter_courses_by_category(courses: List[dict], category: str) -> List[dict]:
    """Отобрать курсы по категории."""
    category = category.lower()
    return [c for c in courses if c["category"].lower() == category]


def sort_courses(courses: List[dict]) -> List[dict]:
    """Отсортировать курсы по количеству уроков."""
    return sorted(courses, key=lambda c: c["total_lessons"])


def show_courses(courses: List[dict]) -> None:
    """Вывести список курсов."""
    if not courses:
        print("Курсы не найдены")
        return
    for course in courses:
        print(get_course_info(course))


def get_course_info(course: dict) -> str:
    """Вернуть строку с информацией о курсе (сценарий из ПР1)."""
    return (
        f"[{course['id']}] Курс: {course['title']} ({course['category']}), "
        f"всего уроков: {course['total_lessons']}"
    )
