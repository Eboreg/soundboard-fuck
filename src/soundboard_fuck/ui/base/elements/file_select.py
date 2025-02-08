from dataclasses import dataclass
from pathlib import Path
from soundboard_fuck.ui.base.elements.scrollable_select import ScrollableSelect
from soundboard_fuck.utils import format_filesize


@dataclass
class SimplePath:
    name: str
    is_dir: bool
    path: Path
    is_valid_file: bool = False
    size: int = 0

    @classmethod
    def from_path(cls, path: Path, extensions: list[str] | None):
        return cls(
            name=path.name,
            is_dir=path.is_dir(),
            path=path,
            size=path.stat().st_size if path.is_file() else 0,
            is_valid_file=extensions is None or path.suffix.lower().strip(".") in extensions,
        )


class FileSelect(ScrollableSelect[SimplePath]):
    def __init__(
        self,
        parent,
        height,
        directory: Path,
        x=None,
        y=None,
        value=None,
        validator=None,
        on_change=None,
        label=None,
        width=None,
        inactive_color=None,
        active_color=None,
        selected_color=None,
        extensions: list[str] | None = None,
        show_hidden: bool = False,
    ):
        self.directory = directory
        self.show_hidden = show_hidden
        self.extensions = extensions
        options = self.get_directory_contents()
        super().__init__(
            parent=parent,
            height=height,
            x=x,
            y=y,
            value=value,
            validator=validator,
            on_change=on_change,
            label=label,
            options=options,
            width=width,
            inactive_color=inactive_color,
            active_color=active_color,
            selected_color=selected_color,
        )

    def get_directory_contents(self) -> list[SimplePath]:
        contents = []
        if self.directory.parent != self.directory:
            contents.append(SimplePath("..", True, self.directory.parent))
        paths = sorted(
            sorted(self.directory.iterdir(), key=lambda p: p.name.lower()),
            key=lambda p: p.is_dir(),
            reverse=True,
        )
        for path in paths:
            if path.name.startswith(".") and not self.show_hidden:
                continue
            if path.is_dir() or self.extensions is None or path.suffix.lower().strip(".") in self.extensions:
                contents.append(SimplePath.from_path(path, self.extensions))
        return contents

    def is_valid_path(self, path: Path) -> bool:
        if path.is_dir():
            return True
        if not path.is_file():
            return False
        if self.extensions is not None and path.suffix.lower().strip(".") not in self.extensions:
            return False
        if not self.show_hidden and path.name.startswith("."):
            return False
        return True

    def print_option_label(self, option, window, x, y, width):
        if not option.is_dir:
            end = " " + format_filesize(option.size)
        else:
            end = " DIR"
        name_width = width - len(end)
        label = f"{option.name:{name_width}.{name_width}}{end}"
        window.addstr(y, x, label)

    def set_path(self, value: Path):
        directory = value if value.is_dir() else value.parent
        self.directory = directory
        self.options = self.get_directory_contents()
        self.set_value(self.options[0], False)
        if directory != value:
            try:
                self.set_value([o for o in self.options if o.path == value][0], False)
            except IndexError:
                pass
        self.offset = self.options.index(self.get_value())

    def set_show_hidden(self, value: bool):
        if value != self.show_hidden:
            self.show_hidden = value
            self.options = self.get_directory_contents()
            self.offset = 0
