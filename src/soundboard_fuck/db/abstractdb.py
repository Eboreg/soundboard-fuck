from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from soundboard_fuck.data.category_with_sounds import CategoryWithSounds
from soundboard_fuck.db.base.adapter import DbAdapter
from soundboard_fuck.ui.colors import ColorScheme


if TYPE_CHECKING:
    from soundboard_fuck.data.meta import Meta
    from soundboard_fuck.data.category import Category
    from soundboard_fuck.data.sound import Sound


class AbstractDb(ABC):
    _listeners: list[Callable[[str], Any]]
    category_adapter: DbAdapter["Category"]
    meta_adapter: DbAdapter["Meta"]
    sound_adapter: DbAdapter["Sound"]

    def __init__(self):
        self._listeners = []

    @abstractmethod
    def filter_sounds(self, query: str) -> "list[Sound]":
        ...

    @abstractmethod
    def list_categories(self) -> "list[Category]":
        ...

    @abstractmethod
    def list_sounds(self) -> "list[Sound]":
        ...

    @abstractmethod
    def set_default_category(self, category_id: int | None):
        ...

    def copy_sound_to_wav(self, sound: "Sound"):
        if sound.format != "wav":
            new_path = sound.copy_to_wav()
            self.sound_adapter.update(sound, path=new_path)

    def get_default_category(self) -> "Category | None":
        for category in self.list_categories():
            if category.is_default:
                return category
        return None

    def get_or_create_default_category(self) -> "Category":
        from soundboard_fuck.data.category import Category

        category = self.get_default_category()
        if category:
            return category
        category = self.category_adapter.insert(Category(name="Default", order=0, colors=ColorScheme.BLUE))
        assert category.id is not None
        self.set_default_category(category.id)
        return self.category_adapter.get(id=category.id)

    def list_categories_with_sounds(self, query: str = "") -> "list[CategoryWithSounds]":
        if query:
            return [CategoryWithSounds(None, self.filter_sounds(query))]

        categories = self.list_categories()
        sounds = self.list_sounds()

        return [c.with_sounds([s for s in sounds if s.category_id == c.id]) for c in categories]

    def notify_listeners(self, *table: str):
        for listener in self._listeners:
            for t in table:
                listener(t)

    def on_change(self, listener: Callable[[str], Any]):
        self._listeners.append(listener)
