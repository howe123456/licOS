# ╲ ╳ ╱ licOS

> Arch Linux-based distribution with a modern TUI installer, animated Plymouth boot splash, and XFCE desktop environment — v3.0

licOS is an Arch Linux-based distribution focused on simplicity and modern desktop computing. It features a curses-based terminal UI installer with support for 12 languages, LUKS encryption, flexible partitioning, and a lightning bolt logo that animates on boot and in the installer.

## Features

### v3.0

- **Plymouth Boot Splash** — Lightning spark animation with progress bar on boot
- **XFCE Desktop** — Pre-configured dark theme (licOS-dark) with lightning wallpaper
- **LightDM Autologin** — Automatic login into XFCE on boot
- **licos-fetch** — System info CLI tool with lightning ASCII art
- **licos-welcome** — Interactive welcome dashboard (TUI)
- **I/W/F/S/R Key Handler** — Boot-time keyboard shortcuts for Install/Welcome/Fetch/Shell/Reboot

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

1. Download the latest ISO from [Releases](https://github.com/howe123456/licOS/releases/tag/v2026.07.03)
2. Write to USB:
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. Boot from the USB drive
4. Watch the Plymouth lightning animation, then press **I** to install or **F** for system info

### Build from Source

```bash
# Install dependencies
sudo pacman -S archiso

# Clone and build
git clone https://github.com/licOS/licOS.git
cd licOS
sudo mkarchiso -v archiso-profile/

# Output ISO in out/ (~1.8 GB)
ls out/*.iso
```

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
│   │   │   └── xdg/            # XFCE panel, xfwm4, xsettings
│   │   ├── root/               # Root user (live session)
│   │   │   ├── .zshrc / .bashrc    # Welcome banner + key handler
│   │   │   ├── customize_airootfs.sh  # Post-install customization
│   │   │   └── licOS/
│   │   │       ├── licos-installer   # Shell launcher
│   │   │       └── welcome/         # Welcome TUI app
│   │   ├── usr/
│   │   │   ├── local/bin/       # licos-fetch, licos-welcome
│   │   │   ├── share/
│   │   │   │   ├── plymouth/    # licOS-spark boot theme
│   │   │   │   ├── themes/      # licOS-dark GTK theme
│   │   │   │   └── backgrounds/ # Lightning wallpaper
│   │   │   └── .../
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

## License

[MIT](LICENSE)
