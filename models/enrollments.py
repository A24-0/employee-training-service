"""Класс Enrollment и функции для работы с коллекцией назначений."""

from datetime import date
from typing import List, Optional

from .courses import Course
from .employees import Employee


class Enrollment:
    """Назначение курса сотруднику."""

    def __init__(
        self,
        enrollment_id: int,
        course: Course,
        employee: Employee,
        deadline: date,
        total_questions: int,
    ) -> None:
        """Создать объект назначения курса."""
        self.id = enrollment_id
        self.course = course
        self.employee = employee
        self.deadline = deadline
        self.total_questions = total_questions
        self.lessons_completed = 0
        self.correct_answers = 0
        self.is_cancelled = False

    def record_progress(
        self,
        lessons_completed: int,
        correct_answers: int,
    ) -> None:
        """Обновить прогресс прохождения курса."""
        self.lessons_completed = lessons_completed
        self.correct_answers = correct_answers

    def cancel(self) -> None:
        """Отменить назначение курса."""
        self.is_cancelled = True

    def accuracy(self) -> int:
        """Вычислить точность ответов на итоговый тест, в процентах."""
        if self.total_questions == 0:
            return 0
        return int(self.correct_answers / self.total_questions * 100)

    def is_lessons_done(self) -> bool:
        """Проверить, что все уроки курса пройдены."""
        return self.lessons_completed == self.course.total_lessons

    def is_on_time(self) -> bool:
        """Проверить, что срок сдачи ещё не истёк."""
        return date.today() <= self.deadline

    @staticmethod
    def check_lessons_completion(lessons_completed: int, total: int) -> str:
        """Проверяет, все ли уроки пройдены (функция из ПР1)."""
        if lessons_completed == total:
            return "Все уроки пройдены"
        return f"Пройдено {lessons_completed} из {total} уроков"

    @staticmethod
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

    def status(self) -> str:
        """Сформировать текстовый статус назначения курса."""
        return self.calculate_status(
            self.accuracy(), self.is_on_time(), self.is_lessons_done()
        )

    def __str__(self) -> str:
        """Вернуть строковое представление назначения курса."""
        cancelled = " (отменено)" if self.is_cancelled else ""
        lessons_status = self.check_lessons_completion(
            self.lessons_completed, self.course.total_lessons
        )
        return (
            f"[{self.id}] {self.employee.full_name} -> {self.course.title}, "
            f"срок: {self.deadline.isoformat()}, {lessons_status}{cancelled}"
        )


def is_course_available(
    enrollments: List[Enrollment],
    employee: Employee,
    course: Course,
) -> bool:
    """Проверить, нет ли у сотрудника активного назначения на курс."""
    for enrollment in enrollments:
        if (
            enrollment.employee.id == employee.id
            and enrollment.course.id == course.id
            and not enrollment.is_cancelled
        ):
            return False
    return True


def create_enrollment(
    enrollments: List[Enrollment],
    employee: Employee,
    course: Course,
    deadline: date,
    total_questions: int,
) -> Optional[Enrollment]:
    """Создать объект Enrollment, связав его с Course и Employee."""
    if not is_course_available(enrollments, employee, course):
        return None
    enrollment_id = max((e.id for e in enrollments), default=0) + 1
    enrollment = Enrollment(
        enrollment_id, course, employee, deadline, total_questions
    )
    enrollments.append(enrollment)
    return enrollment


def find_enrollment_by_id(
    enrollments: List[Enrollment],
    enrollment_id: int,
) -> Optional[Enrollment]:
    """Найти назначение курса по идентификатору."""
    for enrollment in enrollments:
        if enrollment.id == enrollment_id:
            return enrollment
    return None


def cancel_enrollment(enrollments: List[Enrollment], enrollment_id: int) -> bool:
    """Найти назначение и отменить его."""
    enrollment = find_enrollment_by_id(enrollments, enrollment_id)
    if enrollment is None:
        return False
    enrollment.cancel()
    return True


def update_progress(
    enrollments: List[Enrollment],
    enrollment_id: int,
    lessons_completed: int,
    correct_answers: int,
) -> bool:
    """Найти назначение и обновить его прогресс."""
    enrollment = find_enrollment_by_id(enrollments, enrollment_id)
    if enrollment is None:
        return False
    enrollment.record_progress(lessons_completed, correct_answers)
    return True


def show_enrollments(enrollments: List[Enrollment]) -> None:
    """Вывести список назначений курсов."""
    if not enrollments:
        print("Назначения не найдены")
        return
    for enrollment in enrollments:
        print(enrollment)
