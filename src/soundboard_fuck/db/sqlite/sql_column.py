import enum
from dataclasses import dataclass
from typing import Any, Generic, TypeVar


_T = TypeVar("_T")


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


class Nothing:
    ...


@dataclass
class SqlColumn(Generic[_T]):
    name: str
    sql_type: SqlType
    type_: type[_T] = Nothing
    default: Any = Nothing
    primary_key: bool = False
    auto_increment: bool = False
    not_null: bool = False
    is_derived: bool = False
    references: tuple[str, str] | None = None
    on_delete: ForeignKeyAction | None = None
    on_update: ForeignKeyAction | None = None
    select_stmt: str | None = None

    def __post_init__(self):
        if self.type_ is Nothing:
            if self.sql_type == SqlType.INTEGER:
                self.type_ = int
            elif self.sql_type == SqlType.REAL:
                self.type_ = float
            elif self.sql_type in (SqlType.TEXT, SqlType.VARCHAR):
                self.type_ = str
            elif self.sql_type == SqlType.BLOB:
                self.type_ = bytes

    @property
    def has_default(self):
        return self.default is not Nothing

    def create_stmt(self) -> str:
        stmt = f"`{self.name}` {self.sql_type}"
        if self.primary_key:
            stmt += " PRIMARY KEY"
        if self.auto_increment:
            stmt += " AUTOINCREMENT"
        if self.not_null:
            stmt += " NOT NULL"
        if isinstance(self.default, str):
            stmt += f" DEFAULT '{self.default}'"
        elif self.default is None:
            stmt += " DEFAULT NULL"
        elif self.default is not Nothing:
            stmt += f" DEFAULT {self.value_to_sql(self.default)}"
        if self.references:
            stmt += f" REFERENCES {self.references[0]} ({self.references[1]})"
            if self.on_delete:
                stmt += f" ON DELETE {self.on_delete}"
            if self.on_update:
                stmt += f" ON UPDATE {self.on_update}"
        return stmt

    def get_select_stmt(self) -> str:
        return self.select_stmt or self.name

    def sql_to_value(self, sql: Any) -> _T:
        if sql == "NULL":
            return None
        if issubclass(self.type_, enum.Enum):
            # pylint: disable=unsubscriptable-object
            return self.type_[sql]
        return self.type_(sql)

    def value_to_sql(self, value: _T, quote: bool = False):
        if value is None:
            if not self.not_null:
                return "NULL"
            raise ValueError(f"{self.name} cannot be null")

        if self.sql_type == SqlType.INTEGER and isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, enum.Enum):
            value = value.name
        elif self.sql_type in (SqlType.VARCHAR, SqlType.TEXT):
            value = str(value)

        if isinstance(value, str) and quote:
            return f"'{value}'"
        return value
