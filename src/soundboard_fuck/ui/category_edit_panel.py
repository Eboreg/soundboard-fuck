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
    category: Category

    @property
    def title(self):
        if self.category.id:
            return "Edit category"
        return "Add category"

    def __init__(self, state, db: AbstractDb, border=None, z_index=None):
        self.db = db
        super().__init__(state, border, z_index)

    def create_elements(self):
        third_width = int(self.width / 3) - 1
        elements = {
            "name": Input(
                parent=self.window,
                x=2,
                y=1,
                label="Name",
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_name,
                error_color=colors.RED_ON_DEFAULT,
                value=self.category.name,
            ),
            "order": Input(
                parent=self.window,
                x=2,
                y=4,
                width=third_width,
                label="Order",
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_order,
                error_color=colors.RED_ON_DEFAULT,
                value=str(self.category.order),
            ),
            "color": ColorSelect(
                parent=self.window,
                x=third_width + 3,
                y=4,
                width=third_width,
                options=list(colors.ColorScheme),
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                selected_color=colors.BLACK_ON_BLUE,
                value=self.category.colors,
            ),
            "is_default": Checkbox(
                parent=self.window,
                x=(third_width * 2) + 5,
                y=5,
                label="Default",
                active_color=colors.BLACK_ON_BLUE,
                value=self.category.is_default,
            ),
            "save": Button(self.window, 2, 7, label="Save", active_color=colors.BLACK_ON_BLUE),
        }
        if self.category.id and self.category.sound_count == 0:
            elements["delete"] = Button(self.window, 10, 7, label="Delete", active_color=colors.BLACK_ON_RED)
        return elements

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=11)

    def on_element_keypress(self, elem_key, element, key):
        if key.c == curses.KEY_RESIZE:
            self.state.on_resize()
            return True
        if elem_key in ("save", "delete") and key.c in (curses.ascii.SP, curses.ascii.NL):
            if elem_key == "delete":
                self.db.category_adapter.delete(id=self.category.id)
                return False
            if elem_key == "save":
                name_input = self.elements["name"]
                order_input = self.elements["order"]
                if not name_input.error and not order_input.error:
                    if self.category.id:
                        self.db.category_adapter.update(
                            self.category,
                            name=name_input.value,
                            order=int(order_input.value),
                            colors=self.elements["color"].value,
                        )
                        category = self.category
                    else:
                        category = self.db.category_adapter.insert(
                            Category(
                                name=name_input.value,
                                order=int(order_input.value),
                                colors=self.elements["color"].value,
                                is_expanded=True,
                            )
                        )
                    if self.elements["is_default"].value != category.is_default:
                        self.db.set_default_category(category.id if self.elements["is_default"].value else None)
                    return False
        return True


    def take(self, key):
        if key.meta and key.s == "e" and self.state.selected_category:
            self.category = self.state.selected_category
            self.show()
            return True
        if key.meta and key.s == "n":
            self.category = Category(
                name="",
                order=self.state.max_category_order + 1,
                colors=colors.ColorScheme.BLUE,
            )
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
