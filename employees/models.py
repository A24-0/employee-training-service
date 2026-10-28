from django.db import models


class Employee(models.Model):
    full_name = models.CharField(
        max_length=200,
        verbose_name="ФИО",
    )
    department = models.CharField(
        max_length=200,
        verbose_name="Отдел",
    )

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.department})"
