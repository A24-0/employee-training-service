"""Вспомогательные функции безопасного ввода данных."""

from datetime import date


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Некорректное число, попробуйте ещё раз")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ГГГГ-ММ-ДД."""
    while True:
        try:
            return date.fromisoformat(input(prompt))
        except ValueError:
            print("Некорректная дата, используйте формат ГГГГ-ММ-ДД")


def input_str(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым")
