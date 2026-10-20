import json

from db import import_json
from db.database import fetch_all, fetch_one


def test_import_json_copies_all_records(tmp_path):
    db_path = tmp_path / "test.sqlite"
    import_json.main(db_path)

    for table, filename in [
        ("courses", import_json.COURSES_FILE),
        ("employees", import_json.EMPLOYEES_FILE),
        ("enrollments", import_json.ENROLLMENTS_FILE),
    ]:
        with open(filename, encoding="utf-8") as file:
            expected = len(json.load(file))
        row = fetch_one(f"SELECT COUNT(*) AS n FROM {table}", db_path=db_path)
        assert row["n"] == expected


def test_import_json_can_be_run_twice(tmp_path):
    db_path = tmp_path / "test.sqlite"
    import_json.main(db_path)
    import_json.main(db_path)
    rows = fetch_all("SELECT id FROM courses", db_path=db_path)
    assert len(rows) == len(set(row["id"] for row in rows))


def test_parameterized_query_filters_rows(tmp_path):
    db_path = tmp_path / "test.sqlite"
    import_json.main(db_path)
    rows = fetch_all(
        "SELECT title FROM courses WHERE total_lessons >= ?",
        [100],
        db_path=db_path,
    )
    assert rows == []
