# licos-v3 - Draft

## Intent
- Routing: **UNCLEAR** — clarified by user as three pillars:
  1. Boot animation (lightning Plymouth theme)
  2. Customized XFCE desktop (rebranded, themed)
  3. Unique identity (distinctive features, tools, branding)

## User Approval Notes
- Approved general direction
- Prioritized: Plymouth lightning animation, custom XFCE, unique features
- ISO size budget: keep reasonable (≤2GB target)

## Bug Findings (from code audit)
1. **`installer/core/utils.py:check_internet()`** — `run_cmd(..., check=False)` never raises, returns `True` even when ping fails.
2. **`installer/tui/framework.py:Application._get_prev_screen()`** — Uses `screens` dict insertion order, NOT `self.steps` list order. "Back" button navigation is wrong.
3. **`installer/tui/framework.py`** — Duplicate `get_disk_prefix()`/`get_base_disk()` also in `utils.py`, implementations differ.
4. **`installer/core/installer.py:cleanup()`** — `swapoff`/`umount` exceptions silently swallowed.
5. **`installer/core/installer.py:InstallerConfig`** — `encrypt`/`encrypt_password` declared but never used.
6. **`installer/core/config.py:CHROOT_COMMANDS`** — Passwords with single quotes break `printf | passwd` — shell injection surface.
7. **`installer/tui/screens.py:InstallScreen._do_install()`** — Partition config hardcoded inline, duplicates InstallerConfig.

## v3.0 Feature Plan

### 1. Plymouth Lightning Boot Splash
- Custom Plymouth theme "licOS-spark" with lightning bolt animation
- Lightning bolt ASCII-art converted to Plymouth script
- Yellow/white bolt on dark background, 7-frame animation matching existing logo
- GRUB resolution matching Plymouth (1024x768)
- Integrate with mkinitcpio

### 2. Custom XFCE Desktop (licOS Edition)
- **Theme**: Custom GTK theme with lightning motif (dark theme, yellow accents)
- **Wallpaper**: Lightning bolt on dark background (PNG from ASCII art)
- **Panel config**: licOS-branded panel with custom launchers
- **Default apps**: 
  - Terminal: xfce4-terminal with licOS colorscheme
  - File manager: thunar
  - Web browser: firefox with licOS startpage (or just pre-configured)
- **Session branding**: licOS login screen, cursor theme, icon set
- **Pre-installed**: licOS Welcome App, system tools

### 3. Unique Identity Features
- **licOS Welcome App** (TUI + GTK): Dashboard with system info, install option, tools menu
- **licOS System Info Tool**: Custom `neofetch`-style system info with lightning ASCII art
- **Package sets**: Pre-configured development, multimedia, gaming profiles
- **Custom GRUB theme**: Match lightning branding
- **licOS Terminal Welcome**: Enhanced shell prompt with branding
- **Unique driver/display helpers**: Tools for NVIDIA/AMD GPU setup

### 4. Required Packages (add to packages.x86_64)
- xfce4, xfce4-goodies (desktop)
- lightdm + lightdm-gtk-greeter (display manager)
- plymouth (boot splash)
- firefox (browser for live session)
- Custom Plymouth theme files
- Custom GTK/icon themes

### 5. Bug Fixes (all 7 from audit)

## Developer Decisions
| Decision | Choice | Rationale |
|---|---|---|
| Plymouth theme type | script (not fade/throbber) | Custom animation frames needed |
| XFCE greeter | lightdm-gtk-greeter | Standard; can theme easily |
| ISO build | Keep archiso, add packages | No build system change |
| Version | 3.0.0 | Major feature release |
| Lightning animation frames | 7 frames (same as TUI logo) | Brand consistency |
| Desktop autologin | lightdm autologin for live session | Seamless boot experience |

## Component Topology
1. **Bugfixes** (7 fixes across 5 files) — independent, parallel
2. **Plymouth Theme** — New theme directory, mkinitcpio hook, GRUB config
3. **XFCE Config** — Panel, theme, wallpaper, default apps, lightdm config
4. **Welcome App** — New TUI/GTK app in installer/welcome/
5. **Unique Tools** — System info tool, custom-branded scripts
6. **Visual Branding** — Plymouth + GRUB theme + desktop theme unified
7. **Build & Release** — packages.x86_64, ISO rebuild, version bump

## Status
- Exploration: COMPLETE
- Gate: APPROVED (user confirmed direction: boot animation + XFCE + unique features)
- Next: write `.omo/plans/licos-v3.md` with full todos
