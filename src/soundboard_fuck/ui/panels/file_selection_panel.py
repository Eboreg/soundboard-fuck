import curses
import curses.ascii
from pathlib import Path
from typing import TypedDict
from soundboard_fuck.constants import SOUND_EXTENSIONS
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.ui.base.elements.button import Button
from soundboard_fuck.ui.base.elements.checkbox import Checkbox
from soundboard_fuck.ui.base.elements.file_select import FileSelect, SimplePath
from soundboard_fuck.ui.base.elements.input import Input
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.colors import ColorPair, ColorPairs
from soundboard_fuck.ui.panels.form_panel import FormPanel
from soundboard_fuck.ui.panels.status_panel import StatusPanel
from soundboard_fuck.utils import iterate_directory_sounds


class Elements(TypedDict):
    path: Input
    file_select: FileSelect
    show_hidden: Checkbox
    add_file: Button
    add_dir: Button
    add_dir_recursive: Button


class FileSelectionPanel(FormPanel):
    border = True
    is_popup = True
    create_hidden = True
    elements: Elements
    path = Path.cwd()
    title = "Add sounds"

    def __init__(
        self,
        state,
        db,
        border=None,
        z_index=None,
        create_hidden=None,
        is_popup=None,
        inactive_color: ColorPair | None = None,
        show_hidden_files: bool = False,
    ):
        self.inactive_color = inactive_color
        self.show_hidden_files = show_hidden_files
        super().__init__(state, db, border, z_index, create_hidden, is_popup)

    def create_elements(self):
        return {
            "path": Input(
                parent=self.window,
                x=2,
                y=1,
                width=self.width - 18,
                inactive_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_path,
                value=str(self.path.absolute()),
                on_change=self.on_path_change,
            ),
            "show_hidden": Checkbox(
                parent=self.window,
                label="Show hidden",
                y=2,
                x=self.width - 14,
                active_color=ColorPairs.BLACK_ON_BLUE,
                value=self.show_hidden_files,
                on_change=self.on_show_hidden_change,
            ),
            "file_select": FileSelect(
                parent=self.window,
                height=min(15, self.height - 5),
                width=self.width - 15,
                directory=self.path,
                y=4,
                x=2,
                inactive_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                selected_color=ColorPairs.BLACK_ON_BLUE,
                extensions=SOUND_EXTENSIONS,
                show_hidden=self.show_hidden_files,
                on_change=self.on_file_select_change,
            ),
            "add_file": Button(
                parent=self.window,
                label="Add file",
                x=self.width - 11,
                y=4,
                active_color=ColorPairs.BLACK_ON_BLUE,
                disabled_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                is_disabled=True,
            ),
            "add_dir": Button(
                parent=self.window,
                label="Add dir ",
                x=self.width - 11,
                y=7,
                active_color=ColorPairs.BLACK_ON_BLUE,
            ),
            "add_dir_recursive": Button(
                parent=self.window,
                label="Add dir\nrecurs. ",
                x=self.width - 11,
                y=10,
                active_color=ColorPairs.BLACK_ON_BLUE,
                height=4,
            )
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=120, height=20)

    def on_element_keypress(self, elem_key, element, key):
        if elem_key == "file_select" and key.c == curses.ascii.NL:
            self.set_path(self.elements["file_select"].get_value().path)
            return True

        if key.c in (curses.ascii.NL, curses.ascii.SP) and elem_key in ("add_file", "add_dir", "add_dir_recursive"):
            existing_paths = [s.path for s in self.db.list_sounds()]
            convert_to_wav = self.db.meta_adapter.get().convert_to_wav
            path = self.path
            status_panel = StatusPanel(self.state, self.db, "", z_index=4, show_cancel_button=True)
            self.screen.attach_panel(status_panel)

            if elem_key == "add_file":
                paths = [path]
            else:
                paths = iterate_directory_sounds(path, elem_key == "add_dir_recursive")

            for p in paths:
                if Sound.get_final_path(p, convert_to_wav) in existing_paths:
                    continue
                if status_panel.check_cancellation():
                    break
                status_panel.set_text(f"Importing {p.name} ...")
                if not status_panel.is_visible:
                    status_panel.show()
                self.db.insert_sound(p)

            self.screen.detach_panel(status_panel)

        return super().on_element_keypress(elem_key, element, key)

    def on_file_select_change(self, value: SimplePath):
        self.elements["add_file"].is_disabled = not value.is_valid_file
        self.elements["add_file"].draw()
        self.elements["path"].set_value(str(value.path.absolute()), False)
        self.elements["path"].draw()

    def on_path_change(self, value: str):
        path = self.path / value
        if self.elements["file_select"].is_valid_path(path):
            self.path = path
            self.elements["file_select"].set_path(path)
            self.set_active_element("file_select")
            self.elements["file_select"].draw()
        abspath = self.path.absolute()
        if self.elements["path"].get_value() != str(abspath):
            self.elements["path"].set_value(str(abspath), False)
            self.elements["path"].draw()

    def on_show_hidden_change(self, value: bool):
        self.elements["file_select"].set_show_hidden(value)
        self.elements["file_select"].draw()

    def set_path(self, value: Path):
        self.path = value
        self.elements["file_select"].set_path(value)
        self.elements["file_select"].draw()

    def take(self, key):
        if not self.state.is_popup_open:
            if key.meta and key.s == "a":
                self.show()
                return True
        return False

    def validate_path(self, value: str):
        if not (self.path / value).exists():
            return f"Path '{value}' not found."
        return None
