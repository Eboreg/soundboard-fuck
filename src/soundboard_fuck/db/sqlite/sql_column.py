import enum
from dataclasses import dataclass
from typing import Any


class SqlType(enum.StrEnum):
    INTEGER = "INTEGER"
    VARCHAR = "VARCHAR"
    REAL = "REAL"
    TEXT = "TEXT"
    BLOB = "BLOB"


class ForeignKeyAction(enum.StrEnum):
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


@dataclass
class SqlColumn:
    type: SqlType
    primary_key: bool = False
    auto_increment: bool = False
    not_null: bool = False
    default: Any = None
    references: tuple[str, str] | None = None
    on_delete: ForeignKeyAction | None = None
    on_update: ForeignKeyAction | None = None

    def create_stmt(self, name: str) -> str:
        stmt = f"`{name}` {self.type}"
        if self.primary_key:
            stmt += " PRIMARY KEY"
        if self.auto_increment:
            stmt += " AUTOINCREMENT"
        if self.not_null:
            stmt += " NOT NULL"
        if isinstance(self.default, str):
            stmt += f" DEFAULT '{self.default}'"
        elif self.default is not None:
            stmt += f" DEFAULT {self.default}"
        if self.references:
            stmt += f" REFERENCES {self.references[0]} ({self.references[1]})"
            if self.on_delete:
                stmt += f" ON DELETE {self.on_delete}"
            if self.on_update:
                stmt += f" ON UPDATE {self.on_update}"
        return stmt


IdColumn = SqlColumn(type=SqlType.INTEGER, primary_key=True, auto_increment=True)
