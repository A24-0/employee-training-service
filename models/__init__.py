"""Пакет моделей предметной области сервиса обучения сотрудников."""

from .courses import Course
from .employees import Employee
from .enrollments import Enrollment

__all__ = ["Course", "Employee", "Enrollment"]
