#!/usr/bin/env python3
"""licOS Welcome App v3.0 — TUI Dashboard for licOS Live Desktop"""

import curses
import subprocess
import os
import sys
import time

# ── Color / UI framework (inline, no external deps) ──

COLORS = {
    "normal": 0, "highlight": 1, "title": 2, "selected": 3,
    "error": 4, "success": 5, "info": 6, "border": 7,
    "dim": 8, "lightning": 9, "flash": 10,
}

def init_colors():
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_BLACK)

def color(name):
    return curses.color_pair(COLORS.get(name, 0))

# Lightning animation
LIGHTNING_FRAMES = [
    (["     ", "     ", "     "], "dim"),
    (["  .  ", " ... ", "  .  "], "dim"),
    ([" \\   ", "  \\  ", "   / "], "lightning"),
    ([" \\   ", "  X  ", " /   "], "lightning"),
    ([" === ", " =O= ", " === "], "flash"),
    ([" \\   ", "  X  ", " /   "], "lightning"),
    ([" \\   ", "  X  ", " /   "], "lightning"),
]

class LightningLogo:
    def __init__(self):
        self.frame_idx = 0
        self.timer = 0
        self.done = False

    def update(self):
        if self.done:
            return
        self.timer += 1
        if self.timer >= 3:
            self.timer = 0
            if self.frame_idx < len(LIGHTNING_FRAMES) - 1:
                self.frame_idx += 1
            else:
                self.done = True

    def reset(self):
        self.frame_idx = 0
        self.timer = 0
        self.done = False

    def draw(self, win, y, x):
        frame, cname = LIGHTNING_FRAMES[self.frame_idx]
        attr = color(cname) | curses.A_BOLD
        max_y, max_x = win.getmaxyx()
        for i, line in enumerate(frame):
            cy = y + i
            if cy < max_y and x < max_x:
                try:
                    win.addstr(cy, x, line[:max_x - x], attr)
                except curses.error:
                    pass

# ── Welcome App ──

MENU_ITEMS = [
    ("1", "Install licOS", "Launch the licOS installer"),
    ("2", "System Information", "View CPU, RAM, disk, OS info"),
    ("3", "Network Setup", "Configure Wi-Fi and network"),
    ("4", "Desktop Environment", "Start XFCE desktop"),
    ("5", "System Rescue", "Mount and chroot helper"),
    ("6", "Documentation", "View licOS README"),
    ("7", "Exit to Shell", "Return to command prompt"),
]

def get_sys_info():
    info = {}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["cpu"] = line.split(":", 1)[1].strip()
                    break
    except:
        info["cpu"] = "N/A"
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    info["ram"] = f"{kb // 1024} MB"
                    break
    except:
        info["ram"] = "N/A"
    try:
        info["kernel"] = subprocess.check_output(["uname", "-r"], text=True).strip()
    except:
        info["kernel"] = "N/A"
    try:
        info["hostname"] = subprocess.check_output(["uname", "-n"], text=True).strip()
    except:
        info["hostname"] = "N/A"
    try:
        out = subprocess.check_output(["df", "-h", "/"], text=True).splitlines()
        if len(out) >= 2:
            info["disk"] = out[1].split()[2] + " / " + out[1].split()[1]
    except:
        info["disk"] = "N/A"
    try:
        info["ncpu"] = subprocess.check_output(["nproc"], text=True).strip()
    except:
        info["ncpu"] = "N/A"
    try:
        info["de"] = os.environ.get("XDG_CURRENT_DESKTOP", "N/A")
    except:
        info["de"] = "N/A"
    return info

def run_cmd_detached(cmd):
    """Run a command in a new terminal or via shell."""
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        return str(e)
    return None

