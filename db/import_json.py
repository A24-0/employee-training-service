import json

from db.database import DB_PATH, create_schema, get_connection

COURSES_FILE = "data/courses.json"
EMPLOYEES_FILE = "data/employees.json"
ENROLLMENTS_FILE = "data/enrollments.json"


def load_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def clear_tables(conn):
    # Сначала удаляем назначения: они ссылаются на курсы и сотрудников
    conn.execute("DELETE FROM enrollments")
    conn.execute("DELETE FROM employees")
    conn.execute("DELETE FROM courses")


def import_courses(conn, filename=COURSES_FILE):
    conn.executemany(
        """
        INSERT INTO courses (id, title, category, total_lessons)
        VALUES (?, ?, ?, ?)
        """,
        [
            (c["id"], c["title"], c["category"], c["total_lessons"])
            for c in load_json(filename)
        ],
    )


def import_employees(conn, filename=EMPLOYEES_FILE):
    conn.executemany(
        """
        INSERT INTO employees (id, full_name, department)
        VALUES (?, ?, ?)
        """,
        [
            (e["id"], e["full_name"], e["department"])
            for e in load_json(filename)
        ],
    )


def import_enrollments(conn, filename=ENROLLMENTS_FILE):
    conn.executemany(
        """
        INSERT INTO enrollments (
            id, course_id, employee_id, deadline,
            lessons_completed, correct_answers, total_questions, is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                e["id"],
                e["course_id"],
                e["employee_id"],
                e["deadline"],
                e["lessons_completed"],
                e["correct_answers"],
                e["total_questions"],
                int(e["is_cancelled"]),
            )
            for e in load_json(filename)
        ],
    )


def main(db_path=DB_PATH):
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        clear_tables(conn)
        import_courses(conn)
        import_employees(conn)
        import_enrollments(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
