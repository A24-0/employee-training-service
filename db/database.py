import sqlite3

DB_PATH = "data/training.sqlite"
SCHEMA_FILE = "sql/schema.sql"


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    with open(SCHEMA_FILE, encoding="utf-8") as file:
        conn.executescript(file.read())


def fetch_all(sql, params=(), db_path=DB_PATH):
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=(), db_path=DB_PATH):
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()
