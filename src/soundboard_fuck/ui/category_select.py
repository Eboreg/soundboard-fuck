from soundboard_fuck.data.category import Category
from soundboard_fuck.ui.base.elements.select import Select


class CategorySelect(Select[Category]):
    label = "Category"

    def print_option_label(self, option, window, x, y, width):
        label_width = width - 2
        label = f" {option.name}"
        color = option.colors.value.selected.color_pair()
        window.addstr(y, x, "  ", color)
        window.addstr(y, x + 2, f"{label:{label_width}.{label_width}s}")
