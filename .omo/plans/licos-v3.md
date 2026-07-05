# licos-v3 - Work Plan

## TL;DR (For humans)

**What you'll get:** licOS v3.0 — a complete live desktop Linux distribution, not just an installer. Boots into a custom XFCE desktop with lightning-themed Plymouth boot animation, unique licOS branding throughout, a TUI welcome dashboard, system rescue tools, and a fully debugged installer that now supports LUKS encryption.

**Why this approach:** Python TUI framework and archiso profile already exist; we extend them rather than rewrite. XFCE chosen for lightweight (~200MB) desktop that keeps ISO under 2GB. Custom Plymouth theme reuses the 7-frame lightning animation from the existing TUI logo for brand consistency.

**What it will NOT do:** Replace the existing installer workflow. Add unnecessary bloat (>400MB increase). Break BIOS/UEFI dual-boot capability. Introduce systemd dependencies that conflict with existing setup.

**Effort:** Large (7 bugfixes + 3 major feature areas + ISO rebuild)
**Risk:** Medium — XFCE + Plymouth interaction with archiso can be tricky; solves by iterative testing

**Decisions I made for you:**
| Decision | My default | Why |
|---|---|---|
| Desktop environment | XFCE | Lightest full DE, ~200MB packages |
| Display manager | LightDM + GTK greeter | Standard for XFCE, easy to theme |
| Boot splash | Plymouth (script theme) | XFCE compatible, custom animation |
| Theme engine | GTK3 CSS + custom assets | Native to XFCE, no extra deps |
| Welcome dashboard | Python curses TUI | Reuse framework.py code |
| Unique feature focus | System info tool + welcome app | Low effort, high visibility |
| ISO target size | ≤2GB | +400MB budget from current 1.5GB |

---

> **TL;DR (machine):** Large effort, Medium risk. Deliverables: (1) bugfixes to 7 known bugs, (2) Plymouth lightning boot splash, (3) custom XFCE desktop with GTK theme + wallpaper + panel + lightdm, (4) unique tools (welcome app, system info), (5) LUKS encryption in installer, (6) ISO rebuild v3.0.0.

## Scope
### Must have
- Fix all 7 bugs from the code audit
- Plymouth boot splash: custom "licOS-spark" theme with lightning animation
- XFCE desktop: autologin, custom theme (dark + yellow lightning), lightning wallpaper
- LightDM: custom greeter config with licOS branding
- Welcome app: TUI dashboard (System Info, Install, Network, Rescue, Tools, Docs)
- System info tool: neofetch-like display with lightning ASCII art
- LUKS2 encryption option in installer (partitioning step)
- GRUB + syslinux + systemd-boot branding refresh
- Version bump to 3.0.0 throughout
- All shell scripts (welcome, prompts) updated with v3 branding

### Must NOT have (guardrails)
- Do NOT change the installer workflow (same screens, same order)
- Do NOT remove existing boot modes (BIOS + UEFI)
- Do NOT add systemd services that conflict with archiso defaults
- Do NOT introduce binary blobs or non-FOSS packages
- Do NOT break i18n (all 12 languages must still work)
- Do NOT add GNOME/KDE — ISO must stay ≤2GB
- Do NOT modify installer core installation logic (only extend)

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- **Test decision:** tests-after (no test framework exists; manual verification via QEMU boot tests + code inspection)
- **Evidence:** `.omo/evidence/` directory for each task's verification output

## Execution strategy
### Parallel execution waves

**Wave 1: Bugfixes** (5 parallel tasks, no deps)
**Wave 2: Infrastructure** (packages, build config, version bump) — after Wave 1
**Wave 3: Plymouth Theme** (standalone) — parallel with Wave 4/5
**Wave 4: XFCE Customization** (theme, wallpaper, panel, lightdm) — parallel with Wave 3/5
**Wave 5: Unique Features** (welcome app, system info, branding) — parallel with Wave 3/4
**Wave 6: Integration & ISO Build** (after all preceding waves)

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
|---|---|---|---|
| 1-7 (bugfixes) | — | Wave 6 | Each other |
| 8 (packages) | — | Wave 6 | 1-7, 9, 10, 11 |
| 9 (Plymouth theme) | — | 12 (mkinitcpio) | 1-8, 10, 11 |
| 10 (XFCE config) | — | 12 (autologin) | 1-9, 11 |
| 11 (Welcome app) | — | 12 (shell scripts) | 1-10 |
| 12 (Integration) | 1-11 | — | — |
| 13 (ISO build) | 12 | — | — |
| 14 (QEMU verify) | 13 | — | — |

