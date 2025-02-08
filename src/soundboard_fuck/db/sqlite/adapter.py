import re
import sqlite3
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from soundboard_fuck.data.model import _M
from soundboard_fuck.db.base.adapter import DbAdapter
from soundboard_fuck.db.sqlite.comparison import Equals
from soundboard_fuck.db.sqlite.expression import Expression
from soundboard_fuck.db.sqlite.wrappers import FetchAllWrapper, FetchOneWrapper


_T = TypeVar("_T")


if TYPE_CHECKING:
    from soundboard_fuck.db.sqlite.sql_column import SqlColumn
    from soundboard_fuck.db.sqlitedb import SqliteDb


class SqliteAdapter(DbAdapter[_M], ABC):
    columns: "list[SqlColumn]"
    column_dict: "dict[str, SqlColumn]"

    def __init__(self, db: "SqliteDb"):
        self.db = db
        super().__init__()

    @abstractmethod
    def _get_model_class(self) -> type[_M]:
        ...

    def _dict_to_record(self, d: dict) -> _M:
        kwargs = {
            k: self.column_dict[k].sql_to_value(v)
            for k, v in d.items()
        }
        return self._get_model_class()(**kwargs)

    def _get_insert_stmt(self):
        column_names = [c.name for c in self.column_dict.values() if not c.auto_increment and not c.is_derived]
        columns = ", ".join(f"`{c}`" for c in column_names)
        values = ", ".join(f":{c}" for c in column_names)
        return f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})"

    def _get_order_by_stmt(self, order_by: list[str] | None) -> str:
        if order_by:
            return "ORDER BY " + ", ".join(order_by)
        return ""

    def _get_select_stmt(self, where: str, order_by: str = "", columns: list[str] | None = None) -> str:
        return self._trim(f"SELECT {self._get_select_columns(columns)} FROM {self.table_name} {where} {order_by}")

    def _get_select_columns(self, only: list[str] | None = None):
        names = []
        for c in self.column_dict.values():
            if only is not None and c.name not in only:
                continue
            if c.is_derived:
                names.append(f"{c.select_stmt} AS {c.name}")
            else:
                names.append(f"{self.table_name}.`{c.name}`")
        return ", ".join(names)

    def _get_where_stmt(self, kwargs: dict[str, Any]):
        expressions = []
        for k, v in kwargs.items():
            expression = Expression(key=k, value=v)
            if expression.key_string in self.column_dict:
                expression.add_prefix(self.table_name)
            expressions.append(expression)
        if expressions:
            return "WHERE " + " AND ".join(str(e) for e in expressions)
        return ""

    def _record_factory(self, cursor: "sqlite3.Cursor", row: tuple) -> _M:
        fields = [c[0] for c in cursor.description]
        d = dict(zip(fields, row))
        return self._dict_to_record(d)

    def _record_to_parameters(self, record: _M) -> "sqlite3._Parameters":  # type: ignore
        parameters = {}

        for column in self.column_dict.values():
            if column.is_derived or (column.name == "id" and record.id is None):
                continue
            parameters[column.name] = column.value_to_sql(getattr(record, column.name))

        return parameters

    def _trim(self, value: str) -> str:
        return re.sub(r" {2,}", " ", value.strip().replace("\n", " "))

    def bulk_insert(self, records: list[_M]):
        parameters = [self._record_to_parameters(r) for r in records]
        self.db.executemany(self._get_insert_stmt(), parameters)
        self.db.notify_listeners(self.table_name)

    def create_table(self):
        column_stmts = ", ".join(c.create_stmt() for c in self.column_dict.values() if not c.is_derived)
        if self.db.sqlite_version_gte(3, 3, 0):
            sql = f"CREATE TABLE IF NOT EXISTS {self.table_name}({column_stmts})"
        else:
            sql = f"CREATE TABLE {self.table_name}({column_stmts})"
        self.db.execute(sql)

    def delete(self, **where):
        sql = f"DELETE FROM {self.table_name} {self._get_where_stmt(where)}"
        self.db.execute(sql)
        self.db.notify_listeners(self.table_name)

    def get(self, columns: list[str] | None = None, **where) -> _M:
        sql = self._get_select_stmt(where=self._get_where_stmt(where), columns=columns)
        with FetchOneWrapper[_M](self.db.db_name, sql, row_factory=self._record_factory) as record:
            assert record is not None
            return record

    def get_column(self, column: "SqlColumn[_T]", **where) -> _T:  # type: ignore
        sql = self._get_select_stmt(where=self._get_where_stmt(where), columns=[column.name])
        with FetchOneWrapper[sqlite3.Row](self.db.db_name, sql, row_factory=sqlite3.Row) as row:
            assert row is not None
            return column.sql_to_value(row[column.name])

    def get_column_definition(self, name: str):
        return self.column_dict[name]

    def insert(self, record: _M) -> _M:
        record_id = self.db.insert_one(self._get_insert_stmt(), self._record_to_parameters(record))
        assert record_id is not None
        self.db.notify_listeners(self.table_name)
        return self.get(id=Equals(record_id))

    def list(self, order_by: list[str] | None = None, columns: list[str] | None = None, **where) -> list[_M]:
        sql = self._get_select_stmt(
            where=self._get_where_stmt(where),
            order_by=self._get_order_by_stmt(order_by),
            columns=columns,
        )
        with FetchAllWrapper[_M](self.db.db_name, sql, row_factory=self._record_factory) as records:
            return records

    def update(self, record: _M, **changes) -> bool:
        changes = {k: v for k, v in changes.items() if getattr(record, k) != v}
        if changes:
            updates = ", ".join(f"`{k}`=:{k}" for k in changes.keys())
            parameters = {k: self.column_dict[k].value_to_sql(v) for k, v in changes.items()}
            sql = f"UPDATE {self.table_name} SET {updates} WHERE id = {record.id}"
            self.db.execute(sql, parameters)
            self.db.notify_listeners(self.table_name)
            return True
        return False
