"""Функции сохранения и загрузки данных в формате JSON."""

import json
from typing import List


def _load(filename: str) -> list:
    """Загрузить список данных из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Предупреждение: файл {filename} повреждён, используется пустой список")
        return []


def _save(filename: str, data: list) -> None:
    """Сохранить список данных в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_courses(filename: str) -> List[dict]:
    """Загрузить курсы из JSON-файла."""
    return _load(filename)


def save_courses(filename: str, courses: List[dict]) -> None:
    """Сохранить курсы в JSON-файл."""
    _save(filename, courses)


def load_employees(filename: str) -> List[dict]:
    """Загрузить сотрудников из JSON-файла."""
    return _load(filename)


def save_employees(filename: str, employees: List[dict]) -> None:
    """Сохранить сотрудников в JSON-файл."""
    _save(filename, employees)


def load_enrollments(filename: str) -> List[dict]:
    """Загрузить назначения курсов из JSON-файла."""
    return _load(filename)


def save_enrollments(filename: str, enrollments: List[dict]) -> None:
    """Сохранить назначения курсов в JSON-файл."""
    _save(filename, enrollments)
