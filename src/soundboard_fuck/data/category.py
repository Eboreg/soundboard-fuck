from dataclasses import dataclass
from typing import TYPE_CHECKING

from soundboard_fuck.ui.colors import ColorScheme


if TYPE_CHECKING:
    from soundboard_fuck.data.category_with_sounds import CategoryWithSounds
    from soundboard_fuck.data.sound import Sound


@dataclass
class Category:
    id: int
    name: str
    order: int
    colors: ColorScheme
    is_default: bool

    def with_sounds(self, sounds: "list[Sound]") -> "CategoryWithSounds":
        from soundboard_fuck.data.category_with_sounds import (
            CategoryWithSounds,
        )

        return CategoryWithSounds(category=self, sounds=sounds)


test_categories = [
    Category(id=0, name="Default", order=0, is_default=True, colors=ColorScheme.RED),
]
