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
    is_expanded: bool
    sound_count: int
    duration_ms: int

    def copy(
        self,
        name: str | None = None,
        order: int | None = None,
        colors: ColorScheme | None = None,
        is_expanded: bool | None = None,
    ):
        return Category(
            id=self.id,
            is_default=self.is_default,
            name=name if name is not None else self.name,
            order=order if order is not None else self.order,
            colors=colors if colors is not None else self.colors,
            is_expanded=is_expanded if is_expanded is not None else self.is_expanded,
            sound_count=self.sound_count,
            duration_ms=self.duration_ms,
        )

    def with_sounds(self, sounds: "list[Sound]") -> "CategoryWithSounds":
        from soundboard_fuck.data.category_with_sounds import (
            CategoryWithSounds,
        )

        return CategoryWithSounds(category=self, sounds=sounds)


test_categories = [
    Category(
        id=0,
        name="Default",
        order=0,
        is_default=True,
        colors=ColorScheme.RED,
        is_expanded=True,
        sound_count=0,
        duration_ms=0,
    ),
]
