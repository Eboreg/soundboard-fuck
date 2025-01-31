import curses

from soundboard_fuck.data.category import Category
from soundboard_fuck.ui.base.form_element import FormElement
from soundboard_fuck.ui.base.select import Select


class CategorySelect(Select[Category], FormElement[Category]):
    label = "Category"

    def print_option_label(self, option, window, x, y, width):
        label_width = width - 2
        label = f" {option.name}"
        color = curses.color_pair(option.colors.value.selected)
        window.addstr(y, x, "  ", color)
        window.addstr(y, x + 2, f"{label:{label_width}.{label_width}s}")
