import sqlite3
from pathlib import Path
from typing import Any, Optional, Sequence, Union

DB_PATH = "data/training.sqlite"
SCHEMA_FILE = "sql/schema.sql"


def get_connection(db_path: Union[str, Path] = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_FILE, encoding="utf-8") as file:
        conn.executescript(file.read())


def fetch_all(
    sql: str, params: Sequence[Any] = (), db_path: Union[str, Path] = DB_PATH
) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def fetch_one(
    sql: str, params: Sequence[Any] = (), db_path: Union[str, Path] = DB_PATH
) -> Optional[dict[str, Any]]:
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()
