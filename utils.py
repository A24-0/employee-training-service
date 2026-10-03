from datetime import date


def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Некорректное число, попробуйте ещё раз")


def input_date(prompt: str) -> date:
    while True:
        try:
            return date.fromisoformat(input(prompt))
        except ValueError:
            print("Некорректная дата, используйте формат ГГГГ-ММ-ДД")


def input_str(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым")
