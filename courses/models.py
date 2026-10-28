from django.db import models


class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название курса",
    )
    category = models.CharField(
        max_length=100,
        verbose_name="Категория",
    )
    # Количество уроков не может быть отрицательным
    total_lessons = models.PositiveIntegerField(
        verbose_name="Количество уроков",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def has_at_least(self, min_lessons: int) -> bool:
        return self.total_lessons >= min_lessons

    def __str__(self) -> str:
        return self.title
