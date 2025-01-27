import logging
import sqlite3
from typing import Callable, Generic, TypeVar


_T = TypeVar("_T")
logger = logging.getLogger(__name__)


class ExecuteWrapper(Generic[_T]):
    con: sqlite3.Connection | None = None

    def __init__(self, db_name: str, operation: Callable[[sqlite3.Connection], _T]):
        self.db_name = db_name
        self.operation = operation

    def __enter__(self) -> _T:
        try:
            self.con = sqlite3.connect(self.db_name)
            return self.operation(self.con)
        except Exception as e:
            logger.error(str(e))
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            logger.error(str(exc_value))
        if self.con:
            self.con.close()


class FetchAllWrapper(ExecuteWrapper[list[tuple]]):
    def __init__(self, db_name, sql: str, parameters: "sqlite3._Parameters | None" = None):
        self.sql = sql
        self.parameters = parameters
        super().__init__(db_name, self.execute)

    def execute(self, conn: sqlite3.Connection):
        cursor = conn.execute(self.sql, self.parameters or tuple())
        return cursor.fetchall()


class FetchOneWrapper(ExecuteWrapper[tuple | None]):
    def __init__(self, db_name, sql: str, parameters: "sqlite3._Parameters | None" = None):
        self.sql = sql
        self.parameters = parameters
        super().__init__(db_name, self.execute)

    def execute(self, conn: sqlite3.Connection):
        cursor = conn.execute(self.sql, self.parameters or tuple())
        return cursor.fetchone()
