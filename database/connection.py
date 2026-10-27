"""
Database Connection Manager for Acadence.
Configures and yields SQLite connection with row factory.
"""

import os
import sqlite3

# Store the SQLite database file in the project root directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "acadence.db")


def get_connection() -> sqlite3.Connection:
    """Establish connection with sqlite3.Row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
