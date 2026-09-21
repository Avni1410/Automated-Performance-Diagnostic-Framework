"""
database.py

Handles SQLite database creation and storage of periodic system
metric snapshots. This module owns all database logic - other parts
of the project (main.py, later the dashboard and diagnostic engine)
should go through these functions rather than writing raw SQL
themselves.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


# Database file lives in the top-level data/ folder.
# The data/ folder is already excluded from Git.
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "metrics.db"


def init_db():
    """
    Creates the database file and system_metrics table if they
    don't already exist.

    Also performs a migration for databases created during
    earlier phases by adding the network_connections column
    if it does not already exist.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_percent REAL NOT NULL,
            disk_percent REAL NOT NULL,
            process_count INTEGER NOT NULL,
            thread_count INTEGER NOT NULL,
            network_connections INTEGER NOT NULL DEFAULT 0,
            file_descriptor_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Migration:
    # Check whether an existing database from Phase 5/6
    # already contains the network_connections column.
    cursor.execute("PRAGMA table_info(system_metrics)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "network_connections" not in existing_columns:
        cursor.execute(
            "ALTER TABLE system_metrics "
            "ADD COLUMN network_connections INTEGER NOT NULL DEFAULT 0"
        )

    if "file_descriptor_count" not in existing_columns:
        cursor.execute(
            "ALTER TABLE system_metrics "
            "ADD COLUMN file_descriptor_count INTEGER NOT NULL DEFAULT 0"
        )

    conn.commit()
    conn.close()


def insert_metrics(
    cpu_percent: float,
    memory_percent: float,
    disk_percent: float,
    process_count: int,
    thread_count: int,
    network_connections: int = 0,
    file_descriptor_count: int = 0
):
    """
    Inserts one system metric snapshot into the database.

    network_connections defaults to 0 for backward compatibility
    with code written before Phase 7.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO system_metrics
        (timestamp, cpu_percent, memory_percent, disk_percent,
         process_count, thread_count, network_connections, file_descriptor_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        cpu_percent,
        memory_percent,
        disk_percent,
        process_count,
        thread_count,
        network_connections,
        file_descriptor_count

    ))

    conn.commit()
    conn.close()


def get_recent_metrics(limit: int = 50) -> list[dict]:
    """
    Returns the most recent metric snapshots, oldest first.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM system_metrics
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in reversed(rows)]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")
