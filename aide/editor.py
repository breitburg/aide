import curses
from aide.ollama import Ollama
from threading import Timer


class TextEditor:
    def __init__(self, model: str, text: str = None, ahead: int = 5):
        self.suggestion = ""
        self.ahead = ahead

        # Keeping the state of each line in the editor
        self.lines = (text or "").split("\n")

        # Setting initial cursor position depending on the text
        self.cursor_x = len(self.lines[-1])
        self.cursor_y = len(self.lines) - 1

        # AI model
        self.ollama = Ollama()
        self.model = model
        self.timer = None

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

    def process_keystroke(self, key) -> None:
        """Handle keystrokes for editor navigation and text processing"""

        # Tab key
        if key == 9:
            self._handle_tab_key()
            self.suggestion = ""
            return

        self.suggestion = ""

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

    def _handle_enter_key(self) -> tuple[int, int]:
        self.lines = (
            self.lines[: self.cursor_y + 1] + [""] + self.lines[self.cursor_y + 1 :]
        )

        self.cursor_y, self.cursor_x = self.cursor_y + 1, 0

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

    def _handle_delete_key(self):
        if self.cursor_x < len(self.lines[self.cursor_y]):
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][: self.cursor_x]
                + self.lines[self.cursor_y][self.cursor_x + 1 :]
            )

    def _handle_tab_key(self):
        suggestions = self.suggestion.split("\n")

        for index, suggestion in enumerate(suggestions):
            if index == 0:  # If it's the first line
                # Insert the suggestion on the current line
                self.lines[self.cursor_y] = (
                    self.lines[self.cursor_y][: self.cursor_x]
                    + suggestion
                    + self.lines[self.cursor_y][self.cursor_x :]
                )
                self.cursor_x += len(suggestion)
                continue

            # Insert the suggestion on a new line
            self.cursor_y += 1
            self.lines.insert(self.cursor_y, suggestion)
            self.cursor_x = len(suggestion)

    def _handle_regular_characters(self, key):
        self.lines[self.cursor_y] = (
            self.lines[self.cursor_y][: self.cursor_x]
            + chr(key)
            + self.lines[self.cursor_y][self.cursor_x :]
        )
        self.cursor_x += 1

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
            self.process_keystroke(key)

            if self.timer:
                self.timer.cancel()

            self.timer = Timer(0.5, self.ask_llm)
            self.timer.start()

    def ask_llm(self) -> None:
        stream = self.ollama.generate("\n".join(self.lines), model=self.model, raw=True)

        self.suggestion = ""
        for token in stream:
            self.suggestion += token.text
            self.redraw_text()

            if len(self.suggestion.split(" ")) > self.ahead:
                break
