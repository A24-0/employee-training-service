"""Точка входа сервиса обучения сотрудников."""

from typing import List

from courses import (
    add_course,
    check_course_lessons,
    find_course,
    find_course_by_id,
    show_courses,
)
from employees import (
    add_employee,
    find_employee_by_id,
    show_employees,
)
from enrollments import (
    cancel_enrollment,
    create_enrollment,
    get_enrollment_status,
    show_enrollments,
    update_progress,
)
from storage import (
    load_courses,
    load_employees,
    load_enrollments,
    save_courses,
    save_employees,
    save_enrollments,
)
from utils import input_date, input_int, input_str

COURSES_FILE = "data/courses.json"
EMPLOYEES_FILE = "data/employees.json"
ENROLLMENTS_FILE = "data/enrollments.json"

MENU = """
=== Сервис обучения сотрудников ===
1. Показать курсы
2. Найти курс по названию
3. Проверить длительность курса
4. Добавить курс
5. Показать сотрудников
6. Добавить сотрудника
7. Назначить курс сотруднику
8. Обновить прогресс прохождения курса
9. Отменить назначение курса
10. Показать назначения курсов
0. Выход
"""


def add_new_course(courses: List[dict]) -> None:
    """Сценарий добавления нового курса."""
    title = input_str("Название курса: ")
    category = input_str("Категория курса: ")
    total_lessons = input_int("Количество уроков: ")
    course = add_course(courses, title, category, total_lessons)
    print(f"Курс добавлен: {course['title']}")


def add_new_employee(employees: List[dict]) -> None:
    """Сценарий добавления нового сотрудника."""
    full_name = input_str("ФИО сотрудника: ")
    department = input_str("Отдел: ")
    employee = add_employee(employees, full_name, department)
    print(f"Сотрудник добавлен: {employee['full_name']}")


def create_new_enrollment(
    enrollments: List[dict],
    courses: List[dict],
    employees: List[dict],
) -> None:
    """Сценарий назначения курса сотруднику."""
    course_id = input_int("ID курса: ")
    course = find_course_by_id(courses, course_id)
    if course is None:
        print("Курс не найден")
        return

    employee_id = input_int("ID сотрудника: ")
    employee = find_employee_by_id(employees, employee_id)
    if employee is None:
        print("Сотрудник не найден")
        return

    deadline = input_date("Срок сдачи (ГГГГ-ММ-ДД): ")
    total_questions = input_int("Количество вопросов итогового теста: ")

    enrollment = create_enrollment(
        enrollments, employee_id, course_id, deadline, total_questions
    )
    if enrollment is None:
        print("У сотрудника уже есть активное назначение на этот курс")
        return
    print(f"Назначение создано: id={enrollment['id']}")


def update_enrollment_progress(
    enrollments: List[dict],
    courses: List[dict],
) -> None:
    """Сценарий обновления прогресса прохождения курса."""
    enrollment_id = input_int("ID назначения: ")
    lessons_completed = input_int("Пройдено уроков: ")
    correct_answers = input_int("Правильных ответов: ")
    if not update_progress(
        enrollments, enrollment_id, lessons_completed, correct_answers
    ):
        print("Назначение не найдено")
        return

    enrollment = next(
        (e for e in enrollments if e["id"] == enrollment_id), None
    )
    course = find_course_by_id(courses, enrollment["course_id"])
    print(get_enrollment_status(enrollment, course))


def cancel_existing_enrollment(enrollments: List[dict]) -> None:
    """Сценарий отмены назначения курса."""
    enrollment_id = input_int("ID назначения: ")
    if cancel_enrollment(enrollments, enrollment_id):
        print("Назначение отменено")
    else:
        print("Назначение не найдено")


def main() -> None:
    """Основной сценарий программы."""
    courses = load_courses(COURSES_FILE)
    employees = load_employees(EMPLOYEES_FILE)
    enrollments = load_enrollments(ENROLLMENTS_FILE)

    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_courses(courses)
        elif choice == "2":
            query = input_str("Название или часть названия: ")
            show_courses(find_course(courses, query))
        elif choice == "3":
            course_id = input_int("ID курса: ")
            min_lessons = input_int("Минимальное количество уроков: ")
            course = find_course_by_id(courses, course_id)
            if course is None:
                print("Курс не найден")
            else:
                print(check_course_lessons(course, min_lessons))
        elif choice == "4":
            add_new_course(courses)
        elif choice == "5":
            show_employees(employees)
        elif choice == "6":
            add_new_employee(employees)
        elif choice == "7":
            create_new_enrollment(enrollments, courses, employees)
        elif choice == "8":
            update_enrollment_progress(enrollments, courses)
        elif choice == "9":
            cancel_existing_enrollment(enrollments)
        elif choice == "10":
            show_enrollments(enrollments, courses, employees)
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")

    save_courses(COURSES_FILE, courses)
    save_employees(EMPLOYEES_FILE, employees)
    save_enrollments(ENROLLMENTS_FILE, enrollments)
    print("Данные сохранены. До свидания!")


if __name__ == "__main__":
    main()
