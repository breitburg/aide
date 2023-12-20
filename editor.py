import curses


class TextEditor:
    def __init__(self, suggestion: str = " world"):
        self.suggestion = suggestion

        # Setting initial cursor position
        self.cursor_x = 0
        self.cursor_y = 0

        # Keeping the state of each line in the editor
        self.lines = [""]

    def _initialize_colors(self):
        """Initialize color setup"""
        # Initialize color pair
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, 8, -1)  # grey color code 8

    def redraw_text(self):
        """Refreshes the screen with updated text"""
        self.stdscr.clear()
        for i, line in enumerate(self.lines):
            self.stdscr.addstr(i, 0, line)

            if i == self.cursor_y:
                self.stdscr.addstr(i, len(line), self.suggestion, curses.color_pair(1))

        self.stdscr.refresh()
        self.stdscr.move(self.cursor_y, self.cursor_x)

    def process_keystroke(self, key) -> tuple[int, int]:
        """Handle keystrokes for editor navigation and text processing"""

        # Navigation keys
        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            return self._handle_navigation_keys(key)

        # Enter key
        elif key in (curses.KEY_ENTER, 10, 13):
            return self._handle_enter_key()

        # Backspace key
        elif key in (8, 127):
            return self._handle_backspace_key()

        # Delete key
        elif key in (4, curses.KEY_DC):
            return self._handle_delete_key()

        # Tab key
        elif key == 9:
            return self._handle_tab_key()

        return self._handle_regular_characters(key)

    # Various key handlers
    def _handle_navigation_keys(self, key) -> tuple[int, int]:
        """Navigation keys handling"""
        if key == curses.KEY_UP:
            self.cursor_y = max(0, self.cursor_y - 1)
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

        elif key == curses.KEY_DOWN:
            self.cursor_y = min(self.cursor_y + 1, len(self.lines) - 1)
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

        elif key == curses.KEY_LEFT:
            self.cursor_y, self.cursor_x = (
                (self.cursor_y - 1, len(self.lines[self.cursor_y - 1]))
                if self.cursor_x == 0 and self.cursor_y > 0
                else (self.cursor_y, max(0, self.cursor_x - 1))
            )

        elif key == curses.KEY_RIGHT:
            self.cursor_y, self.cursor_x = (
                (self.cursor_y + 1, 0)
                if self.cursor_x >= len(self.lines[self.cursor_y])
                and self.cursor_y < len(self.lines) - 1
                else (
                    self.cursor_y,
                    min(self.cursor_x + 1, len(self.lines[self.cursor_y])),
                )
            )

        return self.cursor_x, self.cursor_y

    def _handle_enter_key(self) -> tuple[int, int]:
        self.lines = (
            self.lines[: self.cursor_y + 1] + [""] + self.lines[self.cursor_y + 1 :]
        )

        self.cursor_y, self.cursor_x = self.cursor_y + 1, 0
        return self.cursor_x, self.cursor_y

    def _handle_backspace_key(self) -> tuple[int, int]:
        if self.cursor_x > 0:
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][: self.cursor_x - 1]
                + self.lines[self.cursor_y][self.cursor_x :]
            )
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            self.cursor_x = len(self.lines[self.cursor_y - 1])
            self.lines[self.cursor_y - 1] += self.lines[self.cursor_y]
            self.lines = self.lines[: self.cursor_y] + self.lines[self.cursor_y + 1 :]
            self.cursor_y -= 1
        return self.cursor_x, self.cursor_y

    def _handle_delete_key(self):
        if self.cursor_x < len(self.lines[self.cursor_y]):
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][: self.cursor_x]
                + self.lines[self.cursor_y][self.cursor_x + 1 :]
            )
        return self.cursor_x, self.cursor_y

    def _handle_tab_key(self):
        self.lines[self.cursor_y] = (
            self.lines[self.cursor_y][: self.cursor_x]
            + self.suggestion
            + self.lines[self.cursor_y][self.cursor_x :]
        )
        self.cursor_x += len(self.suggestion)
        return self.cursor_x, self.cursor_y

    def _handle_regular_characters(self, key):
        self.lines[self.cursor_y] = (
            self.lines[self.cursor_y][: self.cursor_x]
            + chr(key)
            + self.lines[self.cursor_y][self.cursor_x :]
        )
        self.cursor_x += 1
        return self.cursor_x, self.cursor_y

    def run(self, stdscr: curses.window):
        # Clearing the screen
        self.stdscr = stdscr
        self.stdscr.clear()
        self._initialize_colors()

        while True:
            # Limit cursor within the text boundaries
            self.cursor_x = max(0, min(self.cursor_x, len(self.lines[self.cursor_y])))
            self.cursor_y = max(0, min(self.cursor_y, len(self.lines) - 1))

            self.redraw_text()

            # Input handling
            key = self.stdscr.getch()
            self.cursor_x, self.cursor_y = self.process_keystroke(key)


if __name__ == "__main__":
    text_editor = TextEditor()
    curses.wrapper(text_editor.run)
