from datetime import date
from typing import List, Optional

from .courses import Course
from .employees import Employee
from .status import EnrollmentStatus


class Enrollment:

    def __init__(
        self,
        enrollment_id: int,
        course: Course,
        employee: Employee,
        deadline: date,
        total_questions: int,
    ) -> None:
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
        self.lessons_completed = lessons_completed
        self.correct_answers = correct_answers

    def cancel(self) -> None:
        self.is_cancelled = True

    def accuracy(self) -> int:
        if self.total_questions == 0:
            return 0
        return int(self.correct_answers / self.total_questions * 100)

    def is_lessons_done(self) -> bool:
        return self.lessons_completed == self.course.total_lessons

    def is_on_time(self) -> bool:
        return date.today() <= self.deadline

    def status(self) -> str:
        return EnrollmentStatus.calculate(
            self.accuracy(), self.is_on_time(), self.is_lessons_done()
        )

    def __str__(self) -> str:
        cancelled = " (отменено)" if self.is_cancelled else ""
        lessons_status = EnrollmentStatus.check_lessons_completion(
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
    for enrollment in enrollments:
        if enrollment.id == enrollment_id:
            return enrollment
    return None


def cancel_enrollment(enrollments: List[Enrollment], enrollment_id: int) -> bool:
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
    enrollment = find_enrollment_by_id(enrollments, enrollment_id)
    if enrollment is None:
        return False
    enrollment.record_progress(lessons_completed, correct_answers)
    return True


def show_enrollments(enrollments: List[Enrollment]) -> None:
    if not enrollments:
        print("Назначения не найдены")
        return
    for enrollment in enrollments:
        print(enrollment)
