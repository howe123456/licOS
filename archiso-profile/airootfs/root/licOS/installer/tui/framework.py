import curses
import threading
from typing import List, Optional, Callable, Any


COLOR_DEFINITIONS = {
    "normal": 0,
    "highlight": 1,
    "title": 2,
    "selected": 3,
    "error": 4,
    "success": 5,
    "info": 6,
    "border": 7,
    "progress": 8,
    "dim": 9,
    "sidebar": 10,
    "sidebar_active": 11,
    "step_done": 12,
}


def init_colors():
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLUE)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(12, curses.COLOR_GREEN, curses.COLOR_BLACK)


def color(pair_name: str) -> int:
    return curses.color_pair(COLOR_DEFINITIONS.get(pair_name, 0))


def get_disk_prefix(disk: str) -> str:
    if disk.startswith("/dev/nvme"):
        return f"{disk}p"
    if disk.startswith("/dev/mmcblk"):
        return f"{disk}p"
    if disk.startswith("/dev/loop"):
        return f"{disk}p"
    return disk


def get_base_disk(dev: str) -> str:
    import re
    if dev.startswith("/dev/nvme"):
        m = re.match(r"(/dev/nvme\d+n\d+)", dev)
        if m:
            return m.group(1)
    if dev.startswith("/dev/mmcblk"):
        m = re.match(r"(/dev/mmcblk\d+)", dev)
        if m:
            return m.group(1)
    if dev.startswith("/dev/loop"):
        m = re.match(r"(/dev/loop\d+)", dev)
        if m:
            return m.group(1)
    m = re.match(r"(/dev/[a-z]+)", dev)
    if m:
        return m.group(1)
    return dev


class Button:
    def __init__(self, text: str, callback: Callable = None, width: int = 14):
        self.text = text
        self.callback = callback
        self.width = width
        self.selected = False
        self.x = 0
        self.y = 0

    def draw(self, win, y: int, x: int):
        self.x = x
        self.y = y
        text = f"  {self.text}  "
        if self.selected:
            attr = color("selected") | curses.A_BOLD
            win.addstr(y, x, " " * (len(text) + 2), attr)
            win.addstr(y, x + 1, text, attr)
        else:
            win.addstr(y, x, "  " + text + "  ")
            win.chgat(y, x, len(text) + 4, color("dim"))


class Spinner:
    def __init__(self):
        self.chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.idx = 0
        self._timer = 0

    def update(self):
        self._timer += 1
        if self._timer >= 2:
            self.idx = (self.idx + 1) % len(self.chars)
            self._timer = 0

    def __str__(self):
        return self.chars[self.idx]


class Label:
    def __init__(self, text: str = "", y: int = 0, x: int = 0,
                 color_name: str = "normal", bold: bool = False):
        self.text = text
        self.y = y
        self.x = x
        self.color_name = color_name
        self.bold = bold

    def draw(self, win, y: int = None, x: int = None):
        cy = y if y is not None else self.y
        cx = x if x is not None else self.x
        max_x = win.getmaxyx()[1]
        attr = color(self.color_name)
        if self.bold:
            attr |= curses.A_BOLD
        if cy < win.getmaxyx()[0]:
            win.addstr(cy, cx, self.text[:max_x - cx - 1], attr)