def show_splash(stdscr):
    """Animated splash screen, returns after animation completes."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    logo = LightningLogo()
    start = time.time()
    while time.time() - start < 2.0:
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        logo.update()
        lx = max_x // 2 - 2
        ly = max_y // 2 - 4
        logo.draw(stdscr, ly, lx)

        title = "licOS Welcome v3.0"
        tx = max_x // 2 - len(title) // 2
        if tx >= 0:
            stdscr.addstr(ly + 4, tx, title, color("title") | curses.A_BOLD)

        subtitle = "Loading..."
        sx = max_x // 2 - len(subtitle) // 2
        if sx >= 0:
            stdscr.addstr(ly + 6, sx, subtitle, color("dim"))

        stdscr.refresh()
        time.sleep(0.05)

def show_main_menu(stdscr):
    """Main menu loop."""
    curses.curs_set(0)
    stdscr.nodelay(0)
    selected = 0
    logo = LightningLogo()
    logo.done = True  # Static logo

    while True:
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()

        # Draw border
        try:
            stdscr.border(0)
        except curses.error:
            pass

        # Title
        title = "licOS Welcome v3.0"
        tx = max_x // 2 - len(title) // 2
        if tx >= 0:
            stdscr.addstr(1, tx, "=" * len(title), color("border"))
            stdscr.addstr(2, tx, title, color("title") | curses.A_BOLD)
            stdscr.addstr(3, tx, "=" * len(title), color("border"))

        # Lightning logo (static final frame) on left side
        logo.draw(stdscr, 5, 4)

        # Menu items
        menu_start_y = 5
        menu_x = 14
        for i, (key, label, desc) in enumerate(MENU_ITEMS):
            y = menu_start_y + i * 2
            if y + 1 >= max_y - 2:
                break
            if i == selected:
                attr = color("selected") | curses.A_BOLD
                stdscr.addstr(y, menu_x - 1, " ", attr)
                stdscr.addstr(y, menu_x, f"  {key}. {label}", attr)
                stdscr.addstr(y, menu_x, " " * (max_x - menu_x - 2), attr)
            else:
                stdscr.addstr(y, menu_x, f"  {key}. {label}", color("normal"))
            stdscr.addstr(y + 1, menu_x + 3, desc, color("dim"))

        # Footer
        footer = " [1-7] Select  [Up/Down] Navigate  [Q] Quit "
        try:
            stdscr.addstr(max_y - 2, max_x // 2 - len(footer) // 2, footer, color("dim"))
        except curses.error:
            pass

        stdscr.refresh()

        # Input handling
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break
        elif key in (ord("1"),):
            selected = 0
            run_menu_action(0, stdscr)
        elif key in (ord("2"),):
            selected = 1
            run_menu_action(1, stdscr)
        elif key in (ord("3"),):
            selected = 2
            run_menu_action(2, stdscr)
        elif key in (ord("4"),):
            selected = 3
            run_menu_action(3, stdscr)
        elif key in (ord("5"),):
            selected = 4
            run_menu_action(4, stdscr)
        elif key in (ord("6"),):
            selected = 5
            run_menu_action(5, stdscr)
        elif key in (ord("7"),):
            selected = 6
            run_menu_action(6, stdscr)
            break
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (10, 13, ord(" ")):  # Enter / Space
            run_menu_action(selected, stdscr)

def run_menu_action(idx, stdscr):
    max_y, max_x = stdscr.getmaxyx()

    if idx == 0:  # Install licOS
        installer = "/root/licOS/licos-installer"
        if os.path.exists(installer):
            curses.endwin()
            subprocess.call([installer])
            curses.doupdate()
        else:
            show_msg(stdscr, "Installer not found at " + installer)
    elif idx == 1:  # System Info
        info = get_sys_info()
        lines = [
            ("System Information", "title"),
            ("", ""),
            (f"Hostname:  {info.get('hostname', 'N/A')}", "normal"),
            (f"Kernel:    {info.get('kernel', 'N/A')}", "normal"),
            (f"CPU:       {info.get('cpu', 'N/A')[:60]}", "normal"),
            (f"Cores:     {info.get('ncpu', 'N/A')}", "normal"),
            (f"RAM:       {info.get('ram', 'N/A')}", "normal"),
            (f"Disk (/):  {info.get('disk', 'N/A')}", "normal"),
            (f"DE:        {info.get('de', 'N/A')}", "normal"),
            ("", ""),
            ("[Press any key to return]", "dim"),
        ]
        show_text_screen(stdscr, lines)
    elif idx == 2:  # Network
        if subprocess.call(["which", "nmtui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            curses.endwin()
            subprocess.call(["nmtui"])
            curses.doupdate()
        else:
            show_msg(stdscr, "nmtui not available. Try: systemctl start iwd")
    elif idx == 3:  # Desktop
        if "DISPLAY" in os.environ:
            show_msg(stdscr, "Desktop already running (DISPLAY=" + os.environ["DISPLAY"] + ")")
        else:
            curses.endwin()
            subprocess.call(["startxfce4"])
            curses.doupdate()
    elif idx == 4:  # Rescue
        lines = [
            ("System Rescue", "title"),
            ("", ""),
            ("To mount and chroot into an installed system:", "normal"),
            ("", ""),
            ("1. Find your root partition:", "normal"),
            ("   lsblk", "normal"),
            ("", ""),
            ("2. Mount it:", "normal"),
            ("   mount /dev/sdXN /mnt", "normal"),
            ("", ""),
            ("3. Chroot:", "normal"),
            ("   arch-chroot /mnt", "normal"),
            ("", ""),
            ("4. Fix issues, then:", "normal"),
            ("   exit && umount -R /mnt", "normal"),
            ("", ""),
            ("[Press any key to return]", "dim"),
        ]
        show_text_screen(stdscr, lines)
    elif idx == 5:  # Documentation
        readme = "/root/licOS/README.md"
        if os.path.exists(readme):
            curses.endwin()
            subprocess.call(["less", readme])
            curses.doupdate()
        else:
            show_msg(stdscr, "README not found")
    elif idx == 6:  # Exit
        pass

def show_msg(stdscr, msg):
    max_y, max_x = stdscr.getmaxyx()
    stdscr.clear()
    try:
        stdscr.addstr(max_y // 2, max_x // 2 - len(msg) // 2, msg, color("normal"))
        stdscr.addstr(max_y // 2 + 2, max_x // 2 - 15, "[Press any key to continue]", color("dim"))
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()

def show_text_screen(stdscr, lines):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    for i, (text, style) in enumerate(lines):
        if i >= max_y - 1:
            break
        try:
            if style == "title":
                attr = color("title") | curses.A_BOLD
                tx = max_x // 2 - len(text) // 2
                stdscr.addstr(i + 1, max(0, tx), text, attr)
            elif style == "dim":
                tx = max_x // 2 - len(text) // 2
                stdscr.addstr(i + 1, max(0, tx), text, color("dim"))
            else:
                stdscr.addstr(i + 1, 4, text, color("normal"))
        except curses.error:
            pass
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    init_colors()
    show_splash(stdscr)
    show_main_menu(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
