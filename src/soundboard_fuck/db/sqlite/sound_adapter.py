from pathlib import Path
from typing import TypedDict, TYPE_CHECKING

from soundboard_fuck.db.sqlite.adapter import SqliteAdapter
from soundboard_fuck.db.sqlite.sql_column import ForeignKeyAction, SqlColumn, SqlType
from soundboard_fuck.ui.colors import ColorScheme


if TYPE_CHECKING:
    from soundboard_fuck.data.sound import Sound


class SoundColumns(TypedDict):
    id: SqlColumn[int | None]
    name: SqlColumn[str]
    path: SqlColumn[Path]
    category_id: SqlColumn[int]
    duration_ms: SqlColumn[int | None]
    colors: SqlColumn[ColorScheme]
    play_count: SqlColumn[int]


class SoundAdapter(SqliteAdapter["Sound"]):
    table_name = "sounds"
    columns = [
        SqlColumn[int | None]("id", SqlType.INTEGER, primary_key=True, auto_increment=True),
        SqlColumn[str]("name", SqlType.VARCHAR, not_null=True),
        SqlColumn[Path]("path", SqlType.VARCHAR, Path, not_null=True),
        SqlColumn[int](
            "category_id",
            SqlType.INTEGER,
            not_null=True,
            references=("categories", "id"),
            on_delete=ForeignKeyAction.RESTRICT,
            on_update=ForeignKeyAction.CASCADE,
        ),
        SqlColumn[int | None]("duration_ms", SqlType.INTEGER, default=None),
        SqlColumn[ColorScheme](
            name="colors",
            sql_type=SqlType.VARCHAR,
            type_=ColorScheme,
            default=ColorScheme.BLUE,
            not_null=True,
            is_derived=True,
            select_stmt="categories.colors",
        ),
        SqlColumn[int]("play_count", SqlType.INTEGER, default=0, not_null=True),
    ]
    column_dict: SoundColumns = {c.name: c for c in columns}

    def _get_model_class(self):
        from soundboard_fuck.data.sound import Sound
        return Sound

    def _get_select_stmt(self, where, order_by="", columns=None):
        return self._trim(
            f"""
            SELECT {self._get_select_columns(columns)}
            FROM sounds LEFT JOIN categories ON sounds.category_id = categories.id
            {where} {order_by}
            """
        )
