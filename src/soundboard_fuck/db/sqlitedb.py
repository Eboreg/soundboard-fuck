from soundboard_fuck.data.category import Category
from soundboard_fuck.data.meta import Meta
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.db.sqlite.category_adapter import CategoryAdapter
from soundboard_fuck.db.sqlite.comparison import Like
from soundboard_fuck.db.sqlite.meta_adapter import MetaAdapter
from soundboard_fuck.db.sqlite.mixin import SqliteMixin
from soundboard_fuck.db.sqlite.sound_adapter import SoundAdapter


class SqliteDb(SqliteMixin, AbstractDb):
    db_name = "soundboard.sqlite3"
    db_version = 10
    category_adapter: CategoryAdapter
    sound_adapter: SoundAdapter
    meta_adapter: MetaAdapter

    def __init__(self):
        super().__init__()
        self.category_adapter = CategoryAdapter(self)
        self.sound_adapter = SoundAdapter(self)
        self.meta_adapter = MetaAdapter(self)
        actual_version = self.check_actual_version()
        if actual_version != self.db_version:
            cat_version = actual_version
            sound_version = actual_version
            meta_version = actual_version
            while cat_version < self.db_version:
                cat_version = self.migrate_categories(cat_version)
            while sound_version < self.db_version:
                sound_version = self.migrate_sounds(sound_version)
            while meta_version < self.db_version:
                meta_version = self.migrate_meta(meta_version)
            try:
                meta = self.meta_adapter.get()
                self.meta_adapter.update(meta, db_version=self.db_version)
            except Exception:
                self.meta_adapter.insert(Meta(db_version=self.db_version))
            self.get_or_create_default_category()

    def check_actual_version(self) -> int:
        try:
            return self.meta_adapter.get_column(self.meta_adapter.column_dict["db_version"])
        except Exception:
            return 0

    def filter_sounds(self, query):
        if query:
            return self.sound_adapter.list(
                order_by=["sounds.play_count DESC", "LOWER(sounds.name)"],
                name__lower=Like(f"%{query.lower()}%"),
            )
        return self.list_sounds()

    def list_categories(self):
        return self.category_adapter.list(order_by=["categories.`order`"])

    def list_sounds(self):
        return self.sound_adapter.list(order_by=["LOWER(sounds.name)"])

    def migrate_categories(self, from_version: int) -> int:
        if from_version in (5, 6):
            self.execute("ALTER TABLE categories DROP COLUMN is_default")
            return 7

        if from_version == 4:
            column = self.category_adapter.column_dict["is_expanded"]
            stmt = column.create_stmt()
            self.execute(f"ALTER TABLE categories ADD COLUMN {stmt}")
            return 6

        if from_version == 3:
            column = self.category_adapter.column_dict["colors"]
            stmt = column.create_stmt()
            self.execute(f"ALTER TABLE categories ADD COLUMN {stmt}")
            return 4

        if from_version == 2:
            categories = self.list_categories()

            self.execute("DROP TABLE categories")
            self.category_adapter.create_table()

            default_cat = self.get_or_create_default_category()
            if default_cat not in categories:
                categories.append(default_cat)

            self.category_adapter.bulk_insert(categories)
            return self.db_version

        if from_version <= 1:
            self.category_adapter.create_table()
            return self.db_version

        return self.db_version

    def migrate_sounds(self, from_version: int) -> int:
        if from_version == 2:
            sounds = self.list_sounds()
            categories = self.list_categories()

            self.execute("DROP TABLE sounds")
            self.sound_adapter.create_table()

            default_cat = self.get_or_create_default_category()
            for sound in sounds:
                if sound.category_id is None or sound.category_id not in [c.id for c in categories]:
                    sound.category_id = default_cat.id

            self.sound_adapter.bulk_insert(sounds)
            return self.db_version

        if from_version <= 1:
            self.sound_adapter.create_table()
            return self.db_version

        return self.db_version

    def migrate_meta(self, from_version: int) -> int:
        if from_version == 9:
            column = self.meta_adapter.get_column_definition("convert_to_wav")
            stmt = column.create_stmt()
            self.execute(f"ALTER TABLE meta ADD COLUMN {stmt}")
            return 10

        if from_version == 8:
            meta = self.meta_adapter.get(columns=["db_version", "repress_mode", "default_category"])
            self.execute("DROP TABLE meta")
            self.meta_adapter.create_table()
            self.meta_adapter.insert(meta)
            return self.db_version

        if from_version == 7:
            column = self.meta_adapter.get_column_definition("repress_mode")
            stmt = column.create_stmt()
            self.execute(f"ALTER TABLE meta ADD COLUMN {stmt}")
            return 8

        if from_version in (5, 6):
            self.execute("DROP TABLE meta")
            self.meta_adapter.create_table()
            category: Category | None = None

            try:
                category = self.category_adapter.get(is_default=True)
            except Exception:
                pass

            self.meta_adapter.insert(
                Meta(
                    db_version=6,
                    default_category=category.id if category else None,
                )
            )
            return self.db_version

        if from_version < 5:
            self.meta_adapter.create_table()
            self.meta_adapter.insert(Meta(db_version=self.db_version))
            return self.db_version

        return self.db_version

    def set_default_category(self, category_id):
        meta = self.meta_adapter.get()
        if self.meta_adapter.update(meta, default_category=category_id):
            self.notify_listeners("categories", "meta")
