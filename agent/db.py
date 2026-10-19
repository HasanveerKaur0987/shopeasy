import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "shopeasy.db"

def init_db():
    """Rebuild the database from schema.sql + seed.sql (fresh demo data)."""
    folder = DB_PATH.parent
    conn = sqlite3.connect(DB_PATH)
    conn.executescript((folder / "schema.sql").read_text())
    conn.executescript((folder / "seed.sql").read_text())
    conn.close()

def get_connection():
    """Open the ShopEasy database. Rows can be read like dicts."""

    con = sqlite3.connect(DB_PATH)

    con.row_factory = sqlite3.Row

    con.execute("PRAGMA foreign_keys = ON")

    return con