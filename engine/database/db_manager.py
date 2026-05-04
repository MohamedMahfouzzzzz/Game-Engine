"""SQLite database management with connection pooling."""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, Any, List, Dict, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import queue


@dataclass
class DatabaseConfig:
    """Configuration for database."""

    db_path: str
    pool_size: int = 5
    timeout: float = 30.0
    check_same_thread: bool = False
    enable_wal: bool = True


class ConnectionPool:
    """Simple connection pool for SQLite."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: queue.Queue = queue.Queue(maxsize=config.pool_size)
        self.lock = threading.Lock()

        # Initialize pool with connections
        for _ in range(config.pool_size):
            conn = self._create_connection()
            self.pool.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """Create new database connection."""
        conn = sqlite3.connect(
            self.config.db_path,
            timeout=self.config.timeout,
            check_same_thread=self.config.check_same_thread
        )
        conn.row_factory = sqlite3.Row
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """Get connection from pool."""
        try:
            return self.pool.get(timeout=self.config.timeout)
        except queue.Empty:
            # Create new connection if pool exhausted
            return self._create_connection()

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """Return connection to pool."""
        try:
            self.pool.put(conn, block=False)
        except queue.Full:
            conn.close()


class DatabaseManager:
    """Manages SQLite database for game saves and data."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / ".engine" / "game.db"

        config = DatabaseConfig(str(self.db_path))
        self.config = config
        self.pool = ConnectionPool(config)

        # Initialize database
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database schema."""
        schema_file = self.project_path / ".engine" / "schema.sql"

        if schema_file.exists():
            with open(schema_file, 'r') as f:
                schema = f.read()
            self.execute_script(schema)

    @contextmanager
    def get_connection(self):
        """Context manager for database connection."""
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            self.pool.return_connection(conn)

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute query and return cursor."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def execute_script(self, script: str) -> None:
        """Execute SQL script."""
        with self.get_connection() as conn:
            conn.executescript(script)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert row and return ID."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        cursor = self.execute(query, tuple(data.values()))
        return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: str,
               where_params: tuple = ()) -> int:
        """Update rows."""
        assignments = ", ".join(f"{k}=?" for k in data.keys())
        query = f"UPDATE {table} SET {assignments} WHERE {where}"

        params = tuple(data.values()) + where_params
        cursor = self.execute(query, params)
        return cursor.rowcount

    def delete(self, table: str, where: str, where_params: tuple = ()) -> int:
        """Delete rows."""
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.execute(query, where_params)
        return cursor.rowcount

    def count(self, table: str, where: str = "", where_params: tuple = ()) -> int:
        """Count rows in table."""
        if where:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {where}"
            params = where_params
        else:
            query = f"SELECT COUNT(*) as count FROM {table}"
            params = ()

        result = self.fetch_one(query, params)
        return result['count'] if result else 0

    def transaction(self):
        """Context manager for transactions."""
        return TransactionContext(self)

    def vacuum(self) -> None:
        """Optimize database."""
        self.execute("VACUUM")

    def close(self) -> None:
        """Close all connections."""
        while not self.pool.pool.empty():
            try:
                conn = self.pool.pool.get_nowait()
                conn.close()
            except queue.Empty:
                break


class TransactionContext:
    """Context manager for database transactions."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.conn = None

    def __enter__(self) -> sqlite3.Connection:
        """Enter transaction."""
        self.conn = self.db_manager.pool.get_connection()
        self.conn.execute("BEGIN")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction."""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.db_manager.pool.return_connection(self.conn)