## Todos
> Implementation + Test = ONE todo. Never separate.

### Wave 1: Bugfixes (parallel)

- [ ] 1. **Fix `check_internet()` logic inversion**
  What to do / Must NOT do: In `installer/core/utils.py`, `check_internet()` calls `run_cmd(['ping',...], check=False)` which returns a CompletedProcess with returncode=1 on failure. Since we catch `Exception` and `run_cmd` won't raise with `check=False`, the function returns `True` even when ping fails. Fix: check `result.returncode != 0` instead of try/except. Must NOT change other functions in utils.py.
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/core/utils.py:118-124`
  Acceptance criteria: `check_internet()` returns `False` when ping fails, `True` when it succeeds.
  QA scenarios: Run `python3 -c "from installer.core.utils import check_internet; print(check_internet())"` in an offline context (returns False) and online context (returns True). Evidence: `.omo/evidence/task-1-licos-v3.txt`
  Commit: Y | `fix(utils): correct check_internet() logic inversion`

- [ ] 2. **Fix `_get_prev_screen()` navigation order**
  What to do / Must NOT do: In `installer/tui/framework.py:Application._get_prev_screen()`, the method uses `list(self.screens.keys())` (dict insertion order) instead of `self.steps` list to find the previous screen. This causes the "back" button to navigate incorrectly. Fix: navigate using `self.steps` list order instead. Find the current step's index in `self.steps`, return the previous step name if `current_step_idx > 0`. Must NOT break `switch_to()` or other navigation.
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/tui/framework.py:622-629`
  Acceptance criteria: Pressing Esc in any screen navigates to the correct previous screen per `steps` order, not dict order.
  QA scenarios: Run the installer, navigate forward several steps, press Esc to go back, verify it goes to the correct screen. Use a debug print to confirm screen names match expected order. Evidence: `.omo/evidence/task-2-licos-v3.txt`
  Commit: Y | `fix(framework): correct back navigation order using steps list`

- [ ] 3. **Remove duplicate disk helper functions**
  What to do / Must NOT do: In `installer/tui/framework.py`, remove the duplicate `get_disk_prefix()` and `get_base_disk()` functions (lines 46-73). Replace all calls to these functions in framework.py with imports from `installer.core.utils`. The `installer/core/utils.py` version is the canonical one (uses `re.match`). Must NOT change the function signatures or behavior.
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/tui/framework.py:46-73`, `installer/core/utils.py:155-178`
  Acceptance criteria: `get_disk_prefix()` and `get_base_disk()` work identically to before, imported from utils.
  QA scenarios: Run test that calls both functions with `/dev/nvme0n1`, `/dev/sda`, `/dev/mmcblk0`, `/dev/loop0` — verify same output as before. Evidence: `.omo/evidence/task-3-licos-v3.txt`
  Commit: Y | `refactor(framework): deduplicate disk helper functions`

- [ ] 4. **Improve `cleanup()` error handling**
  What to do / Must NOT do: In `installer/core/installer.py:cleanup()`, replace empty `except Exception: pass` blocks with proper logging via `self.log()`. The method should still continue on error (non-fatal), but log what failed. Must NOT change the cleanup behavior (swapoff + umount -R still runs).
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/core/installer.py:320-330`
  Acceptance criteria: If swapoff or umount fail, the error is logged instead of silently ignored.
  QA scenarios: Run cleanup() when nothing is mounted — verify it logs errors but doesn't crash. Evidence: `.omo/evidence/task-4-licos-v3.txt`
  Commit: Y | `fix(installer): log cleanup errors instead of swallowing them`

