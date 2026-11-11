from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from pytils.translit import slugify


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
        help_text="Укажите число уроков в курсе, включая итоговый тест.",
    )
    cover = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True,
        verbose_name="Обложка",
        help_text="Необязательно. Форматы JPEG, PNG или WebP.",
    )
    # Англоязычный идентификатор для адреса страницы курса
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name="Слаг",
        help_text="Формируется автоматически из названия курса.",
    )
    # Признак вычисляется базой данных по количеству уроков:
    # курс считается длительным, если в нём 20 уроков и более
    is_long = models.GeneratedField(
        expression=Case(
            When(total_lessons__gte=20, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Длительный курс",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def has_at_least(self, min_lessons: int) -> bool:
        return self.total_lessons >= min_lessons

    def _make_unique_slug(self) -> str:
        base = slugify(self.title)[:200] or "course"
        candidate = base
        number = 2
        while (
            Course.objects.filter(slug=candidate)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate = f"{base}-{number}"
            number += 1
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._make_unique_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("courses:detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.title
