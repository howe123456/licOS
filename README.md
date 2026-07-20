# ╲ ╳ ╱ licOS

> Arch Linux-based distribution with a modern TUI installer, animated Plymouth boot splash, and XFCE desktop environment — v4.0 LTS

licOS is an Arch Linux-based distribution focused on simplicity and modern desktop computing. It features a curses-based terminal UI installer with support for 12 languages, LUKS encryption, flexible partitioning, a lightning bolt logo that animates on boot and in the installer, and a showcase of the XFCE dark desktop theme (licOS-dark) via an interactive TUI launcher. This project has its limitations.

## Features

### v4.0 LTS — First Long-Term Support Release

- **lidlm (macOS Desktop)** — licOS Integrated Desktop like macOS: top menu bar + bottom dock with autohide
- **lidlh (Hybrid Desktop)** — licOS Integrated Desktop Hybrid: single bottom panel blending traditional app menu with modern dock elements
- **licfetch** — Lightning bolt ASCII art system info tool (Python, like fastfetch/neofetch but with the "A" replaced by a large ╲╳╱ bolt)
- **Large Lightning Art** — All lightning bolt animations enlarged to 8+ line ASCII art using box-drawing characters: Plymouth boot splash, welcome screen, licfetch
- **Boot Splash** — SYSLINUX and systemd-boot now display "archlinux & licOS" branding
- **Installation Speedup** — `ParallelDownloads=20` in live environment, trimmed mirrorlist (USTC, Tsinghua, Alibaba + fallback)
- **CJK Font Fix** — wqy-zenhei via pacman, `licos-cjk.service` for guaranteed font availability

### v3.0

- **C Rewrite** — All shell tools rewritten to compiled C binaries (~15K each): licos-launcher, licos-about, licos-fetch, licos-welcome, licos-setup
- **licos-setup Service** — Dedicated systemd service for first-boot config overrides (zshrc, XFCE panel)
- **licos-about** — Interactive desktop showcase highlighting licOS features
- **licos-launcher** — Boot-time TUI main menu with desktop showcase entry
- **1/I/W/F/S/R Key Handler** — Boot-time keyboard shortcuts for Launcher/Install/Welcome/Fetch/Shell/Reboot
- **Shell Branding** — Custom MOTD and prompt in .zshrc / .bashrc

### v2.0

- **Plymouth Boot Splash** — Lightning spark animation with progress bar on boot
- **XFCE Desktop** — Pre-configured dark theme (licOS-dark) with lightning wallpaper
- **LightDM Autologin** — Automatic login into XFCE on boot
- **licos-fetch** — System info CLI tool with lightning ASCII art (shell)
- **licos-welcome** — Interactive welcome dashboard (shell)
- **CJK Terminal Fonts** — Built-in WenQuanYi (wqy-zenhei) font for proper CJK display
- **Unicode Console** — `ter-132n` wide Unicode console font with UTF-8 locale

### Installer

- **TUI Installer** — Clean terminal UI with keyboard navigation and sidebar progress
- **12 Languages** — English, 中文, 日本語, 한국어, Français, Deutsch, Español, and more
- **Desktop Environments** — GNOME, KDE Plasma, XFCE, LXQt, Cinnamon, MATE, i3, Sway
- **LUKS Encryption** — LUKS2 with argon2id for disk encryption (toggle with E key)
- **Flexible Partitioning** — Auto (full disk) or manual for BIOS and UEFI
- **Filesystem Choices** — ext4, btrfs, xfs, f2fs
- **Package Groups** — Development tools, multimedia, office, printing, bluetooth, gaming


## Quick Start

### Boot from ISO

