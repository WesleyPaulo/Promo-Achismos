import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "/data/promo.db")


def connect(path=None):
    con = sqlite3.connect(path or DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init(con):
    con.executescript((Path(__file__).parent / "schema.sql").read_text())
