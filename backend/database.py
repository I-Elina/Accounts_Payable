import sqlite3
from pathlib import Path
from backend.settings import get_db_file_path


def get_conn(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else get_db_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_conn(db_path)
    try:
        conn.executescript(schema_sql)
        # Seed default settings if not present
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                [
                    ("auto_pass_threshold", "0.85"),
                    ("exception_below", "0.40"),
                    ("policy_limit", "100000"),
                ],
            )
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)
