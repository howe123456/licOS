import curses
import threading
from typing import Optional

from installer.core.config import (
    DESKTOP_ENVIRONMENTS, FILESYSTEMS, KEYBOARD_LAYOUTS,
    ADDITIONAL_PACKAGE_GROUPS,
)
from installer.tui.framework import (
    Screen, Button, Label, TextInput, ListBox,
    ProgressWin, color,
)
from installer.i18n.translations import _, set_language, get_language
from installer.i18n.languages import LANGUAGES, detect_system_language


class LanguageScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "")
        self.lang_codes = list(LANGUAGES.keys())
        lang_items = [f"  {name}" for name in LANGUAGES.values()]

        self.listbox = ListBox(
            items=lang_items,
            width=34,
            height=min(len(lang_items), 14),
            title="",
        )
        self.widgets = [self.listbox]

        detected = detect_system_language()
        if detected in self.lang_codes:
            self.listbox.selected_idx = self.lang_codes.index(detected)

        self.buttons = [
            Button("  ", callback=self.on_next),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def on_enter(self):
        self.app.set_steps([
            "language", "keyboard", "locale", "disk",
            "partition", "desktop", "packages", "user",
            "summary", "install",
        ])
        self.app.current_step_idx = 0
        self.title = _("lang_title")
        self.buttons[0].text = _("btn_continue")

        lang_items = [f"  {name}" for name in LANGUAGES.values()]
        self.listbox.items = lang_items

    def on_next(self):
        idx = self.listbox.selected_idx
        if idx < len(self.lang_codes):
            lang = self.lang_codes[idx]
            set_language(lang)
            self.app.lang = lang
            self.app.data["language"] = lang
        self.app.switch_to("keyboard")

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("lang_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        prompt = _("lang_prompt")
        cy = max_y // 2 - len(self.lang_codes) // 2 - 2
        cx = max_x // 2 - 20
        cx = max(1, cx)
        win.addstr(cy, cx, prompt, color("normal"))
        cy += 2

        lx = max(1, max_x // 2 - 17)
        self.listbox.draw(win, cy, lx)

        btn_y = cy + min(len(self.lang_codes), 14) + 2
        btn_x = max(1, max_x // 2 - 7)
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)

        win.noutrefresh()

    def handle_key(self, key: int) -> Optional[str]:
        if key == ord("\n") or key == ord("\r"):
            if self.buttons:
                self.buttons[0].callback()
            return None
        if key == 27:
            self.app.running = False
            return None
        for w in self.widgets:
            if hasattr(w, "handle_key"):
                w.handle_key(key)
        return None


class WelcomeScreen(Screen):
    def on_enter(self):
        self.title = _("welcome_title")
        self.lines = [
            _("welcome_line1"),
            _("welcome_line2"),
            _("welcome_line3"),
            _("welcome_line4"),
            _("welcome_line5"),
            _("welcome_line6"),
            _("welcome_line7"),
            _("welcome_line8"),
            _("welcome_line9"),
            _("welcome_line10"),
            _("welcome_line11"),
            _("welcome_line12"),
            _("welcome_line13"),
        ]
        self.buttons[0].text = _("btn_start")
        self.buttons[1].text = _("btn_quit")

    def __init__(self, app):
        super().__init__(app, "")
        self.lines = []
        self.buttons = [
            Button("", callback=lambda: app.switch_to("language")),
            Button("", callback=lambda: setattr(app, "running", False)),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("welcome_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - len(self.lines) // 2
        for i, line in enumerate(self.lines):
            if i >= max_y - 5:
                break
            cx = (max_x - len(line)) // 2
            attr = color("highlight") if i == 0 else color("normal")
            if cy + i >= 0 and cy + i < max_y:
                win.addstr(cy + i, max(1, cx), line[:max_x - 2], attr)

        btn_y = cy + len(self.lines) + 2
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()


class KeyboardScreen(Screen):
    def on_enter(self):
        self.title = _("keyboard_title")
        self.listbox.title = _("keyboard_select")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

    def __init__(self, app):
        super().__init__(app, "")

        self.listbox = ListBox(
            items=KEYBOARD_LAYOUTS,
            width=30,
            height=15,
            title="",
        )
        self.widgets = [self.listbox]
        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("welcome")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def on_next(self):
        layout = self.listbox.get_selected()
        self.app.data["keyboard"] = layout
        self.app.switch_to("locale")

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()
        title = _("keyboard_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - 8
        cx = max(1, max_x // 2 - 18)
        self.listbox.draw(win, cy, cx)

        btn_y = cy + 16
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()


class LocaleScreen(Screen):
    def on_enter(self):
        self.title = _("locale_title")
        self.lang_input.label = _("locale_lang")
        self.tz_input.label = _("locale_tz")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

        lang = self.app.lang
        from installer.i18n.languages import get_locale_for_lang
        default_locale = get_locale_for_lang(lang)
        self.lang_input.value = default_locale
        self.lang_input.cursor_pos = len(default_locale)

    def __init__(self, app):
        super().__init__(app, "")

        self.lang_input = TextInput("", width=30, default="en_US.UTF-8")
        self.tz_input = TextInput("", width=30, default="UTC")

        self.focused_input = 0
        self.inputs = [self.lang_input, self.tz_input]
        self.lang_input.focused = True
        self.error_msg = ""

        self.widgets = [self.lang_input, self.tz_input]
        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("keyboard")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def handle_key(self, key: int) -> Optional[str]:
        current = self.inputs[self.focused_input]
        if key == curses.KEY_UP:
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input - 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        if key == curses.KEY_DOWN:
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input + 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        if key == ord("\t"):
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input + 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        current.handle_key(key)

        if key == ord("\n") or key == ord("\r"):
            if self.buttons:
                self.buttons[self.selected_button].callback()
        elif key == 27:
            return "back"
        return None

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()
        title = _("locale_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - 3
        cx = max(1, max_x // 2 - 22)

        prompt = _("locale_prompt")
        win.addstr(cy, cx, prompt, color("normal"))
        cy += 2

        self.lang_input.width = 30
        self.lang_input.draw(win, cy, cx)
        cy += 2

        self.tz_input.width = 30
        self.tz_input.draw(win, cy, cx)
        cy += 2

        if self.error_msg:
            win.addstr(cy + 1, cx, self.error_msg, color("error") | curses.A_BOLD)

        btn_y = cy + 3
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()

    def on_next(self):
        self.error_msg = ""
        if not self.lang_input.value.strip():
            self.error_msg = "Locale cannot be empty!"
            return
        if not self.tz_input.value.strip():
            self.error_msg = "Timezone cannot be empty!"
            return
        tz = self.tz_input.value.strip()
        tz_path = f"/usr/share/zoneinfo/{tz}"
        import os
        if not os.path.exists(tz_path):
            self.error_msg = f"Timezone '{tz}' not found!"
            return

        self.app.data["locale"] = self.lang_input.value.strip()
        self.app.data["timezone"] = tz
        self.app.switch_to("disk")


class DiskScreen(Screen):
    def on_enter(self):
        self.title = _("disk_title")
        self.listbox.title = _("disk_available")
        self.fs_listbox.title = _("disk_fs")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

        self._refresh_disks()
        self.fs_listbox.items = FILESYSTEMS

    def __init__(self, app):
        super().__init__(app, "")

        self.disks = []
        self.listbox = ListBox(
            items=[],
            width=60,
            height=8,
            title="",
        )
        self.widgets = [self.listbox]

        self.fs_listbox = ListBox(
            items=FILESYSTEMS,
            width=18,
            height=5,
            title="",
        )

        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("locale")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def _refresh_disks(self):
        from installer.core.utils import get_disks
        self.disks = get_disks()
        if not self.disks:
            self.disks = [
                {"path": "/dev/sda", "name": "sda",
                 "size": "?", "model": "No disks found"}
            ]
        disk_labels = [
            f"{d['path']:<12} {d['size']:<8} {d['model']}"
            for d in self.disks
        ]
        self.listbox.items = disk_labels

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("disk_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - 7
        cx = max(1, max_x // 2 - 34)

        self.listbox.width = 40
        self.listbox.draw(win, cy, cx)

        fscx = cx + 42
        self.fs_listbox.draw(win, cy, fscx)

        btn_y = cy + 10
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()

    def on_next(self):
        idx = self.listbox.selected_idx
        if idx < len(self.disks):
            disk = self.disks[idx]
            self.app.data["disk"] = disk["path"]
            self.app.data["filesystem"] = self.fs_listbox.get_selected()
            self.app.switch_to("partition")


class PartitionScreen(Screen):
    def on_enter(self):
        self.title = _("partition_title")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

    def __init__(self, app):
        super().__init__(app, "")

        self.mode_selected = 0
        self.modes = [_("partition_auto"), _("partition_manual")]

        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("disk")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def handle_key(self, key: int) -> Optional[str]:
        if key == curses.KEY_UP:
            self.mode_selected = (self.mode_selected - 1) % len(self.modes)
        elif key == curses.KEY_DOWN:
            self.mode_selected = (self.mode_selected + 1) % len(self.modes)
        elif key == ord("\n") or key == ord("\r"):
            if self.buttons:
                self.buttons[self.selected_button].callback()
        elif key == 27:
            return "back"
        return None

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("partition_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - 5
        cx = max(1, max_x // 2 - 22)

        win.addstr(cy, cx, _("partition_mode"),
                   color("title") | curses.A_BOLD)
        cy += 2

        for i, mode in enumerate(self.modes):
            marker = "\u25b6" if i == self.mode_selected else " "
            attr = (color("highlight") | curses.A_BOLD
                    if i == self.mode_selected else color("normal"))
            win.addstr(cy + i * 2, cx + 4, f" {marker} {mode}", attr)

        desc_y = cy + len(self.modes) * 2 + 1
        if self.mode_selected == 0:
            win.addstr(desc_y, cx + 4, _("partition_auto_desc"), color("dim"))
            win.addstr(desc_y + 1, cx + 6, _("partition_efi"), color("dim"))
            win.addstr(desc_y + 2, cx + 6, _("partition_swap"), color("dim"))
            win.addstr(desc_y + 3, cx + 6, _("partition_root"), color("dim"))

        btn_y = desc_y + 6
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()

    def on_next(self):
        self.app.data["partition_mode"] = (
            "auto" if self.mode_selected == 0 else "manual"
        )
        self.app.switch_to("desktop")


class DesktopScreen(Screen):
    def on_enter(self):
        self.title = _("desktop_title")
        self.listbox.title = _("desktop_select")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

        de_list = []
        self.de_keys = list(DESKTOP_ENVIRONMENTS.keys())
        for key in self.de_keys:
            de = DESKTOP_ENVIRONMENTS[key]
            name = _(de["name_key"])
            desc = _(de["desc_key"])
            de_list.append(f"{name:<20} {desc}")
        self.listbox.items = de_list

    def __init__(self, app):
        super().__init__(app, "")

        self.listbox = ListBox(
            items=[],
            width=55,
            height=min(len(DESKTOP_ENVIRONMENTS), 12),
            title="",
        )
        self.widgets = [self.listbox]
        self.de_keys = []

        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("partition")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def on_next(self):
        idx = self.listbox.selected_idx
        if idx < len(self.de_keys):
            key = self.de_keys[idx]
            self.app.data["desktop"] = key
            self.app.data["desktop_info"] = DESKTOP_ENVIRONMENTS[key]
            self.app.switch_to("packages")


class PackagesScreen(Screen):
    def on_enter(self):
        self.title = _("packages_title")
        self.listbox.title = _("packages_select")
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")

        pkg_list = []
        self.pkg_keys = list(ADDITIONAL_PACKAGE_GROUPS.keys())
        for key in self.pkg_keys:
            group = ADDITIONAL_PACKAGE_GROUPS[key]
            name = _(group["name_key"])
            desc = _(group["desc_key"])
            pkg_list.append(f"{name:<25} {desc}")
        self.listbox.items = pkg_list

    def __init__(self, app):
        super().__init__(app, "")

        self.listbox = ListBox(
            items=[],
            width=55,
            height=8,
            title="",
            multi=True,
        )
        self.widgets = [self.listbox]
        self.pkg_keys = []

        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("desktop")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def on_next(self):
        selected = self.listbox.selected_items
        groups = [self.pkg_keys[i] for i in sorted(selected)]
        self.app.data["additional_packages"] = groups
        self.app.switch_to("user")


class UserScreen(Screen):
    def on_enter(self):
        self.title = _("user_title")
        self.labels = [
            _("user_hostname"),
            _("user_username"),
            _("user_root_pass"),
            _("user_user_pass"),
            _("user_confirm_pass"),
        ]
        self.buttons[0].text = _("btn_next")
        self.buttons[1].text = _("btn_back")
        self.error_msg = ""

    def __init__(self, app):
        super().__init__(app, "")

        self.labels = []
        self.hostname_input = TextInput("", width=30, default="licos")
        self.username_input = TextInput("", width=30, default="user")
        self.root_pass_input = TextInput("", width=30, password=True)
        self.user_pass_input = TextInput("", width=30, password=True)
        self.user_pass_confirm = TextInput("", width=30, password=True)

        self.focused_input = 0
        self.inputs = [
            self.hostname_input, self.username_input,
            self.root_pass_input, self.user_pass_input,
            self.user_pass_confirm,
        ]
        self.hostname_input.focused = True
        self.widgets = self.inputs
        self.error_msg = ""

        self.buttons = [
            Button("", callback=self.on_next),
            Button("", callback=lambda: app.switch_to("packages")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def handle_key(self, key: int) -> Optional[str]:
        current = self.inputs[self.focused_input]
        if key == curses.KEY_UP:
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input - 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        if key == curses.KEY_DOWN:
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input + 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        if key == ord("\t"):
            self.inputs[self.focused_input].focused = False
            self.focused_input = (self.focused_input + 1) % len(self.inputs)
            self.inputs[self.focused_input].focused = True
            return None
        current.handle_key(key)

        if key == ord("\n") or key == ord("\r"):
            if self.buttons:
                self.buttons[self.selected_button].callback()
        elif key == 27:
            return "back"
        return None

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("user_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = max_y // 2 - 6
        cx = max(1, max_x // 2 - 22)

        win.addstr(cy, cx, _("user_prompt"), color("title") | curses.A_BOLD)
        cy += 2

        for i, inp in enumerate(self.inputs):
            if i < len(self.labels):
                inp.label = self.labels[i]
            inp.width = 25
            inp.draw(win, cy, cx)
            cy += 2

        if self.error_msg:
            win.addstr(cy, cx, self.error_msg, color("error") | curses.A_BOLD)
            cy += 2

        btn_y = cy + 2
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()

    def on_next(self):
        self.error_msg = ""
        if not self.hostname_input.value.strip():
            self.error_msg = _("user_err_hostname")
            return
        if not self.username_input.value.strip():
            self.error_msg = _("user_err_username")
            return
        if not self.root_pass_input.value:
            self.error_msg = _("user_err_root_pass")
            return
        if not self.user_pass_input.value:
            self.error_msg = _("user_err_user_pass")
            return
        if self.user_pass_input.value != self.user_pass_confirm.value:
            self.error_msg = _("user_err_pass_mismatch")
            return

        self.app.data["hostname"] = self.hostname_input.value.strip()
        self.app.data["username"] = self.username_input.value.strip()
        self.app.data["root_password"] = self.root_pass_input.value
        self.app.data["user_password"] = self.user_pass_input.value
        self.app.switch_to("summary")


class SummaryScreen(Screen):
    def on_enter(self):
        self.title = _("summary_title")
        self.buttons[0].text = _("btn_install")
        self.buttons[1].text = _("btn_back")

    def __init__(self, app):
        super().__init__(app, "")

        self.buttons = [
            Button("", callback=self.on_install),
            Button("", callback=lambda: app.switch_to("user")),
        ]
        self.selected_button = 0
        self.buttons[0].selected = True

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("summary_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        cy = 2
        cx = max(1, (max_x - 60) // 2)
        d = self.app.data

        desktop_name = d.get("desktop_info", {}).get("name_key", "de_none")
        desktop_name = _(desktop_name)
        pkgs = d.get("additional_packages", [])
        pkg_names = ", ".join(pkgs) if pkgs else _("de_none_desc")

        summary = [
            (_("summary_keyboard"), d.get("keyboard", "us")),
            (_("summary_locale"), d.get("locale", "en_US.UTF-8")),
            (_("summary_timezone"), d.get("timezone", "UTC")),
            (_("summary_disk"), d.get("disk", "N/A")),
            (_("summary_fs"), d.get("filesystem", "ext4")),
            (_("summary_partition"), d.get("partition_mode", "auto")),
            (_("summary_desktop"), desktop_name),
            (_("summary_packages"), pkg_names),
            (_("summary_hostname"), d.get("hostname", "licos")),
            (_("summary_username"), d.get("username", "user")),
        ]

        win.addstr(cy, cx, _("summary_review"),
                   color("title") | curses.A_BOLD)
        cy += 2

        for label, value in summary:
            line = f"  {label}:  {value}"
            win.addstr(cy, cx, line[:min(len(line), max_x - cx - 1)],
                       color("normal"))
            cy += 1

        cy += 1
        warning = _("summary_warning")
        if cy + 3 < max_y:
            win.addstr(cy, cx, warning, color("error") | curses.A_BOLD)

        btn_y = cy + 2
        if btn_y + 2 >= max_y:
            btn_y = max_y - 4
        btn_total_w = sum(b.width for b in self.buttons) + 4
        btn_x = (max_x - btn_total_w) // 2
        for b in self.buttons:
            b.draw(win, btn_y, btn_x)
            btn_x += b.width + 4

        win.noutrefresh()

    def on_install(self):
        self.app.switch_to("install")


class InstallScreen(Screen):
    def on_enter(self):
        self.progress.title = _("install_progress")
        self.install_done = False
        self.install_success = False
        self.error_msg = ""
        self.progress.lines = []
        self.progress.progress = 0
        self.progress.status = ""

        self.install_thread = threading.Thread(
            target=self._do_install, daemon=True
        )
        self.install_thread.start()

    def __init__(self, app):
        super().__init__(app, "")

        self.progress = ProgressWin(title="", width=60, height=20)
        self.install_done = False
        self.install_success = False
        self.error_msg = ""
        self.install_thread = None

    def _do_install(self):
        try:
            from installer.core.installer import Installer, InstallerConfig
            d = self.app.data

            config = InstallerConfig()
            config.disk = d.get("disk", "/dev/sda")
            config.filesystem = d.get("filesystem", "ext4")
            config.keyboard_layout = d.get("keyboard", "us")
            config.locale = d.get("locale", "en_US.UTF-8")
            config.timezone = d.get("timezone", "UTC")
            config.hostname = d.get("hostname", "licos")
            config.username = d.get("username", "user")
            config.root_password = d.get("root_password", "")
            config.user_password = d.get("user_password", "")
            config.desktop = d.get("desktop", "")
            de_info = d.get("desktop_info", {})
            config.desktop_packages = de_info.get("packages", [])
            config.display_manager = de_info.get("dm")
            config.additional_groups = d.get("additional_packages", [])

            disk = config.disk
            fs = config.filesystem
            uefi = True

            if uefi:
                config.partitions = {
                    "/boot": {
                        "start": "1MiB", "end": "513MiB",
                        "fs_type": "fat32", "boot": True,
                    },
                    "swap": {
                        "start": "513MiB", "end": "2561MiB",
                        "fs_type": "linux-swap", "boot": False,
                    },
                    "/": {
                        "start": "2561MiB", "end": "100%",
                        "fs_type": fs, "boot": False,
                    },
                }
            else:
                config.partitions = {
                    "/boot": {
                        "start": "1MiB", "end": "513MiB",
                        "fs_type": "ext4", "boot": False,
                    },
                    "swap": {
                        "start": "513MiB", "end": "2561MiB",
                        "fs_type": "linux-swap", "boot": False,
                    },
                    "/": {
                        "start": "2561MiB", "end": "100%",
                        "fs_type": fs, "boot": False,
                    },
                }

            installer = Installer(config, log_callback=self._log)
            installer.install()
            installer.cleanup()

            self.app.data["installer"] = installer
            self.install_success = True
            self._log("")
            self._log(_("install_complete"))
            self.progress.set_progress(100, _("install_complete"))
        except Exception as e:
            self.error_msg = str(e)
            self._log(f"ERROR: {e}")
        finally:
            self.install_done = True

    def _log(self, msg):
        self.progress.add_line(msg)

    def draw(self, win):
        max_y, max_x = win.getmaxyx()
        win.erase()

        title = _("install_title")
        win.addstr(0, (max_x - len(title)) // 2,
                   title, color("title") | curses.A_BOLD)
        win.hline(1, 0, curses.ACS_HLINE, max_x, color("border"))

        if self.install_done:
            if self.install_success:
                done = _("install_complete")
                reboot = _("install_reboot")
                any_key = _("install_any_key")
                win.addstr(max_y // 2 - 2, (max_x - len(done)) // 2,
                           done, color("success") | curses.A_BOLD)
                win.addstr(max_y // 2, (max_x - len(reboot)) // 2,
                           reboot, color("highlight"))
                win.addstr(max_y // 2 + 2, (max_x - len(any_key)) // 2,
                           any_key, color("dim"))
            else:
                failed = _("install_failed")
                win.addstr(max_y // 2 - 2, (max_x - len(failed)) // 2,
                           failed, color("error") | curses.A_BOLD)
                if self.error_msg:
                    lines = self.error_msg.split("\n")
                    for i, line in enumerate(lines[:5]):
                        win.addstr(max_y // 2 + i,
                                   max(1, (max_x - len(line[:60])) // 2),
                                   line[:60], color("error"))
                esc_exit = _("install_any_key")
                win.addstr(max_y // 2 + 7, (max_x - len(esc_exit)) // 2,
                           esc_exit, color("dim"))
        else:
            self.progress.width = min(70, max_x - 8)
            self.progress.height = min(22, max_y - 6)
            pw_x = (max_x - self.progress.width) // 2
            pw_y = (max_y - self.progress.height) // 2
            self.progress.draw(win, pw_y, pw_x)

            wait_text = _("install_wait")
            win.addstr(pw_y + self.progress.height + 1, pw_x,
                       wait_text, color("dim"))

        win.noutrefresh()

    def handle_key(self, key: int) -> Optional[str]:
        if self.install_done:
            if key != -1:
                self.app.running = False
        return None