- [ ] 5. **Add LUKS encryption support to Installer**
  What to do / Must NOT do: `InstallerConfig.encrypt` and `encrypt_password` exist but are never used. Implement encryption flow in `installer/core/installer.py`:
  - In `prepare_disk()`: after creating partitions, if `encrypt=True`, set up LUKS2 on the root partition
  - In `format_partitions()`: if encrypted, open LUKS container and format the mapped device
  - In `mount_partitions()`: mount the mapped device
  - Add encryption password prompt to `UserScreen` in `screens.py` (checkbox + password field)
  - Must NOT break non-encrypted installs; encryption is optional
  - Use `cryptsetup luksFormat --type luks2 --pbkdf argon2id` for modern standards
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/core/installer.py:12-33,55-166`, `installer/tui/screens.py:577-701`, `installer/core/config.py:122-173`
  Acceptance criteria: When encryption is enabled, installer creates LUKS2 container, formats, and mounts it. When disabled, installs without encryption as before.
  QA scenarios: Run installer with encryption=on and verify `cryptsetup status` shows active container. Run without encryption — verify no cryptsetup involvement. Evidence: `.omo/evidence/task-5-licos-v3.txt`
  Commit: Y | `feat(installer): add LUKS2 encryption support`

- [ ] 6. **Fix password shell injection in CHROOT_COMMANDS**
  What to do / Must NOT do: In `installer/core/config.py:CHROOT_COMMANDS`, root_password and user_password are format-string interpolated into `printf '%s\\n' '{password}' '{password}' | passwd`. If password contains single quotes, it breaks the shell command. Fix: replace the approach with `printf '%s\n' "$password" "$password" | passwd` using environment variables or a heredoc approach. Better: write a small script to `/tmp/setpass` in chroot and run it. Must NOT leave shell injection vector open.
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/core/config.py:124-154`, `installer/core/installer.py:196-212`
  Acceptance criteria: Passwords containing single quotes, double quotes, backslashes, and spaces all work correctly.
  QA scenarios: Set password to `pass'word` or `p@$$"word` in installer, verify chroot password setting succeeds and login works. Evidence: `.omo/evidence/task-6-licos-v3.txt`
  Commit: Y | `fix(config): fix password shell injection in chroot commands`

- [ ] 7. **Refactor InstallScreen hardcoded partition config**
  What to do / Must NOT do: In `installer/tui/screens.py:InstallScreen._do_install()`, lines 831-859 duplicate the partition config logic from `InstallerConfig`. Fix: move partition defaults to `InstallerConfig` and use them directly. Create a `default_partitions()` method on `InstallerConfig`. The InstallScreen should just set `partition_mode` and let `Installer` decide partition layout. Must NOT change partition sizes or behavior.
  Parallelization: Wave 1 | Blocked by: — | Blocks: Wave 6
  References: `installer/tui/screens.py:805-874`, `installer/core/installer.py:12-33`
  Acceptance criteria: Partitions created by the installer are identical to before (512MiB ESP, 2GiB swap, rest root) with same sizes and FS types.
  QA scenarios: Run installer with default settings, inspect created partitions with `lsblk`, verify same layout as before. Evidence: `.omo/evidence/task-7-licos-v3.txt`
  Commit: Y | `refactor(installer): move partition defaults to InstallerConfig`

### Wave 2: Infrastructure

- [ ] 8. **Add packages and configuration for XFCE + Plymouth + tools**
  What to do / Must NOT do:
  - Edit `archiso-profile/packages.x86_64`: add packages:
    - xfce4, xfce4-goodies, xfce4-terminal (desktop)
    - lightdm, lightdm-gtk-greeter (display manager)
    - plymouth (boot splash)
    - firefox (browser for live session)
    - gtk-engine-murrine (for GTK theme support)
  - Create `archiso-profile/airootfs/etc/lightdm/lightdm.conf` for autologin as root
  - Create `archiso-profile/airootfs/etc/lightdm/lightdm-gtk-greeter.conf` with branding
  - Update `profiledef.sh`: change `APP_VERSION` to "3.0.0" in config.py; add version reference
  - Must NOT remove any existing packages
  - Must NOT change ISO boot mode configuration
  Parallelization: Wave 2 | Blocked by: — | Blocks: Wave 6
  References: `archiso-profile/packages.x86_64`, `archiso-profile/profiledef.sh`, `archiso-profile/airootfs/etc/`
  Acceptance criteria: ISO builds with XFCE, lightdm, plymouth packages included. Packages list contains all needed deps.
  QA scenarios: After ISO build, verify `pacman -Q` inside live ISO includes xfce4, lightdm, plymouth. Evidence: `.omo/evidence/task-8-licos-v3.txt`
  Commit: Y | `feat(build): add XFCE, LightDM, Plymouth packages`

### Wave 3: Plymouth Lightning Theme

