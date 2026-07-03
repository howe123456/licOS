#!/usr/bin/env python3

import sys
import curses


def main(stdscr):
    from installer.tui.framework import Application
    from installer.tui.screens import (
        WelcomeScreen, LanguageScreen, KeyboardScreen,
        LocaleScreen, DiskScreen, PartitionScreen,
        DesktopScreen, PackagesScreen, UserScreen,
        SummaryScreen, InstallScreen,
    )

    app = Application(stdscr)

    app.add_screen("welcome", WelcomeScreen(app))
    app.add_screen("language", LanguageScreen(app))
    app.add_screen("keyboard", KeyboardScreen(app))
    app.add_screen("locale", LocaleScreen(app))
    app.add_screen("disk", DiskScreen(app))
    app.add_screen("partition", PartitionScreen(app))
    app.add_screen("desktop", DesktopScreen(app))
    app.add_screen("packages", PackagesScreen(app))
    app.add_screen("user", UserScreen(app))
    app.add_screen("summary", SummaryScreen(app))
    app.add_screen("install", InstallScreen(app))

    app.switch_to("welcome")
    app.run()


def check_deps():
    try:
        import psutil
    except ImportError:
        print("Error: 'psutil' is required.")
        print("Install with: pip install psutil")
        return False
    return True


if __name__ == "__main__":
    if not check_deps():
        sys.exit(1)

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nInstallation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
