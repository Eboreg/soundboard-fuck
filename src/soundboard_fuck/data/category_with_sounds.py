from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from soundboard_fuck.data.category import Category
    from soundboard_fuck.data.sound import Sound


@dataclass
class CategoryWithSounds:
    category: "Category | None"
    sounds: "list[Sound]"