- [ ] 9. **Create custom Plymouth "licOS-spark" theme with lightning animation**
  What to do / Must NOT do:
  - Create directory: `archiso-profile/airootfs/usr/share/plymouth/themes/licOS-spark/`
  - Create `licOS-spark.plymouth` theme file:
    ```plymouth
    [Plymouth Theme]
    Name=licOS Spark
    Description=licOS Lightning Bolt Boot Animation
    ModuleName=script
    [script]
    ImageDir=/usr/share/plymouth/themes/licOS-spark
    ScriptFile=/usr/share/plymouth/themes/licOS-spark/licOS-spark.script
    ```
  - Create `licOS-spark.script` — Plymouth script that draws the lightning bolt animation:
    - Use `Window.SetBackgroundTopColor` and `Window.SetBackgroundBottomColor` for dark background
    - Draw 7 frames of lightning bolt using `Image.Text` or custom image sprites
    - Animation sequence: spark → arc → strike → flash → settle → static bolt
    - Each frame displayed for ~0.3s, then hold static bolt
    - Use yellow `#FFD700` and white `#FFFFFF` colors
    - Add a progress bar at bottom that syncs with boot progress
  - Create a simple PNG sprite sheet or individual PNG images for the 7 frames
    (Alternative: use `Image.Text` with larger fonts for ASCII-like characters)
  - Must NOT require external image assets not bundled in the theme directory
  - Must NOT depend on non-standard Plymouth plugins
  Parallelization: Wave 3 | Blocked by: — | Blocks: 12 (mkinitcpio)
  References: Plymouth Script reference: https://www.freedesktop.org/software/plymouth/latest/script.html, existing `installer/tui/framework.py:LIGHTNING_FRAMES` for animation sequence reference
  Acceptance criteria: Plymouth theme shows lightning animation during boot, then holds static bolt with progress bar.
  QA scenarios: Boot ISO in QEMU with `splash` kernel parameter, observe boot animation. Check `/var/log/plymouth/` for errors. Evidence: `.omo/evidence/task-9-licos-v3.txt`
  Commit: Y | `feat(plymouth): add licOS-spark lightning boot splash theme`

- [ ] 10. **Configure mkinitcpio and GRUB for Plymouth**
  What to do / Must NOT do:
  - Edit `archiso-profile/airootfs/etc/mkinitcpio.conf.d/archiso.conf`: Add `plymouth` to HOOKS after `base` and `udev` but before `filesystems`
  - Alternatively create `archiso-profile/airootfs/etc/mkinitcpio.conf` to override
  - Edit `archiso-profile/grub/grub.cfg`: Add `splash` and `quiet` to kernel command line
  - Add `plymouth.enable=1` to kernel cmdline
  - Set GRUB_GFXPAYLOAD_LINUX to "keep" or "1024x768" for Plymouth compatibility
  - Must NOT remove existing kernel parameters (archisosearchuuid, etc.)
  - Must NOT disable serial console (keep existing serial support)
  Parallelization: Wave 3 | Blocked by: 9 | Blocks: 12
  References: `archiso-profile/airootfs/etc/mkinitcpio.conf.d/archiso.conf`, `archiso-profile/grub/grub.cfg`
  Acceptance criteria: mkinitcpio includes Plymouth in initramfs; GRUB passes splash params to kernel.
  QA scenarios: Boot ISO, check `journalctl -b | grep plymouth` shows Plymouth started successfully. Check initramfs contains Plymouth theme files. Evidence: `.omo/evidence/task-10-licos-v3.txt`
  Commit: Y | `feat(boot): enable Plymouth in mkinitcpio and GRUB`

### Wave 4: XFCE Customization

