import sqlite3
import os
from typing import Dict, Any
from pathlib import Path

# Get project root - go up from db_utils.py -> tools/ -> mcp/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / 'database' / 'support.db'

# Flag to track if WAL mode has been initialized (only needs to be set once)
_wal_initialized = False
# wal mode is used to ensure that the database is always in a consistent state
# it allows for multiple reads and writes to the database concurrently
# due to this throughput of the database is increased
def _ensure_wal_mode():
    """Initialize WAL mode once for the database. This persists across connections."""
    global _wal_initialized
    if not _wal_initialized:
        try:
            conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.close()
            _wal_initialized = True
        except Exception:
            pass  # Fail silently, database will still work in default mode

def get_db_connection():
    """Create a database connection with row factory for dict-like access."""
    _ensure_wal_mode()  # Only runs once per process
    conn = sqlite3.connect(str(DB_PATH), timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a SQLite row to a dictionary."""
    return {key: row[key] for key in row.keys()}