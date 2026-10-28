import sqlite3
from pathlib import Path

# Скрипт лежит в каталоге db, корень проекта — на уровень выше
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "training.sqlite"


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    # Выполняются только запросы на чтение: исходная база не изменяется
    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            columns = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()
            print("Столбцы:")
            for column in columns:
                print(
                    f"  имя={column['name']}, "
                    f"тип={column['type']}, "
                    f"NOT NULL={column['notnull']}, "
                    f"PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]
            print(f"Количество записей: {count}")

        # Внешние ключи назначений должны указывать на существующие записи
        broken = connection.execute(
            """
            SELECT COUNT(*)
            FROM enrollments
            WHERE course_id NOT IN (SELECT id FROM courses)
               OR employee_id NOT IN (SELECT id FROM employees)
            """
        ).fetchone()[0]
        print(f"\nНазначений с несуществующим курсом или сотрудником: {broken}")

        cancelled_values = connection.execute(
            "SELECT DISTINCT is_cancelled FROM enrollments ORDER BY is_cancelled"
        ).fetchall()
        print(
            "Значения is_cancelled:",
            [row["is_cancelled"] for row in cancelled_values],
        )


if __name__ == "__main__":
    main()