- [ ] 11. **Create licOS XFCE desktop theme and wallpaper**
  What to do / Must NOT do:
  - Create wallpaper: Generate a 1920x1080 PNG image featuring the lightning bolt on dark gradient background. Use the ASCII lightning bolt design (`╲╳╱`) as inspiration — convert to a stylized vector-like bolt. Can use ImageMagick or Python PIL to generate.
  - Place at: `archiso-profile/airootfs/usr/share/backgrounds/licOS/lightning-wallpaper.png`
  - Create symlink or copy to: `archiso-profile/airootfs/usr/share/xfce4/backdrops/`
  - Create custom GTK3 theme directory: `archiso-profile/airootfs/usr/share/themes/licOS-dark/gtk-3.0/gtk.css`
    - Dark background (#1a1a2e), yellow accent (#FFD700) for selections/buttons
    - Match color palette: dark navy background, warm yellow for highlights, white text
    - Include gtk-main.css, settings.ini, index.theme files
  - Create `archiso-profile/airootfs/usr/share/themes/licOS-dark/index.theme` with metadata
  - Create `archiso-profile/airootfs/usr/share/themes/licOS-dark/gtk-3.0/settings.ini`
  - Must NOT include full GTK theme engine — just CSS overrides on Adwaita/ARC base
  - Must NOT exceed 2MB for all theme files combined
  Parallelization: Wave 4 | Blocked by: — | Blocks: 12 (desktop config)
  References: GTK3 CSS theming docs, existing XFCE defaults
  Acceptance criteria: GTK theme applies correctly in XFCE — windows have dark background, buttons have yellow highlight, selections are yellow.
  QA scenarios: Boot ISO, open Settings → Appearance, verify "licOS-dark" theme is selectable and applies correctly. Take screenshot for evidence. Evidence: `.omo/evidence/task-11-licos-v3.txt`
  Commit: Y | `feat(xfce): add licOS-dark GTK theme and lightning wallpaper`

- [ ] 12. **Configure XFCE panel, LightDM greeter, and default apps**
  What to do / Must NOT do:
  - Create `archiso-profile/airootfs/etc/xdg/xfce4/panel/default.xml`:
    - Panel at bottom with: Applications menu, window buttons, workspace switcher, notification area, clock
    - Applications menu with lightning icon (use a text label if no icon)
    - Clock with date in "yyyy-MM-dd HH:mm" format
  - Create `archiso-profile/airootfs/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml`:
    - Theme: licOS-dark
    - Title font: Sans 10
  - Create `archiso-profile/airootfs/etc/lightdm/lightdm.conf`:
    ```ini
    [Seat:*]
    autologin-user=root
    autologin-user-timeout=0
    greeter-session=lightdm-gtk-greeter
    ```
  - Create `archiso-profile/airootfs/etc/lightdm/lightdm-gtk-greeter.conf`:
    ```ini
    [greeter]
    theme-name=licOS-dark
    background=/usr/share/backgrounds/licOS/lightning-wallpaper.png
    font-name=Sans 10
    xft-antialias=true
    ```
  - Create `archiso-profile/airootfs/etc/skel/.config/xfce4/` directory structure
  - Set default applications in `archiso-profile/airootfs/etc/skel/.config/`:
    - Browser: firefox
    - Terminal: xfce4-terminal
    - File manager: thunar
  - Must NOT conflict with existing root auto-login on tty1
  - Must NOT break the existing TUI installer flow
  Parallelization: Wave 4 | Blocked by: 11 (theme) | Blocks: 12
  References: XFCE panel config format, lightdm.conf man page, existing `/etc/systemd/system/getty@tty1.service.d/autologin.conf`
  Acceptance criteria: Boot ISO → LightDM starts → auto-logins root → XFCE desktop appears with custom panel, dark theme, lightning wallpaper.
  QA scenarios: Boot ISO in QEMU (graphical), observe LightDM greeter with lightning wallpaper, auto-login to XFCE, verify panel layout and theme. Evidence: `.omo/evidence/task-12-licos-v3.txt`
  Commit: Y | `feat(xfce): configure panel, LightDM autologin, and default apps`

### Wave 5: Unique Features

- [ ] 13. **Create licOS Welcome App (TUI dashboard)**
  What to do / Must NOT do:
  - Create new app at `archiso-profile/airootfs/root/licOS/welcome/welcome.py`
  - Reuse `installer/tui/framework.py` components (Screen, Button, Label, ListBox, LightningLogo)
  - Main menu with options:
    1. **Install licOS** — launches the installer (`/root/licOS/licos-installer`)
    2. **System Information** — shows CPU, RAM, disks, network, OS info using `installer/core/utils.py` functions
    3. **Network Setup** — launches `nmtui`
    4. **Desktop Environment** — starts XFCE (if not already running)
    5. **System Rescue** — chroot helper script
    6. **Documentation** — opens README in `less`
    7. **Exit to Shell** — quits to bash/zsh prompt
  - Create launcher script at `/usr/local/bin/licos-welcome`
  - Add option to `.zshrc`/`.bashrc`: after welcome banner, prompt to launch welcome app or installer
  - Create `.desktop` file: `archiso-profile/airootfs/usr/share/applications/licos-welcome.desktop` pointing to `licos-welcome`
  - Must NOT block the installer — launching installer from welcome app is fine
  - Must NOT require root where not needed
  - Must NOT modify existing installer screens or flow
  Parallelization: Wave 5 | Blocked by: — | Blocks: 12 (shell scripts)
  References: `installer/tui/framework.py`, `installer/core/utils.py` (for system info), existing `.zshrc`/`.bashrc`
  Acceptance criteria: Welcome app launches from shell, displays menu with 7 options, each option works correctly.
  QA scenarios: Run `python3 /root/licOS/welcome/welcome.py`, verify each menu option launches the correct tool. Test "Install licOS" launches installer. Test "System Info" displays hardware details. Test "Exit to Shell" returns to prompt. Evidence: `.omo/evidence/task-13-licos-v3.txt`
  Commit: Y | `feat(welcome): create licOS Welcome TUI dashboard`

- [ ] 14. **Create licOS system info tool**
  What to do / Must NOT do:
  - Create script at `archiso-profile/airootfs/usr/local/bin/licos-fetch`
  - Display:
    ```
    ╔══════════════════════════════════════╗
    ║          ╲    licOS v3.0             ║
    ║           ╳   ──────────             ║
    ║          ╱   OS: Arch Linux          ║
    ║               Kernel: 6.x.x          ║
    ║    ═══╬═══    DE: XFCE               ║
    ║    ═══    Shell: zsh                 ║
    ║               CPU: ...               ║
    ║               RAM: ...               ║
    ║               Disk: ...              ║
    ╚══════════════════════════════════════╝
    ```
  - Use ANSI color codes (yellow for lightning, white for info, cyan for labels)
  - Get system info from: /proc/cpuinfo, /proc/meminfo, `uname -r`, `lsb_release` or /etc/os-release, `df -h /`
  - Add alias in `.zshrc`/`.bashrc`: `alias fetch='licos-fetch'`
  - Must NOT display over 30 lines total
  - Must NOT depend on python — pure shell script for minimal dependency
  Parallelization: Wave 5 | Blocked by: — | Blocks: 12 (shell scripts)
  References: Existing `.zshrc`/`.bashrc` for ANSI patterns, `/proc/cpuinfo`, `/proc/meminfo`
  Acceptance criteria: `licos-fetch` displays system info with lightning ASCII art in under 1 second.
  QA scenarios: Run `licos-fetch` in terminal, verify lightning art displays with correct colors, system info is accurate. Evidence: `.omo/evidence/task-14-licos-v3.txt`
  Commit: Y | `feat(tools): add licos-fetch system info tool`

- [ ] 15. **Update shell startup for v3.0 branding**
  What to do / Must NOT do:
  - Update `.zshrc` and `.bashrc` in `archiso-profile/airootfs/root/`:
    - Change version string to "licOS v3.0"
    - Update lightning animation to match Plymouth animation style
    - After welcome banner: display prompt: "Press [I] to Install | [W] Welcome App | [S] Shell | [R] Reboot"
    - Add key handler for I/W/S/R at boot
    - Add `alias fetch='licos-fetch'`
    - Add `alias welcome='licos-welcome'`
  - Create `.zshrc` and `.bashrc` for `/etc/skel/` (new user default)
  - Must NOT break existing autologin and welcome screen
  - Must NOT remove existing `licos` alias
  Parallelization: Wave 5 | Blocked by: 14 (licos-fetch alias) | Blocks: 12
  References: `archiso-profile/airootfs/root/.zshrc`, `archiso-profile/airootfs/root/.bashrc`
  Acceptance criteria: Boot ISO, see welcome banner with v3.0, prompt with I/W/S/R options, aliases work.
  QA scenarios: Boot ISO, verify welcome banner shows "licOS v3.0", press keys to test each option. Run `fetch` and `welcome` aliases. Evidence: `.omo/evidence/task-15-licos-v3.txt`
  Commit: Y | `feat(shell): update startup scripts for v3.0 branding and shortcuts`

### Wave 6: Integration & Build

- [ ] 16. **Version bump and final integration**
  What to do / Must NOT do:
  - Update `installer/core/config.py`: `APP_VERSION = "3.0.0"`, `APP_TITLE = f"licOS Installer v{APP_VERSION}"`
  - Update README.md and README.zh.md for v3.0 changes:
    - Plymouth boot splash
    - XFCE live desktop
    - Welcome dashboard
    - LUKS encryption support
    - System rescue
  - Update any version strings in boot configs or scripts
  - Clean old build artifacts: `rm -rf work/ out/`
  - Must NOT change any functionality
  Parallelization: Wave 6 | Blocked by: 1-15 (all preceding) | Blocks: 17
  References: `installer/core/config.py:4`, `README.md`, `README.zh.md`
  Acceptance criteria: `APP_VERSION` shows "3.0.0" everywhere, READMEs mention new features.
  QA scenarios: Grep for version strings, verify all show "3.0.0". Check README mentions all 3 major features. Evidence: `.omo/evidence/task-16-licos-v3.txt`
  Commit: Y | `chore: bump version to 3.0.0 and update documentation`

- [ ] 17. **Build licOS v3.0 ISO**
  What to do / Must NOT do:
  - Run: `sudo mkarchiso -v -w work/ -o out/ archiso-profile/`
  - This will produce `out/licOS-YYYY.MM.DD-x86_64.iso` (~1.8-2GB expected)
  - Verify ISO: `file out/*.iso`, `checkisomd5` if available
  - Must NOT run without cleaning work/ first
  - Must handle build failures gracefully and report
  Parallelization: Wave 6 | Blocked by: 16 | Blocks: 18
  References: `archiso-profile/`, build instructions
  Acceptance criteria: ISO builds successfully, is bootable (BIOS + UEFI), volume ID starts with "LICOS_".
  QA scenarios: Check `file` output shows "ISO 9660 CD-ROM" with "bootable" tag. Verify size is ≤2GB. Evidence: `.omo/evidence/task-17-licos-v3.txt`
  Commit: Y (at end) | `build: licOS v3.0.0 ISO`

- [ ] 18. **QEMU verification of v3.0 ISO**
  What to do / Must NOT do:
  - BIOS boot test: `timeout 90 qemu-system-x86_64 -machine q35 -m 4G -display none -serial stdio -cdrom out/licOS-*.iso`
  - UEFI boot test: `timeout 90 qemu-system-x86_64 -machine q35 -m 4G -bios /usr/share/edk2/x64/OVMF.4m.fd -display none -serial stdio -cdrom out/licOS-*.iso`
  - Check: boot menu displays, kernel loads, XFCE starts (if graphical output available)
  - Check: terminal shows welcome banner with v3.0
  - Check: `licos-installer` launches correctly
  - Must NOT use `-display none` for graphical tests if SDL/GTK available
  - If no graphical backend, test via serial console only and confirm boot process
  Parallelization: Wave 6 | Blocked by: 17 | Blocks: —
  References: Previous QEMU test commands
  Acceptance criteria: ISO boots successfully in both BIOS and UEFI modes. Welcome screen shows. Installer launches.
  QA scenarios: Run both BIOS and UEFI QEMU tests, capture serial output. Evidence: `.omo/evidence/task-18-licos-v3.txt`
  Commit: N (verification only)

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit — verify all 18 todos completed, all acceptance criteria met
- [ ] F2. Code quality review — run `python3 -m py_compile` on all .py files, check LSP diagnostics
- [ ] F3. Real manual QA — boot ISO, test installer, test desktop, test welcome app
- [ ] F4. Scope fidelity — verify no must-not items violated, all must-have items present

## Commit strategy
- Each bugfix + feature gets its own commit with conventional commit prefix
- Final commit: `build: licOS v3.0.0 ISO`
- Tag: `v3.0.0`
- All commits to main branch

## Success criteria
1. ✅ All 7 bugs from code audit are fixed
2. ✅ Plymouth shows lightning animation during boot
3. ✅ XFCE desktop starts with autologin, dark theme, lightning wallpaper, custom panel
4. ✅ Welcome app shows TUI dashboard with 7 functional options
5. ✅ `licos-fetch` displays system info with lightning art
6. ✅ LUKS encryption option works in installer
7. ✅ ISO boots in both BIOS and UEFI
8. ✅ ISO size ≤2GB
9. ✅ All 12 languages still work in installer
10. ✅ Shell scripts show v3.0 branding