class TextInput:
    def __init__(self, label: str = "", width: int = 40,
                 password: bool = False, default: str = ""):
        self.label = label
        self.width = width
        self.password = password
        self.value = default
        self.cursor_pos = len(default)
        self.focused = False
        self._show_cursor = True

    def handle_key(self, key: int) -> bool:
        if not self.focused:
            return False

        if key == curses.KEY_BACKSPACE or key == 127:
            if self.cursor_pos > 0:
                before = self.value[:self.cursor_pos - 1]
                after = self.value[self.cursor_pos:]
                self.value = before + after
                self.cursor_pos -= 1
        elif key == curses.KEY_DC:
            if self.cursor_pos < len(self.value):
                self.value = (self.value[:self.cursor_pos] +
                              self.value[self.cursor_pos + 1:])
        elif key == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.value):
                self.cursor_pos += 1
        elif key == curses.KEY_HOME:
            self.cursor_pos = 0
        elif key == curses.KEY_END:
            self.cursor_pos = len(self.value)
        elif key >= 32:
            try:
                ch = chr(key)
                self.value = (self.value[:self.cursor_pos] + ch +
                              self.value[self.cursor_pos:])
                self.cursor_pos += 1
            except (ValueError, OverflowError):
                pass
        else:
            return False
        return True

    def draw(self, win, y: int = None, x: int = None):
        cy = y if y is not None else 0
        cx = x if x is not None else 0
        max_x = win.getmaxyx()[1]

        if self.label:
            win.addstr(cy, cx, self.label[:max_x - cx - 1])

        label_len = len(self.label)
        display_val = self.value
        if self.password:
            display_val = "\u25cf" * len(self.value)

        field_x = cx + label_len
        field_w = min(self.width, max_x - field_x - 1)
        visible = display_val[:field_w]

        if self.focused:
            win.addstr(cy, field_x, " " * field_w, curses.A_REVERSE)
            win.addstr(cy, field_x, visible, curses.A_REVERSE)
            cursor_draw = min(self.cursor_pos, field_w - 1)
            if cursor_draw >= 0 and self._show_cursor:
                ch = visible[cursor_draw] if cursor_draw < len(visible) else " "
                win.addstr(cy, field_x + cursor_draw, ch,
                           curses.A_REVERSE | curses.A_BLINK)
        else:
            win.addstr(cy, field_x, " " * field_w, color("dim"))
            win.addstr(cy, field_x, visible)


class ListBox:
    def __init__(self, items: List[Any], width: int = 40, height: int = 10,
                 title: str = "", multi: bool = False):
        self.items = items
        self.width = width
        self.height = height
        self.title = title
        self.multi = multi
        self.selected_idx = 0
        self.scroll_offset = 0
        self.selected_items = set()
        if multi and items:
            self.selected_items.add(0)

    def handle_key(self, key: int) -> bool:
        if key == curses.KEY_UP:
            if self.selected_idx > 0:
                self.selected_idx -= 1
                if self.selected_idx < self.scroll_offset:
                    self.scroll_offset = self.selected_idx
        elif key == curses.KEY_DOWN:
            if self.selected_idx < len(self.items) - 1:
                self.selected_idx += 1
                if self.selected_idx >= self.scroll_offset + self.height:
                    self.scroll_offset = self.selected_idx - self.height + 1
        elif key == curses.KEY_NPAGE:
            self.selected_idx = min(len(self.items) - 1,
                                    self.selected_idx + self.height)
            self.scroll_offset = min(len(self.items) - self.height,
                                     self.selected_idx)
        elif key == curses.KEY_PPAGE:
            self.selected_idx = max(0, self.selected_idx - self.height)
            self.scroll_offset = self.selected_idx
        elif key == ord(" ") and self.multi:
            if self.selected_idx in self.selected_items:
                self.selected_items.remove(self.selected_idx)
            else:
                self.selected_items.add(self.selected_idx)
        elif key == ord("\n") or key == ord("\r"):
            return False
        else:
            return False
        return True

    def get_selected(self):
        if self.multi:
            return [self.items[i] for i in sorted(self.selected_items)]
        return self.items[self.selected_idx] if self.items else None

    def draw(self, win, y: int = None, x: int = None):
        cy = y if y is not None else 0
        cx = x if x is not None else 0
        max_y, max_x = win.getmaxyx()
        avail_w = self.width

        if self.title:
            title_text = f" {self.title} "
            win.addstr(cy, cx + (avail_w - len(title_text)) // 2,
                       title_text, color("title") | curses.A_BOLD)
            cy += 1

        for i in range(self.height):
            item_idx = self.scroll_offset + i
            if cy + i >= max_y:
                break

            if item_idx >= len(self.items):
                win.addstr(cy + i, cx, " " * avail_w)
                continue

            item = self.items[item_idx]
            label = str(item)

            if self.multi:
                marker = "\u2713" if item_idx in self.selected_items else " "
                line = f"[{marker}] {label}"
            else:
                line = f"  {label}"

            line = line[:avail_w]

            if item_idx == self.selected_idx:
                win.addstr(cy + i, cx, " " * avail_w, color("highlight"))
                win.addstr(cy + i, cx, line, color("highlight") | curses.A_BOLD)
            else:
                win.addstr(cy + i, cx, line)

        if len(self.items) > self.height:
            scroll_h = max(1, int(self.height * self.height / len(self.items)))
            max_scroll = len(self.items) - self.height
            scroll_pct = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            scroll_pos = int(scroll_pct * (self.height - scroll_h))
            for si in range(self.height):
                if cy + si >= max_y:
                    break
                if si >= scroll_pos and si < scroll_pos + scroll_h:
                    win.addch(cy + si, cx + avail_w,
                              curses.ACS_CKBOARD, color("highlight"))
                else:
                    win.addch(cy + si, cx + avail_w,
                              curses.ACS_VLINE, color("dim"))


