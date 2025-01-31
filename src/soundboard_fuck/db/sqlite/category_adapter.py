from typing import TypedDict, TYPE_CHECKING

from soundboard_fuck.db.sqlite.adapter import SqliteAdapter
from soundboard_fuck.db.sqlite.sql_column import SqlColumn, SqlType
from soundboard_fuck.ui.colors import ColorScheme


if TYPE_CHECKING:
    from soundboard_fuck.data.category import Category


class CategoryColumns(TypedDict):
    id: SqlColumn[int | None]
    name: SqlColumn[str]
    order: SqlColumn[int]
    colors: SqlColumn[ColorScheme]
    is_default: SqlColumn[bool]
    is_expanded: SqlColumn[bool]
    sound_count: SqlColumn[int]
    duration_ms: SqlColumn[int]


class CategoryAdapter(SqliteAdapter["Category"]):
    table_name = "categories"
    columns = [
        SqlColumn[int | None]("id", SqlType.INTEGER, primary_key=True, auto_increment=True),
        SqlColumn[str]("name", SqlType.VARCHAR, not_null=True),
        SqlColumn[int]("order", SqlType.INTEGER, default=0, not_null=True),
        SqlColumn[ColorScheme]("colors", SqlType.VARCHAR, ColorScheme, ColorScheme.BLUE, not_null=True),
        SqlColumn[bool](
            name="is_default",
            sql_type=SqlType.INTEGER,
            type_=bool,
            default=False,
            not_null=True,
            is_derived=True,
            select_stmt="EXISTS(SELECT * FROM meta WHERE default_category = categories.id)",
        ),
        SqlColumn[bool]("is_expanded", SqlType.INTEGER, bool, True, not_null=True),
        SqlColumn[int](
            name="sound_count",
            sql_type=SqlType.INTEGER,
            default=0,
            not_null=True,
            is_derived=True,
            select_stmt="COUNT(sounds.id)",
        ),
        SqlColumn[int](
            name="duration_ms",
            sql_type=SqlType.INTEGER,
            default=0,
            not_null=True,
            is_derived=True,
            select_stmt="TOTAL(sounds.duration_ms)",
        ),
    ]
    column_dict = {c.name: c for c in columns}

    def _get_model_class(self):
        from soundboard_fuck.data.category import Category
        return Category

    def _get_select_stmt(self, where, order_by="", columns=None):
        return self._trim(
            f"""
            SELECT {self._get_select_columns(columns)}
            FROM categories LEFT JOIN sounds ON categories.id = sounds.category_id
            {where} GROUP BY categories.id {order_by}
            """
        )

    def insert(self, record):
        self.db.execute(
            "UPDATE categories SET `order` = `order` + 1 WHERE "
            f"`order` >= {record.order} AND "
            f"EXISTS(SELECT * FROM categories WHERE `order` = {record.order})"
        )
        return super().insert(record)

    def update(self, record, **changes):
        self.db.execute(
            "UPDATE categories SET `order` = `order` + 1 WHERE "
            f"`order` >= {record.order} AND id != {record.id} AND "
            f"EXISTS(SELECT * FROM categories WHERE `order` = {record.order} AND id != {record.id})"
        )
        return super().update(record, **changes)
