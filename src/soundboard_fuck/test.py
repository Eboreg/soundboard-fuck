import curses
import curses.panel
from time import sleep

from soundboard_fuck.ui.base.panel import Panel
from soundboard_fuck.ui.base.screen import Screen


class TestPanel(Panel):
    text: str = ""

    def __init__(self, text: str, border = False, z_index = 0):
        super().__init__(border, z_index)
        self.text = text

    def contents(self):
        self.set_line(2, 5, self.text)

    def set_text(self, value: str):
        if self.text != value:
            # self.set_line(2, 2, value)
            self.text = value
            self.window.touchline(5, 1, True)


def make_panel_2(screen: Screen, w: int, h: int, x: int, y: int, string: str, z_index: int, show: bool):
    panel = TestPanel(text=string, z_index=z_index, border=True)
    screen.attach_panel(panel, w, h, x, y, show)
    return panel


def test2(stdscr: curses.window):
    screen = Screen(border=True)
    screen.attach_window(stdscr)
    panel1 = make_panel_2(screen, 12, 10, 5, 5, "Panel 1", 0, True)
    panel2 = make_panel_2(screen, 12, 10, 8, 8, "Panel 2", 1, True)

    stdscr.addstr(0, 0, "draw")
    panel1.window.bkgd(".")
    panel2.window.bkgd("o")
    screen.draw()
    sleep(1)

    stdscr.addstr(0, 0, "show panel1           ")
    panel1.show()
    sleep(1)

    stdscr.addstr(0, 0, "move panel1 to top    ")
    panel1.move_to_top()
    sleep(1)

    stdscr.addstr(0, 0, "hide panel1           ")
    panel1.hide()
    sleep(1)

    stdscr.addstr(0, 0, "show panel1           ")
    panel1.show()
    sleep(1)

    stdscr.addstr(0, 0, "change panel1 text    ")
    panel1.set_text("PÄNEL X BÖGEWL BÖGL")
    panel1.redraw()
    sleep(1)

    stdscr.addstr(0, 0, "change panel2 text    ")
    panel2.set_text("PÖNEL Y")
    panel2.redraw()
    sleep(1)

    stdscr.addstr(0, 0, "move panel1 to bottom ")
    panel1.move_to_bottom()
    sleep(1)


def make_panel(h: int, w: int, y: int, x: int, string: str):
    win = curses.newwin(h, w, y, x)
    win.erase()
    win.box()
    win.addstr(2, 2, string)

    panel = curses.panel.new_panel(win)
    return panel


def test(stdscr: curses.window):
    try:
        curses.curs_set(0)
    except Exception:
        pass
    stdscr.box()
    stdscr.addstr(0, 0, "panels everywhere")
    panel1 = make_panel(10, 12, 5, 5, "Panel 1")
    panel2 = make_panel(10, 12, 8, 8, "Panel 2")

    curses.panel.update_panels()
    stdscr.refresh()
    sleep(1)

    panel1.top()
    curses.panel.update_panels()
    curses.doupdate()
    sleep(1)

    panel1.hide()
    curses.panel.update_panels()
    curses.doupdate()
    sleep(1)

    panel1.show()
    curses.panel.update_panels()
    curses.doupdate()
    sleep(1)

    panel1.window().addstr(2, 2, "PÄNEL X")
    panel1.window().noutrefresh()
    curses.doupdate()
    sleep(1)

    for i in range(20):
        panel2.move(8, 8+i)
        curses.panel.update_panels()
        stdscr.refresh()
        sleep(0.1)

    sleep(1)


if __name__ == "__main__":
    curses.wrapper(test2)