class ProgressWin:
    def __init__(self, title: str = "Installing...", width: int = 60, height: int = 20):
        self.title = title
        self.width = width
        self.height = height
        self.lines = []
        self.progress = 0
        self.status = ""
        self.spinner = Spinner()

    def add_line(self, text: str):
        self.lines.append(text)
        max_keep = self.height - 6
        while len(self.lines) > max_keep:
            self.lines.pop(0)

    def set_progress(self, pct: int, status: str = ""):
        self.progress = min(100, max(0, pct))
        self.status = status

    def draw(self, win, y: int, x: int):
        max_y, max_x = win.getmaxyx()
        self.spinner.update()

        box_h = min(self.height, max_y - y - 1)
        box_w = min(self.width, max_x - x - 1)

        for i in range(box_h):
            if y + i < max_y:
                win.addstr(y + i, x, " " * box_w)

        win.attron(color("border"))
        win.hline(y, x + 1, curses.ACS_HLINE, box_w - 2)
        win.hline(y + box_h - 1, x + 1, curses.ACS_HLINE, box_w - 2)
        win.vline(y + 1, x, curses.ACS_VLINE, box_h - 2)
        win.vline(y + 1, x + box_w - 1, curses.ACS_VLINE, box_h - 2)
        win.addch(y, x, curses.ACS_ULCORNER)
        win.addch(y, x + box_w - 1, curses.ACS_URCORNER)
        win.addch(y + box_h - 1, x, curses.ACS_LLCORNER)
        win.addch(y + box_h - 1, x + box_w - 1, curses.ACS_LRCORNER)
        win.attroff(color("border"))

        title_str = f" {self.spinner} {self.title} "
        win.addstr(y, x + (box_w - len(title_str)) // 2,
                   title_str, color("title") | curses.A_BOLD)

        bar_w = box_w - 6
        filled = int(bar_w * self.progress / 100)
        bar_y = y + 2

        win.addstr(bar_y, x + 3, "\u2502", color("dim"))
        for bi in range(bar_w):
            if bi < filled:
                win.addstr(bar_y, x + 4 + bi, "\u2588", color("progress"))
            else:
                win.addstr(bar_y, x + 4 + bi, "\u2591", color("dim"))
        win.addstr(bar_y, x + 4 + bar_w, "\u2502", color("dim"))

        pct_txt = f" {self.progress}% "
        win.addstr(bar_y, x + (box_w - len(pct_txt)) // 2,
                   pct_txt, color("progress") | curses.A_BOLD)

        if self.status:
            st = self.status[:box_w - 4]
            win.addstr(bar_y + 1, x + 2, st, color("info"))

        log_y = bar_y + 3
        max_log = box_h - (log_y - y) - 1
        visible = self.lines[-(max_log):]
        for i, line in enumerate(visible):
            ly = log_y + i
            if ly >= y + box_h - 1:
                break
            win.addstr(ly, x + 2, line[:box_w - 4])


class Screen:
    def __init__(self, app, title: str = ""):
        self.app = app
        self.title = title
        self.widgets = []
        self.buttons = []
        self.selected_button = 0

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_key(self, key: int) -> Optional[str]:
        for w in self.widgets:
            if hasattr(w, "handle_key"):
                if w.handle_key(key):
                    return None

        if key == curses.KEY_UP or key == curses.KEY_DOWN:
            if self.buttons:
                if key == curses.KEY_UP:
                    self.selected_button = ((self.selected_button - 1) %
                                           len(self.buttons))
                else:
                    self.selected_button = ((self.selected_button + 1) %
                                           len(self.buttons))
                for i, b in enumerate(self.buttons):
                    b.selected = (i == self.selected_button)
        elif key == ord("\t"):
            if self.buttons:
                self.selected_button = ((self.selected_button + 1) %
                                       len(self.buttons))
                for i, b in enumerate(self.buttons):
                    b.selected = (i == self.selected_button)
        elif key == ord("\n") or key == ord("\r"):
            if self.buttons and self.buttons[self.selected_button].callback:
                self.buttons[self.selected_button].callback()
        elif key == 27:
            return "back"

        return None

    def draw(self, win):
        win.erase()
        max_y, max_x = win.getmaxyx()

        if self.title:
            title_txt = f" {self.title} "
            win.addstr(0, (max_x - len(title_txt)) // 2,
                       title_txt, color("title") | curses.A_BOLD)
            win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        for w in self.widgets:
            if hasattr(w, "draw"):
                w.draw(win)

        win.noutrefresh()


