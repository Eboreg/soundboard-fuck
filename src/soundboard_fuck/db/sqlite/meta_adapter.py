from typing import TYPE_CHECKING, TypedDict

from soundboard_fuck.db.sqlite.adapter import SqliteAdapter
from soundboard_fuck.db.sqlite.sql_column import (
    ForeignKeyAction,
    SqlColumn,
    SqlType,
)
from soundboard_fuck.enums import RepressMode


if TYPE_CHECKING:
    from soundboard_fuck.data.meta import Meta


class MetaColumns(TypedDict):
    id: SqlColumn[int | None]
    db_version: SqlColumn[int]
    default_category: SqlColumn[int | None]
    repress_mode: SqlColumn[RepressMode]


class MetaAdapter(SqliteAdapter["Meta"]):
    table_name = "meta"
    columns = [
        SqlColumn[int | None]("id", SqlType.INTEGER, primary_key=True, auto_increment=True),
        SqlColumn[int](name="db_version", sql_type=SqlType.INTEGER, not_null=True),
        SqlColumn[int | None](
            name="default_category",
            sql_type=SqlType.INTEGER,
            references=("categories", "id"),
            on_delete=ForeignKeyAction.SET_NULL,
            on_update=ForeignKeyAction.CASCADE,
        ),
        SqlColumn[RepressMode](
            name="repress_mode",
            type_=RepressMode,
            sql_type=SqlType.VARCHAR,
            not_null=True,
            default=RepressMode.STOP
        ),
        SqlColumn[bool](name="convert_to_wav", sql_type=SqlType.INTEGER, type_=bool, default=False, not_null=True),
    ]
    column_dict: MetaColumns = {c.name: c for c in columns}

    def _get_model_class(self):
        from soundboard_fuck.data.meta import Meta
        return Meta

    def insert(self, record):
        self.db.execute("DELETE FROM meta")
        return super().insert(record)
