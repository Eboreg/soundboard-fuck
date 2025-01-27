from soundboard_fuck.ui.base.size import Size


class PanelPlacement:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, parent: Size, width: int, height: int, x: int = 0, y: int = 0):
        self.width = min(width, parent.width - x)
        self.height = min(height, parent.height - y)
        self.x = x
        self.y = y


class CenteredPanelPlacement(PanelPlacement):
    def __init__(self, parent: Size, width: int, height: int):
        width = min(width, parent.width)
        height = min(height, parent.height)
        x = int((parent.width - width) / 2)
        y = int((parent.height - height) / 2)
        super().__init__(parent=parent, width=width, height=height, x=x, y=y)