class Application:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.screens = {}
        self.current_screen: Optional[str] = None
        self.running = True
        self.data = {}
        self.lang = "en"
        self.steps: List[str] = []
        self.current_step_idx = -1

        curses.curs_set(0)
        curses.use_default_colors()
        init_colors()
        self.stdscr.keypad(True)

    def add_screen(self, name: str, screen: Screen):
        self.screens[name] = screen

    def set_steps(self, steps: List[str]):
        self.steps = steps

    def switch_to(self, name: str):
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].on_exit()
        self.current_screen = name
        if name in self.screens:
            self.screens[name].on_enter()
        if name in self.steps:
            self.current_step_idx = self.steps.index(name)
        else:
            self.current_step_idx = -1

    def run(self):
        self.running = True
        while self.running:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()

            if max_y < 20 or max_x < 70:
                self.stdscr.addstr(max_y // 2, max_x // 2 - 15,
                                   "Terminal too small! (min 70x20)",
                                   color("error") | curses.A_BOLD)
                self.stdscr.getch()
                self.running = False
                break

            sidebar_w = 16
            content_x = sidebar_w
            content_w = max_x - sidebar_w

            for i in range(max_y):
                if i < max_y - 1:
                    self.stdscr.addch(i, sidebar_w - 1, curses.ACS_VLINE,
                                      color("border"))

            self.stdscr.addch(0, sidebar_w - 1, curses.ACS_TTEE,
                              color("border"))
            self.stdscr.addch(max_y - 2, sidebar_w - 1, curses.ACS_BTEE,
                              color("border"))

            for i, step_name in enumerate(self.steps):
                step_key = f"step_{step_name}"
                label = self.step_label(step_key)
                if i < max_y - 3:
                    if i == self.current_step_idx:
                        attr = color("sidebar_active") | curses.A_BOLD
                        prefix = "\u25b6"
                    elif i < self.current_step_idx:
                        attr = color("dim")
                        prefix = "\u2713"
                    else:
                        attr = color("sidebar")
                        prefix = " "
                    text = f" {prefix} {label}"
                    if i + 1 < max_y - 2:
                        self.stdscr.addstr(i + 1, 1, text[:sidebar_w - 3],
                                           attr)

            header_txt = self._("app_title")
            self.stdscr.addstr(0, content_x + (content_w - len(header_txt)) // 2,
                               header_txt, color("title") | curses.A_BOLD)
            self.stdscr.hline(1, content_x, curses.ACS_HLINE,
                              content_w - 1, color("border"))

            footer_txt = self._("app_footer")
            self.stdscr.hline(max_y - 2, content_x, curses.ACS_HLINE,
                              content_w - 1, color("border"))
            self.stdscr.addstr(max_y - 1,
                               content_x + (content_w - len(footer_txt)) // 2,
                               footer_txt, color("dim"))

            if self.current_screen and self.current_screen in self.screens:
                screen = self.screens[self.current_screen]
                sub_h = max_y - 4
                sub_w = content_w - 2
                if sub_h > 0 and sub_w > 0:
                    sub_win = self.stdscr.derwin(sub_h, sub_w, 2, content_x + 1)
                    screen.draw(sub_win)

                key = self.stdscr.getch()
                if key == 3:
                    self.running = False
                    break

                result = screen.handle_key(key)
                if result == "exit":
                    self.running = False
                elif result and result in self.screens:
                    self.switch_to(result)
                elif result == "back":
                    prev = self._get_prev_screen()
                    if prev:
                        self.switch_to(prev)

            self.stdscr.noutrefresh()
            curses.doupdate()

    def _get_prev_screen(self) -> Optional[str]:
        if not self.steps or self.current_step_idx <= 0:
            return None
        ordered = list(self.screens.keys())
        idx = ordered.index(self.current_screen) if self.current_screen in ordered else -1
        if idx > 0:
            return ordered[idx - 1]
        return None

    def step_label(self, key: str) -> str:
        from installer.i18n.translations import _
        return _(key)

    def _(self, key: str, *args, **kwargs) -> str:
        from installer.i18n.translations import _
        return _(key, *args, **kwargs)
