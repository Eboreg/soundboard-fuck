import curses.ascii


class KeyPress:
    escape: bool = False
    meta: bool = False
    ctrl: bool = False
    s: str | None = None

    def __init__(self, wch: int | str, meta: bool = False):
        self.wch = wch
        self.c = wch if isinstance(wch, int) else ord(wch)
        self.escape = self.c == -1

        if not self.escape:
            self.s = wch if isinstance(wch, str) else chr(wch)
            self.meta = meta
            self.ctrl = curses.ascii.iscntrl(self.c) and self.s not in ("\t", "\r", "\n")

            if self.ctrl:
                self.s = chr(self.c | 0x60)
