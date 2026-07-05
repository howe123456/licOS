import os

APP_NAME = "licOS"
APP_VERSION = "3.0.0"
APP_TITLE = f"{APP_NAME} Installer v{APP_VERSION}"

DEFAULT_LOCALE = "en_US.UTF-8"
DEFAULT_TIMEZONE = "UTC"

DESKTOP_ENVIRONMENTS = {
    "gnome": {
        "name_key": "de_gnome",
        "desc_key": "de_gnome_desc",
        "packages": ["gnome", "gnome-extra", "gdm"],
        "dm": "gdm",
    },
    "kde": {
        "name_key": "de_kde",
        "desc_key": "de_kde_desc",
        "packages": ["plasma", "kde-applications", "sddm"],
        "dm": "sddm",
    },
    "xfce": {
        "name_key": "de_xfce",
        "desc_key": "de_xfce_desc",
        "packages": ["xfce4", "xfce4-goodies", "lightdm"],
        "dm": "lightdm",
    },
    "lxqt": {
        "name_key": "de_lxqt",
        "desc_key": "de_lxqt_desc",
        "packages": ["lxqt", "lxqt-extra", "sddm"],
        "dm": "sddm",
    },
    "cinnamon": {
        "name_key": "de_cinnamon",
        "desc_key": "de_cinnamon_desc",
        "packages": ["cinnamon", "gnome-terminal", "lightdm"],
        "dm": "lightdm",
    },
    "mate": {
        "name_key": "de_mate",
        "desc_key": "de_mate_desc",
        "packages": ["mate", "mate-extra", "lightdm"],
        "dm": "lightdm",
    },
    "i3": {
        "name_key": "de_i3",
        "desc_key": "de_i3_desc",
        "packages": ["i3", "i3lock", "i3status", "dmenu", "lightdm"],
        "dm": "lightdm",
    },
    "sway": {
        "name_key": "de_sway",
        "desc_key": "de_sway_desc",
        "packages": ["sway", "waybar", "wofi", "lightdm"],
        "dm": "lightdm",
    },
    "none": {
        "name_key": "de_none",
        "desc_key": "de_none_desc",
        "packages": [],
        "dm": None,
    },
}

FILESYSTEMS = ["ext4", "btrfs", "xfs", "f2fs"]

BASE_PACKAGES = [
    "base", "base-devel", "linux", "linux-firmware",
    "sudo", "vim", "nano", "networkmanager",
    "grub", "efibootmgr", "os-prober",
    "bash-completion", "man-db", "man-pages",
    "git", "curl", "wget", "htop",
]

ADDITIONAL_PACKAGE_GROUPS = {
    "development": {
        "name_key": "pkg_development",
        "desc_key": "pkg_development_desc",
        "packages": ["gcc", "make", "python", "python-pip",
                     "nodejs", "npm", "rust", "cargo"],
    },
    "multimedia": {
        "name_key": "pkg_multimedia",
        "desc_key": "pkg_multimedia_desc",
        "packages": ["vlc", "firefox", "gimp", "inkscape", "audacity"],
    },
    "office": {
        "name_key": "pkg_office",
        "desc_key": "pkg_office_desc",
        "packages": ["libreoffice-fresh", "evince", "gthumb"],
    },
    "printing": {
        "name_key": "pkg_printing",
        "desc_key": "pkg_printing_desc",
        "packages": ["cups", "hplip", "system-config-printer"],
    },
    "bluetooth": {
        "name_key": "pkg_bluetooth",
        "desc_key": "pkg_bluetooth_desc",
        "packages": ["bluez", "bluez-utils", "blueman"],
    },
    "gaming": {
        "name_key": "pkg_gaming",
        "desc_key": "pkg_gaming_desc",
        "packages": ["steam", "lutris", "wine", "winetricks"],
    },
}

KEYBOARD_LAYOUTS = [
    "us", "us-dvorak", "us-colemak",
    "gb", "de", "de-latin1", "fr", "fr-latin1",
    "es", "it", "pt", "pt-br",
    "jp", "kr", "cn", "tw",
    "ru", "ua", "by",
    "se", "no", "dk", "fi",
    "pl", "cz", "sk", "hu", "ro",
    "tr", "gr", "il", "ar", "ir",
]

INSTALL_DIR = "/mnt/licos"

CHROOT_COMMANDS = [
    ("Setting timezone",
     "ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime"),
    ("Setting hardware clock",
     "hwclock --systohc"),
    ("Generating locale",
     "echo '{locale} UTF-8' > /etc/locale.gen && locale-gen"),
    ("Setting locale",
     "echo 'LANG={locale}' > /etc/locale.conf"),
    ("Setting hostname",
     "echo '{hostname}' > /etc/hostname"),
    ("Setting hosts",
     "cat > /etc/hosts << 'EOF'\n"
     "127.0.0.1 localhost\n"
     "::1 localhost\n"
     "127.0.1.1 {hostname}.localdomain {hostname}\n"
     "EOF"),
    ("Creating user",
     "useradd -m -G wheel,audio,video,storage,power,network "
     "-s /bin/bash {username}"),
    ("Configuring sudo",
     "echo '%wheel ALL=(ALL:ALL) ALL' > /etc/sudoers.d/wheel"),
    ("Enabling NetworkManager",
     "systemctl enable NetworkManager"),
    ("Enabling systemd-resolved",
     "systemctl enable systemd-resolved"),
]

BOOTLOADER_UEFI_CMDS = {
    "grub": [
        "grub-install --target=x86_64-efi --efi-directory=/boot "
        "--bootloader-id=licOS --recheck",
        "grub-mkconfig -o /boot/grub/grub.cfg",
    ],
    "systemd-boot": [
        "bootctl install",
    ],
}

BOOTLOADER_BIOS_CMDS = {
    "grub": [
        "grub-install --target=i386-pc --recheck {disk}",
        "grub-mkconfig -o /boot/grub/grub.cfg",
    ],
}
#hello world