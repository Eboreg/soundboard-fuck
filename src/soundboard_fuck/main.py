import curses

from soundboard_fuck.ui.screen import SoundboardScreen


if __name__ == "__main__":
    screen = SoundboardScreen()
    curses.wrapper(screen.attach_window)