1. Download the latest ISO from [Releases](https://github.com/howe123456/licOS/releases/tag/v4.0)
2. Write to USB:
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. Boot from the USB drive
4. Watch the Plymouth lightning animation, then press **1** for the desktop showcase, **I** to install, or **F** for system info

### Build from Source

```bash
# Install dependencies (optional: nginx for local caching proxy)
sudo pacman -S archiso nginx

# Clone and build
git clone https://github.com/licOS/licOS.git
cd licOS

# Quick build (pre-downloads packages, uses cache proxy, incremental)
sudo ./archiso-profile/build.sh

# Manual build
sudo mkarchiso -v archiso-profile/

# Output ISO in out/ (~1.8 GB)
ls out/*.iso
```

> **Build acceleration**:
> - `build.sh` auto-starts a local nginx caching proxy at `localhost:8080`
> - Packages are pre-downloaded to host cache before `mkarchiso` runs
> - The USTC mirror is used as primary (fastest for China)
> - `ParallelDownloads=20` for concurrent package download
> - `work/` directory is preserved between runs for incremental rebuilds
> - Set up nginx proxy: `sudo systemctl enable --now nginx`

### Run in QEMU

```bash
# BIOS
qemu-system-x86_64 -cdrom out/licOS-*.iso -m 4G -enable-kvm

# UEFI
qemu-system-x86_64 -bios /usr/share/edk2/x64/OVMF.4m.fd \
  -cdrom out/licOS-*.iso -m 4G -enable-kvm
```

## Project Structure

```
licOS/
├── installer/                  # Python TUI installer
│   ├── core/                   # Installation engine
│   │   ├── config.py           # Defaults (DEs, packages, etc.)
│   │   ├── installer.py        # Partition, pacstrap, chroot, bootloader
│   │   └── utils.py            # Disk detection, network check, etc.
│   ├── i18n/                   # Internationalization
│   │   ├── languages.py        # 12 language definitions
│   │   └── translations.py     # Translation dictionary (1100+ lines)
│   ├── tui/                    # Terminal UI
│   │   ├── framework.py        # Widget library (curses) + LightningLogo
│   │   └── screens.py          # 10 installer screens
│   └── __main__.py             # Entry point
├── archiso-profile/            # ISO build profile
│   ├── grub/                   # GRUB config (UEFI)
│   ├── syslinux/               # SYSLINUX config (BIOS)
│   ├── airootfs/               # Live environment overlay
│   │   ├── etc/                # System configs
│   │   │   ├── lightdm/        # LightDM autologin + greeter
│   │   │   ├── mkinitcpio.conf.d/  # mkinitcpio with plymouth hook
│   │   │   ├── skel/           # Default user shell configs
│   │   │   └── xdg/            # Desktop panel configs (XFCE, lidlm, lidlh)
│   │   ├── root/               # Root user (live session)
│   │   │   ├── .zshrc / .bashrc    # Welcome banner + key handler
│   │   │   ├── start-licos     # Fallback launcher (C ELF, 15K)
│   │   │   ├── customize_airootfs.sh  # Post-install customization
│   │   │   └── licOS/
│   │   │       ├── licos-installer   # Installer (C ELF, 15K)
│   │   │       └── welcome/         # Welcome TUI app
│   │   ├── usr/
│   │   │   ├── local/bin/       # CLI tools and desktop entry points
│   │   │   │   ├── licos-fetch, licos-welcome, licos-launcher, ...
│   │   │   │   ├── licos-setup, lidlm-setup, lidlh-setup
│   │   │   │   └── choose-mirror, Installation_guide, ...
│   │   │   ├── share/
│   │   │   │   ├── xsessions/   # lidlm.desktop, lidlh.desktop
│   │   │   │   ├── systemd/bootctl/  # splash-arch.bmp (UEFI boot splash)
│   │   │   │   ├── plymouth/    # licOS-spark boot theme
│   │   │   │   ├── themes/      # licOS-dark GTK theme
│   │   │   │   ├── backgrounds/ # Lightning wallpaper
│   │   │   │   └── overrides/   # First-boot config overrides
│   │   │   │       ├── root.zshrc
│   │   │   │       ├── skel.zshrc
│   │   │   │       ├── xfce4-panel.xml
│   │   │   │       └── xfce4-xsettings.xml
│   │   └── .../
│   ├── packages.x86_64          # Package list
│   ├── profiledef.sh            # Build config + file permissions
│   └── pacman.conf              # Pacman config
├── out/                         # Built ISO images
├── README.md
├── README.zh.md
└── LICENSE
```

## Installer Screens

| Step | Screen | Description |
|------|--------|-------------|
| 1 | Language | Choose from 12 languages |
| 2 | Keyboard | Select keyboard layout |
| 3 | Locale | Set locale and timezone |
| 4 | Disk | Select target disk and filesystem |
| 5 | Partition | Auto or manual partitioning (E=encrypt) |
| 6 | Desktop | Choose desktop environment |
| 7 | Packages | Select additional package groups |
| 8 | User | Configure hostname, users, passwords |
| 9 | Summary | Review installation settings |
| 10 | Install | Progress bar and log output |

> *"One day, people will stop asking 'how do I install Arch?' and start asking 'when's the next licOS release?'"*

## License

[MIT](LICENSE)
