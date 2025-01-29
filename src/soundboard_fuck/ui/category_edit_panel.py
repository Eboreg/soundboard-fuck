import curses
import curses.ascii

from soundboard_fuck.data.category import Category
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.button import Button
from soundboard_fuck.ui.base.checkbox import Checkbox
from soundboard_fuck.ui.base.form_panel import FormPanel
from soundboard_fuck.ui.base.input import Input
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.color_select import ColorSelect


class CategoryEditPanel(FormPanel, AbstractPanel):
    create_hidden = True
    border = True
    category: Category | None = None
    name: str
    order: int
    is_default: bool
    color_scheme: colors.ColorScheme

    def __init__(self, state, db: AbstractDb, border=None, z_index=None):
        self.db = db
        super().__init__(state, border, z_index)

    def create_elements(self):
        third_width = int(self.width / 3) - 1
        return {
            "name": Input(
                parent=self.window,
                x=1,
                y=1,
                label="Name",
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_name,
                error_color=colors.RED_ON_DEFAULT,
            ),
            "order": Input(
                parent=self.window,
                x=1,
                y=4,
                width=third_width,
                label="Order",
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_order,
                error_color=colors.RED_ON_DEFAULT,
            ),
            "color": ColorSelect(
                parent=self.window,
                x=third_width + 2,
                y=4,
                width=third_width,
                options=list(colors.ColorScheme),
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                selected_color=colors.BLACK_ON_BLUE,
            ),
            "is_default": Checkbox(self.window, (third_width * 2) + 4, 5, False, "Default", colors.BLACK_ON_BLUE),
            "button": Button(self.window, 1, 7, label="Save", active_color=colors.BLACK_ON_BLUE),
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=11)

    def on_element_keypress(self, elem_key, element, key):
        if key.c == curses.KEY_RESIZE:
            self.state.on_resize()
            self.activate()
        elif elem_key == "button" and key.c in (curses.ascii.SP, curses.ascii.NL):
            name_input = self.elements["name"]
            order_input = self.elements["order"]
            if not name_input.error and not order_input.error:
                if self.category:
                    category = self.category.copy(
                        name=name_input.value,
                        order=int(order_input.value),
                        colors=self.elements["color"].value,
                    )
                    self.db.save_categories(category)
                else:
                    category = self.db.create_category(
                        name=name_input.value,
                        order=int(order_input.value),
                        colors=self.elements["color"].value,
                        is_expanded=True,
                    )
                if self.elements["is_default"].value != category.is_default:
                    self.db.set_default_category(category.id if self.elements["is_default"].value else None)
                self.hide()
            else:
                self.activate()

    def show(self):
        self.elements["name"].value = self.name
        self.elements["order"].value = str(self.order)
        self.elements["is_default"].value = self.is_default
        self.elements["color"].value = self.color_scheme
        if self.category:
            self.set_title("Edit category")
        else:
            self.set_title("Add category")
        super().show()

    def take(self, key):
        if not self.panel.hidden():
            if key.c == curses.ascii.ESC:
                self.hide()
            return True
        if key.meta and key.s == "e" and self.state.selected_category:
            category = self.state.selected_category
            self.category = category
            self.name = category.name
            self.color_scheme = category.colors
            self.is_default = category.is_default
            self.order = category.order
            self.show()
            return True
        if key.meta and key.s == "n":
            self.category = None
            self.name = ""
            self.color_scheme = colors.ColorScheme.BLUE
            self.is_default = False
            self.order = self.state.max_category_order + 1
            self.show()
            return True
        return False

    def validate_name(self, value: str):
        if value == "":
            return "Cannot be empty."
        return None

    def validate_order(self, value: str):
        try:
            int(value)
            return None
        except ValueError:
            return "Must be a number."
