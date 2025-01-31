from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Self

from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.enums import RepressMode


if TYPE_CHECKING:
    from soundboard_fuck.data.meta import Meta
    from soundboard_fuck.data.category import Category
    from soundboard_fuck.data.category_with_sounds import CategoryWithSounds
    from soundboard_fuck.data.sound import Sound


class AbstractState(ABC):
    _listeners: list[Callable[[str, Any], Any]]

    def __init__(self):
        self._listeners = []

    def __setattr__(self, name: str, value: Any):
        if not name.startswith("_") and hasattr(self, name):
            old_value = getattr(self, name)
            super().__setattr__(name, value)
            if not name.startswith("_") and old_value != value:
                self.on_value_change(name, value)
                for listener in self._listeners:
                    listener(name, value)
        else:
            super().__setattr__(name, value)

    def on_change(self, listener: Callable[[str, Any], Any]) -> Self:
        self._listeners.append(listener)
        return self

    def on_value_change(self, name: str, value: Any):
        ...


class State(AbstractState):
    query: str = ""
    show_help: bool = False
    show_sound_batch_edit: bool = False
    selected_sound_id: int | None = None
    selected_category_id: int | None = None
    selected_sounds: "set[Sound]"
    categories_with_sounds: "list[CategoryWithSounds]"
    meta: "Meta"
    _resize_listeners: list[Callable]

    @property
    def selected_category(self) -> "Category | None":
        try:
            return [
                cws.category for cws in self.categories_with_sounds
                if cws.category.id == self.selected_category_id
            ][0]
        except IndexError:
            return None

    @property
    def selected_sound(self) -> "Sound | None":
        try:
            return [s for cws in self.categories_with_sounds for s in cws.sounds if s.id == self.selected_sound_id][0]
        except IndexError:
            return None

    @property
    def max_category_order(self) -> int:
        orders = [cws.category.order for cws in self.categories_with_sounds]
        return max(orders, default=-1)

    def __init__(self, db: AbstractDb):
        super().__init__()
        self._db = db
        self._db.on_change(self.on_db_change)
        self._resize_listeners = []
        self.selected_sounds = set()
        self.categories_with_sounds = self._db.list_categories_with_sounds()
        self.meta = self._db.meta_adapter.get()

    def add_resize_listener(self, listener: Callable):
        self._resize_listeners.append(listener)

    def cycle_repress_mode(self):
        repress_mode = self.meta.repress_mode
        if repress_mode == RepressMode.STOP:
            repress_mode = RepressMode.RESTART
        elif repress_mode == RepressMode.RESTART:
            repress_mode = RepressMode.OVERDUB
        elif repress_mode == RepressMode.OVERDUB:
            repress_mode = RepressMode.STOP
        self._db.meta_adapter.update(self.meta, repress_mode=repress_mode)

    def list_categories(self) -> "list[Category]":
        return [cws.category for cws in self.categories_with_sounds]

    def on_db_change(self, table: str):
        if table in ("sounds", "categories"):
            self.categories_with_sounds = self._db.list_categories_with_sounds(self.query)
        elif table == "meta":
            self.meta = self._db.meta_adapter.get()

    def on_resize(self):
        for listener in self._resize_listeners:
            listener()

    def on_value_change(self, name, value):
        if name == "query":
            self.categories_with_sounds = self._db.list_categories_with_sounds(value)
