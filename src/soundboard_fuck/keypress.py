import curses.ascii


class KeyPress:
    escaped: bool = False
    meta: bool = False
    ctrl: bool = False
    s: str | None = None

    def __init__(self, wch: int | str, meta: bool = False):
        self.wch = wch
        self.c = wch if isinstance(wch, int) else ord(wch)

        if self.c != -1:
            self.s = wch if isinstance(wch, str) else chr(wch)
            self.meta = meta
            self.ctrl = curses.ascii.iscntrl(self.c) and self.s not in ("\t", "\r", "\n")

            if self.ctrl:
                self.s = chr(self.c | 0x60)
        else:
            self.escaped = True
            self.c = curses.ascii.ESC

    @classmethod
    def get(cls, window: curses.window) -> "KeyPress":
        window.keypad(True)
        wch = window.get_wch()
        key = cls(wch, meta=False)

        if key.c == curses.ascii.ESC and not key.escaped:
            window.nodelay(True)
            c = window.getch()
            key = cls(c, meta=True)
            window.nodelay(False)

        return key

    @classmethod
    def get_non_blocking(cls, window: curses.window) -> "KeyPress | None":
        window.nodelay(True)
        try:
            return cls.get(window)
        except Exception:
            return None
        finally:
            window.nodelay(False)
