from datetime import date

from django.db import models

from courses.models import Course
from employees.models import Employee
from models.status import EnrollmentStatus


class Enrollment(models.Model):
    # PROTECT: курс и сотрудника нельзя удалить, пока на них ссылаются
    # назначения, — история обучения сохраняется
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name="Курс",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name="Сотрудник",
    )
    deadline = models.DateField(
        verbose_name="Срок сдачи",
    )
    lessons_completed = models.PositiveIntegerField(
        default=0,
        verbose_name="Пройдено уроков",
    )
    correct_answers = models.PositiveIntegerField(
        default=0,
        verbose_name="Правильных ответов",
    )
    total_questions = models.PositiveIntegerField(
        verbose_name="Вопросов в тесте",
    )
    # Новое назначение по умолчанию активно
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Назначение отменено",
    )

    class Meta:
        ordering = ["deadline", "pk"]
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"

    def record_progress(self, lessons_completed: int, correct_answers: int) -> None:
        self.lessons_completed = lessons_completed
        self.correct_answers = correct_answers
        self.save(update_fields=["lessons_completed", "correct_answers"])

    def cancel(self) -> None:
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

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
        return f"{self.employee.full_name} — {self.course.title}, срок {self.deadline}"
