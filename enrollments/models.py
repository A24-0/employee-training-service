from datetime import date

from django.db import models

from courses.models import Course
from employees.models import Employee
from models.status import EnrollmentStatus


class EnrollmentQuerySet(models.QuerySet):
    """Набор запросов для работы с назначениями."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_course(self, course):
        return self.filter(course=course)

    def for_employee(self, employee):
        return self.filter(employee=employee)

    def overdue(self):
        # Активные назначения с прошедшим сроком и непройденными уроками
        return self.active().filter(
            deadline__lt=date.today(),
            lessons_completed__lt=models.F("course__total_lessons"),
        )

    def with_related(self):
        return self.select_related("course", "employee")


class EnrollmentManager(models.Manager.from_queryset(EnrollmentQuerySet)):
    pass


class Enrollment(models.Model):
    class Status(models.TextChoices):
        # Назначение действует
        ACTIVE = "active", "Активно"
        # Назначение отменено
        CANCELLED = "cancelled", "Отменено"
        # Все уроки курса пройдены
        COMPLETED = "completed", "Завершено"

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
        help_text="Дата, до которой сотрудник должен пройти курс.",
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
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус назначения",
    )

    objects = EnrollmentManager()

    class Meta:
        ordering = ["deadline", "pk"]
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"

    def record_progress(self, lessons_completed: int, correct_answers: int) -> None:
        self.lessons_completed = lessons_completed
        self.correct_answers = correct_answers
        update_fields = ["lessons_completed", "correct_answers"]
        if self.lessons_completed >= self.course.total_lessons:
            self.status = self.Status.COMPLETED
            update_fields.append("status")
        self.save(update_fields=update_fields)

    def cancel(self) -> None:
        # Отмена меняет состояние, но не удаляет запись из базы
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def mark_completed(self) -> None:
        # Завершение фиксируется, когда пройдены все уроки курса
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])

    def accuracy(self) -> int:
        if self.total_questions == 0:
            return 0
        return int(self.correct_answers / self.total_questions * 100)

    def is_lessons_done(self) -> bool:
        return self.lessons_completed == self.course.total_lessons

    def is_on_time(self) -> bool:
        return date.today() <= self.deadline

    def result_text(self) -> str:
        return EnrollmentStatus.calculate(
            self.accuracy(), self.is_on_time(), self.is_lessons_done()
        )

    def __str__(self) -> str:
        return f"{self.employee.full_name} — {self.course.title}, срок {self.deadline}"
