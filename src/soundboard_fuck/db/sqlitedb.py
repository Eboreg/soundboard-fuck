from pathlib import Path

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.db.sqlite.mixin import SqliteMixin
from soundboard_fuck.db.sqlite.sql_column import (
    ForeignKeyAction,
    IdColumn,
    SqlColumn,
    SqlType,
)
from soundboard_fuck.db.sqlite.wrappers import FetchAllWrapper, FetchOneWrapper
from soundboard_fuck.ui.colors import ColorScheme


class SqliteDb(SqliteMixin, AbstractDb):
    db_name = "soundboard.sqlite3"
    db_version = 4

    def __init__(self):
        super().__init__()
        actual_version = self.check_actual_version()
        if actual_version != self.db_version:
            self.migrate(actual_version)
            self.execute("DELETE FROM meta")
            self.execute(f"INSERT INTO meta (db_version) VALUES ({self.db_version})")

    @property
    def categories_columns(self):
        return {
            "id": IdColumn,
            "name": SqlColumn(type=SqlType.VARCHAR, not_null=True),
            "order": SqlColumn(type=SqlType.INTEGER, not_null=True),
            "is_default": SqlColumn(type=SqlType.INTEGER, not_null=True, default=0),
            "colors": SqlColumn(type=SqlType.VARCHAR, not_null=True, default=ColorScheme.RED.name),
        }

    @property
    def sounds_columns(self):
        return {
            "id": IdColumn,
            "name": SqlColumn(type=SqlType.VARCHAR, not_null=True),
            "path": SqlColumn(type=SqlType.VARCHAR, not_null=True),
            "duration_ms": SqlColumn(type=SqlType.INTEGER),
            "play_count": SqlColumn(type=SqlType.INTEGER, not_null=True, default=0),
            "category_id": SqlColumn(
                not_null=True,
                type=SqlType.INTEGER,
                references=("categories", "id"),
                on_delete=ForeignKeyAction.RESTRICT,
                on_update=ForeignKeyAction.CASCADE,
            ),
        }

    def check_actual_version(self) -> int:
        with FetchOneWrapper(self.db_name, "SELECT db_version FROM meta") as row:
            return row[0] if row else 0

    def create_categories_table(self):
        self.create_table(name="categories", columns=self.categories_columns)

    def create_category(self, name, order, is_default, colors):
        category_id = self.insert_one(
            """
            INSERT INTO categories (name, `order`, is_default, colors)
            VALUES (:name, :order, :is_default, :colors)
            """,
            {
                "name": name,
                "order": order,
                "is_default": self.value_to_sql(is_default, SqlType.INTEGER),
                "colors": self.value_to_sql(colors, SqlType.VARCHAR),
            },
        )
        if category_id is not None:
            self.notify_listeners("categories")
            return self.get_category(category_id)
        return None

    def create_meta_table(self):
        self.create_table(
            name="meta",
            columns={"db_version": SqlColumn(type=SqlType.INTEGER, not_null=True, default=self.db_version)},
        )

    def create_sound(self, name, path, category_id = None, duration_ms = None):
        duration_ms: int | None = duration_ms or Sound.extract_duration_ms(path)
        sound_id = self.insert_one(
            """
            INSERT INTO sounds (name, path, duration_ms, category_id)
            VALUES (:name, :path, :duration_ms, :category_id)
            """,
            {
                "name": name,
                "path": str(path),
                "duration_ms": self.value_to_sql(duration_ms, SqlType.INTEGER),
                "category_id": self.value_to_sql(category_id, SqlType.INTEGER),
            },
        )
        if sound_id is not None:
            self.notify_listeners("sounds")
            return self.get_sound(sound_id)
        return None

    def create_sounds_table(self):
        self.create_table(name="sounds", columns=self.sounds_columns)

    def delete_category(self, category_id):
        self.execute(f"DELETE FROM categories WHERE id={category_id}")
        self.notify_listeners("categories")

    def delete_sound(self, sound_id):
        self.execute(f"DELETE FROM sound WHERE id={sound_id}")
        self.notify_listeners("sounds")

    def filter_sounds(self, query):
        if query:
            sql = f"""
                SELECT s.id, s.name, s.path, s.duration_ms, s.play_count, s.category_id, c.colors
                FROM sounds s LEFT JOIN categories c ON s.category_id = c.id
                WHERE LOWER(s.name) LIKE '%{query.lower()}%'
                ORDER BY s.play_count DESC, LOWER(s.name)
            """
            with FetchAllWrapper(self.db_name, sql) as rows:
                return [self.sql_to_sound(row) for row in rows]
        return self.list_sounds()

    def get_category(self, category_id):
        sql = "SELECT id, name, `order`, is_default, colors FROM categories WHERE id=:id"
        with FetchOneWrapper(self.db_name, sql, {"id": category_id}) as row:
            return self.sql_to_category(row) if row else None

    def get_sound(self, sound_id):
        sql = """
            SELECT s.id, s.name, s.path, s.duration_ms, s.play_count, s.category_id, c.colors
            FROM sounds s LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.id=:id
        """
        with FetchOneWrapper(self.db_name, sql, {"id": sound_id}) as row:
            return self.sql_to_sound(row) if row else None

    def list_categories(self):
        sql = "SELECT id, name, `order`, is_default, colors FROM categories ORDER BY `order`"
        with FetchAllWrapper(self.db_name, sql) as rows:
            return [self.sql_to_category(row) for row in rows]

    def list_sounds(self):
        sql = """
            SELECT s.id, s.name, s.path, s.duration_ms, s.play_count, s.category_id, c.colors
            FROM sounds s LEFT JOIN categories c ON s.category_id = c.id
            ORDER BY LOWER(s.name)
        """
        with FetchAllWrapper(self.db_name, sql) as rows:
            return [self.sql_to_sound(row) for row in rows]

    def migrate(self, from_version: int):
        if from_version == 3:
            stmt = self.categories_columns["colors"].create_stmt("colors")
            self.execute(f"ALTER TABLE categories ADD COLUMN {stmt}")

        elif from_version in (1, 2):
            sounds = self.list_sounds()
            categories = self.list_categories()

            self.execute("DROP TABLE sounds")
            self.execute("DROP TABLE categories")
            self.create_categories_table()
            self.create_sounds_table()

            default_cat = self.get_or_create_default_category()
            assert default_cat is not None
            if default_cat not in categories:
                categories.append(default_cat)
            for sound in sounds:
                if sound.category_id is None or sound.category_id not in [c.id for c in categories]:
                    sound.category_id = default_cat.id

            self.save_categories(*categories)
            self.save_sounds(*sounds)

        elif from_version == 0:
            self.create_meta_table()
            self.create_categories_table()
            self.create_sounds_table()
            self.get_or_create_default_category()

    def save_categories(self, *categories):
        if categories:
            self.executemany(
                """
                INSERT OR REPLACE INTO categories (id, name, `order`, is_default, colors)
                VALUES (:id, :name, :order, :is_default, :colors)
                """,
                [
                    {
                        "id": c.id,
                        "name": c.name,
                        "order": c.order,
                        "is_default": self.value_to_sql(c.is_default, SqlType.INTEGER),
                        "colors": self.value_to_sql(c.colors, SqlType.VARCHAR),
                    } for c in categories
                ],
            )
            self.notify_listeners("categories")

    def save_sounds(self, *sounds):
        if sounds:
            self.executemany(
                """
                INSERT OR REPLACE INTO sounds (id, name, path, duration_ms, play_count, category_id)
                VALUES (:id, :name, :path, :duration_ms, :play_count, :category_id)
                """,
                [
                    {
                        "id": s.id,
                        "name": s.name,
                        "path": str(s.path),
                        "duration_ms": self.value_to_sql(s.duration_ms, SqlType.INTEGER),
                        "play_count": s.play_count,
                        "category_id": self.value_to_sql(s.category_id, SqlType.INTEGER),
                    } for s in sounds
                ],
            )
            self.notify_listeners("sounds")

    def sql_to_category(self, row: tuple) -> Category:
        return Category(
            id=row[0],
            name=row[1],
            order=row[2],
            is_default=self.value_to_python(row[3], bool),
            colors=self.value_to_python(row[4], ColorScheme),
        )

    def sql_to_sound(self, row: tuple):
        return Sound(
            id=row[0],
            name=row[1],
            path=self.value_to_python(row[2], Path),
            duration_ms=self.value_to_python(row[3], int),
            play_count=row[4],
            category_id=self.value_to_python(row[5], int),
            colors=self.value_to_python(row[6], ColorScheme),
        )
