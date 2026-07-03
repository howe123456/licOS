# ╲ ╳ ╱ licOS

> Arch Linux-based distribution with a modern TUI installer and animated lightning bolt branding.

licOS is an Arch Linux-based distribution focused on simplicity and modern desktop computing. It features a curses-based terminal UI installer with support for 12 languages, multiple desktop environments, automated partitioning, and a lightning bolt logo that animates on boot and in the installer's top-right corner.

## Features

- **TUI Installer** — Clean terminal UI with keyboard navigation and sidebar progress
- **12 Languages** — English, 中文, 日本語, 한국어, Français, Deutsch, Español, and more
- **Desktop Environments** — GNOME, KDE Plasma, XFCE, LXQt, Cinnamon, MATE, i3, Sway
- **Flexible Partitioning** — Auto (full disk) or manual for BIOS and UEFI
- **Filesystem Choices** — ext4, btrfs, xfs, f2fs
- **Package Groups** — Development tools, multimedia, office, printing, bluetooth, gaming
- **Animated Logo** — Lightning bolt strikes on boot and in installer corner, then settles to static
- **Live ISO** — Bootable BIOS/UEFI image built with archiso

> **ISO  [Releases](https://github.com/howe123456/licOS/releases/tag/v2026.07.03) download， 1.5 GB。**

## Quick Start

### Boot from ISO

1. Download the latest ISO from [Releases](https://github.com/howe123456/licOS/releases/tag/v2026.07.03)
2. Write to USB:
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. Boot from the USB drive
4. Watch the lightning bolt animation, then type `licos` to start the installer

### Build from Source

```bash
# Install dependencies
sudo pacman -S archiso

# Clone and build
git clone https://github.com/licOS/licOS.git
cd licOS
sudo mkarchiso -v archiso-profile/

# Output ISO in out/
ls out/*.iso
```

### Run in QEMU

```bash
qemu-system-x86_64 -cdrom out/licOS-*.iso -m 4G -enable-kvm
```

## Project Structure

```
licOS/
├── installer/              # Python TUI installer
│   ├── core/               # Installation engine
│   │   ├── config.py       # Defaults (DEs, packages, etc.)
│   │   ├── installer.py    # Partition, pacstrap, chroot, bootloader
│   │   └── utils.py        # Disk detection, network check, etc.
│   ├── i18n/               # Internationalization
│   │   ├── languages.py    # 12 language definitions
│   │   └── translations.py # Translation dictionary (1100+ lines)
│   ├── tui/                # Terminal UI
│   │   ├── framework.py    # Widget library (curses) + LightningLogo
│   │   └── screens.py      # 10 installer screens
│   └── __main__.py         # Entry point
├── archiso-profile/        # ISO build profile (GRUB, Syslinux, systemd-boot)
├── licos-installer         # Shell launcher
├── out/                    # Built ISO images
├── README.md
└── LICENSE
```

## Installer Screens

| Step | Screen | Description |
|------|--------|-------------|
| 1 | Language | Choose from 12 languages |
| 2 | Keyboard | Select keyboard layout |
| 3 | Locale | Set locale and timezone |
| 4 | Disk | Select target disk and filesystem |
| 5 | Partition | Auto or manual partitioning |
| 6 | Desktop | Choose desktop environment |
| 7 | Packages | Select additional package groups |
| 8 | User | Configure hostname, users, passwords |
| 9 | Summary | Review installation settings |
| 10 | Install | Progress bar and log output |

## License

[MIT](LICENSE)
