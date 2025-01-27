import logging
import sqlite3
from enum import Enum
from typing import Any, TypeVar

from soundboard_fuck.db.sqlite.sql_column import SqlColumn, SqlType
from soundboard_fuck.db.sqlite.wrappers import FetchOneWrapper


_T = TypeVar("_T")
logger = logging.getLogger(__name__)


class SqliteMixin:
    db_name: str

    def create_table(self, name: str, columns: dict[str, SqlColumn]):
        column_stmts = ", ".join(v.create_stmt(k) for k, v in columns.items())
        if self.sqlite_version_gte(3, 3, 0):
            sql = f"CREATE TABLE IF NOT EXISTS {name}({column_stmts})"
        else:
            sql = f"CREATE TABLE {name}({column_stmts})"
        self.execute(sql)

    def execute(self, query: str, parameters: "sqlite3._Parameters | None" = None):
        con = sqlite3.connect(self.db_name)

        try:
            con.execute(query, parameters or tuple())
            con.commit()
        except Exception as e:
            logger.error(str(e))
        finally:
            con.close()

    def executemany(self, sql: str, parameters: "list[sqlite3._Parameters] | None" = None):
        con = sqlite3.connect(self.db_name)

        try:
            con.executemany(sql, parameters or [])
            con.commit()
        except Exception as e:
            logger.error(str(e))
        finally:
            con.close()

    def get_last_insert_rowid(self) -> int | None:
        with FetchOneWrapper(self.db_name, "SELECT last_insert_rowid()") as row:
            if row:
                return row[0]
        return None

    def insert_one(self, sql: str, parameters: "sqlite3._Parameters | None" = None) -> int | None:
        con = sqlite3.connect(self.db_name)

        try:
            con.execute(sql, parameters or tuple())
            con.commit()
            cursor = con.execute("SELECT last_insert_rowid()")
            row = cursor.fetchone()
            if row:
                return row[0]
        except Exception as e:
            logger.error(str(e))
        finally:
            con.close()

        return None

    def sqlite_version_gte(self, major: int, minor: int, patch: int) -> bool:
        actual = sqlite3.sqlite_version_info
        if actual[0] > major:
            return True
        if actual[0] == major:
            if actual[1] > minor:
                return True
            return actual[1] == minor and actual[2] >= patch
        return False

    def value_to_python(self, value: Any, type_: type[_T]) -> _T | None:
        if value == "NULL":
            return None
        if issubclass(type_, Enum):
            return type_[value]
        return type_(value)

    def value_to_sql(self, value: Any, type_: SqlType):
        if value is None:
            return "NULL"
        if type_ == SqlType.INTEGER and isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, Enum):
            return value.name
        return value
