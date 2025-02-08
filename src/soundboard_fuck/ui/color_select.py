from soundboard_fuck.ui.base.elements.select import Select
from soundboard_fuck.ui.colors import ColorScheme


class ColorSelect(Select[ColorScheme]):
    label = "Colour"

    def print_option_label(self, option, window, x, y, width):
        label_width = width - 2
        label = f" {option.value.label}"
        color = option.value.selected.color_pair()
        window.addstr(y, x, "  ", color)
        window.addstr(y, x + 2, f"{label:{label_width}.{label_width}s}")
