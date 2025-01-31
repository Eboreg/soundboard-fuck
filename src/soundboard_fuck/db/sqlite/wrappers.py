import logging
import sqlite3
from typing import Any, Callable, Generic, TypeVar


_T = TypeVar("_T")
logger = logging.getLogger(__name__)


class ExecuteWrapper(Generic[_T]):
    con: sqlite3.Connection | None = None

    def __init__(self, db_name: str, operation: Callable[[sqlite3.Connection], _T], row_factory: Any | None = None):
        self.db_name = db_name
        self.operation = operation
        self.row_factory = row_factory

    def __enter__(self) -> _T:
        self.con = sqlite3.connect(self.db_name)
        if self.row_factory:
            self.con.row_factory = self.row_factory
        return self.operation(self.con)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            logger.error(str(exc_value))
        if self.con:
            self.con.close()


class FetchAllWrapper(ExecuteWrapper[list[_T]]):
    def __init__(
        self,
        db_name,
        sql: str,
        parameters: "sqlite3._Parameters | None" = None,
        row_factory: Any | None = None,
    ):
        self.sql = sql
        self.parameters = parameters
        super().__init__(db_name, self.execute, row_factory)

    def execute(self, conn: sqlite3.Connection):
        cursor = conn.execute(self.sql, self.parameters or tuple())
        return cursor.fetchall()


class FetchOneWrapper(ExecuteWrapper[_T | None]):
    def __init__(
        self,
        db_name,
        sql: str,
        parameters: "sqlite3._Parameters | None" = None,
        row_factory: Any | None = None,
    ):
        self.sql = sql
        self.parameters = parameters
        super().__init__(db_name, self.execute, row_factory)

    def execute(self, conn: sqlite3.Connection):
        cursor = conn.execute(self.sql, self.parameters or tuple())
        return cursor.fetchone()
