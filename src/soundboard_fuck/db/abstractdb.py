from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from soundboard_fuck.data.category_with_sounds import CategoryWithSounds
from soundboard_fuck.enums import RepressMode
from soundboard_fuck.ui.colors import ColorScheme


if TYPE_CHECKING:
    from soundboard_fuck.data.category import Category
    from soundboard_fuck.data.sound import Sound


class AbstractDb(ABC):
    _listeners: list[Callable[[str], Any]]

    def __init__(self):
        self._listeners = []

    @abstractmethod
    def create_category(
        self,
        name: str,
        order: int,
        colors: ColorScheme,
        is_expanded: bool,
    ) -> "Category":
        ...

    @abstractmethod
    def create_sound(
        self,
        name: str,
        path: Path,
        category_id: int | None = None,
        duration_ms: int | None = None,
    ) -> "Sound":
        ...

    @abstractmethod
    def delete_category(self, category_id: int):
        ...

    @abstractmethod
    def delete_sound(self, sound_id: int):
        ...

    @abstractmethod
    def filter_sounds(self, query: str) -> "list[Sound]":
        ...

    @abstractmethod
    def get_category(self, category_id: int) -> "Category":
        ...

    def get_default_category(self) -> "Category | None":
        for category in self.list_categories():
            if category.is_default:
                return category
        return None

    def get_or_create_default_category(self) -> "Category":
        category = self.get_default_category()
        if category:
            return category
        category = self.create_category("Default", 0, ColorScheme.RED, True)
        self.set_default_category(category.id)
        return self.get_category(category.id)

    @abstractmethod
    def get_repress_mode(self) -> RepressMode:
        ...

    @abstractmethod
    def get_sound(self, sound_id: int) -> "Sound":
        ...

    @abstractmethod
    def list_categories(self) -> "list[Category]":
        ...

    def list_categories_with_sounds(self, query: str = "") -> "list[CategoryWithSounds]":
        if query:
            return [CategoryWithSounds(None, self.filter_sounds(query))]

        categories = self.list_categories()
        sounds = self.list_sounds()

        return [c.with_sounds([s for s in sounds if s.category_id == c.id]) for c in categories]

    @abstractmethod
    def list_sounds(self) -> "list[Sound]":
        ...

    def notify_listeners(self, table: str):
        for listener in self._listeners:
            listener(table)

    def on_change(self, listener: Callable[[str], Any]):
        self._listeners.append(listener)

    @abstractmethod
    def save_categories(self, *categories: "Category"):
        ...

    @abstractmethod
    def save_sounds(self, *sounds: "Sound"):
        ...

    @abstractmethod
    def set_default_category(self, category_id: int | None):
        ...

    @abstractmethod
    def set_repress_mode(self, value: RepressMode):
        ...
