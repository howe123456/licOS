import os
import re
from typing import List, Dict, Optional, Callable
from installer.core.utils import run_cmd, run_cmd_live, detect_uefi, get_disk_prefix
from installer.core.config import (
    BASE_PACKAGES, INSTALL_DIR, CHROOT_COMMANDS,
    BOOTLOADER_UEFI_CMDS, BOOTLOADER_BIOS_CMDS, ADDITIONAL_PACKAGE_GROUPS,
)
from installer.i18n.translations import _


class InstallerConfig:
    def __init__(self):
        self.disk: str = ""
        self.partitions: Dict[str, dict] = {}
        self.filesystem: str = "ext4"
        self.encrypt: bool = False
        self.encrypt_password: str = ""
        self.keyboard_layout: str = "us"
        self.locale: str = "en_US.UTF-8"
        self.timezone: str = "UTC"
        self.hostname: str = "licos"
        self.username: str = "user"
        self.root_password: str = ""
        self.user_password: str = ""
        self.desktop: str = ""
        self.desktop_packages: List[str] = None
        self.display_manager: Optional[str] = None
        self.additional_groups: List[str] = None
        self.bootloader: str = "grub"
        self.swap: bool = True
        self.swap_size: str = "2G"


class Installer:
    def __init__(self, config: InstallerConfig,
                 log_callback: Callable = None):
        self.config = config
        self.log_callback = log_callback or (lambda x: None)
        self.uefi = detect_uefi()

    def log(self, msg: str):
        if self.log_callback:
            self.log_callback(msg)

    def log_t(self, key: str, *args, **kwargs):
        self.log(_(key, *args, **kwargs))

    def _get_part_dev(self, mount: str) -> str:
        info = self.config.partitions.get(mount, {})
        num = info.get("num", 1)
        prefix = get_disk_prefix(self.config.disk)
        return f"{prefix}{num}"

    def prepare_disk(self):
        self.log_t("log_preparing")
        disk = self.config.disk

        run_cmd(["wipefs", "-a", disk])

        if self.uefi:
            run_cmd(["parted", "-s", disk, "mklabel", "gpt"])
        else:
            run_cmd(["parted", "-s", disk, "mklabel", "msdos"])

        part_num = 1
        esp_part_num = None

        for mount, info in self.config.partitions.items():
            info["num"] = part_num
            start = info.get("start", "1MiB")
            end = info.get("end", "100%")
            fs_type = info.get("fs_type", "ext4")
            part_type = info.get("part_type", "primary")

            if self.uefi:
                run_cmd(["parted", "-s", disk, "mkpart", fs_type, start, end])
            else:
                run_cmd(["parted", "-s", disk, "mkpart", part_type, fs_type,
                        start, end])

            if info.get("boot", False) and self.uefi:
                run_cmd(["parted", "-s", disk, "set", str(part_num),
                        "esp", "on"])
                esp_part_num = part_num

            if info.get("boot", False) and not self.uefi:
                run_cmd(["parted", "-s", disk, "set", str(part_num),
                        "boot", "on"])

            self.log(f"  Partition {part_num}: {mount} ({start} -> {end})")
            part_num += 1

        self.log_t("log_partition_done")

    def format_partitions(self):
        self.log_t("log_formatting")
        for mount, info in self.config.partitions.items():
            num = info.get("num")
            prefix = get_disk_prefix(self.config.disk)
            dev = f"{prefix}{num}"
            fs = info.get("fs_type", "ext4")
            is_boot = info.get("boot", False)
            is_swap = (mount == "swap")

            if is_swap:
                run_cmd(["mkswap", dev])
                self.log(f"  {dev}: swap created")
                continue

            if is_boot:
                run_cmd(["mkfs.fat", "-F32", dev])
                self.log(f"  {dev}: FAT32 (EFI/boot)")
                continue

            if fs == "btrfs":
                run_cmd(["mkfs.btrfs", "-f", dev])
            elif fs == "xfs":
                run_cmd(["mkfs.xfs", "-f", dev])
            elif fs == "f2fs":
                run_cmd(["mkfs.f2fs", "-f", dev])
            else:
                run_cmd(["mkfs.ext4", "-F", dev])
            self.log(f"  {dev}: {fs}")

        self.log_t("log_format_done")

    def mount_partitions(self):
        self.log_t("log_mounting")
        os.makedirs(INSTALL_DIR, exist_ok=True)

        swap_dev = None
        root_mounted = False

        for mount, info in self.config.partitions.items():
            num = info.get("num")
            prefix = get_disk_prefix(self.config.disk)
            dev = f"{prefix}{num}"

            if mount == "swap":
                swap_dev = dev
                continue

            if info.get("boot", False):
                target = os.path.join(INSTALL_DIR, "boot")
                os.makedirs(target, exist_ok=True)
                run_cmd(["mount", dev, target])
                self.log(f"  {dev} -> {target}")
            elif mount == "/":
                run_cmd(["mount", dev, INSTALL_DIR])
                root_mounted = True
                self.log(f"  {dev} -> {INSTALL_DIR}")
            else:
                target = os.path.join(INSTALL_DIR, mount.lstrip("/"))
                os.makedirs(target, exist_ok=True)
                run_cmd(["mount", dev, target])
                self.log(f"  {dev} -> {target}")

        if not root_mounted and self.config.partitions:
            raise RuntimeError("Root partition (/) not found in config!")

        if swap_dev:
            run_cmd(["swapon", swap_dev])
            self.log(f"  {swap_dev}: swap activated")

        self.log_t("log_mount_done")

    def install_base(self):
        self.log_t("log_installing_base")
        packages = BASE_PACKAGES.copy()

        if self.config.desktop_packages:
            packages.extend(self.config.desktop_packages)

        if self.config.additional_groups:
            for group in self.config.additional_groups:
                if group in ADDITIONAL_PACKAGE_GROUPS:
                    packages.extend(
                        ADDITIONAL_PACKAGE_GROUPS[group]["packages"]
                    )

        cmd = ["pacstrap", "-K", INSTALL_DIR] + packages
        ret = run_cmd_live(cmd, log_func=self.log)
        if ret != 0:
            raise RuntimeError(_("err_pacstrap"))
        self.log_t("log_base_done")

    def generate_fstab(self):
        self.log_t("log_generating_fstab")
        gen = run_cmd(["genfstab", "-U", INSTALL_DIR], capture=True)
        fstab_path = os.path.join(INSTALL_DIR, "etc", "fstab")
        with open(fstab_path, "w") as f:
            f.write(gen.stdout)
        self.log_t("log_fstab_done")

    def configure_system(self):
        self.log_t("log_configuring")
        c = self.config

        for label, cmd_template in CHROOT_COMMANDS:
            cmd = cmd_template.format(
                timezone=c.timezone,
                locale=c.locale,
                hostname=c.hostname,
                root_password=c.root_password.replace("'", "'\\''"),
                username=c.username,
                user_password=c.user_password.replace("'", "'\\''"),
            )
            self.log(f"  {label}...")
            run_cmd(["arch-chroot", INSTALL_DIR, "sh", "-c", cmd])

        self.log_t("log_config_done")

    def install_bootloader(self):
        self.log_t("log_bootloader")
        c = self.config
        disk = c.disk

        if self.uefi:
            cmds = BOOTLOADER_UEFI_CMDS.get(c.bootloader,
                                            BOOTLOADER_UEFI_CMDS["grub"])
        else:
            cmds = BOOTLOADER_BIOS_CMDS.get(c.bootloader,
                                            BOOTLOADER_BIOS_CMDS["grub"])

        base_disk = re.sub(r"p?\d+$", "", disk)
        if disk.startswith("/dev/nvme"):
            m = re.match(r"(/dev/nvme\d+n\d+)", disk)
            if m:
                base_disk = m.group(1)

        for cmd in cmds:
            full_cmd = cmd.format(disk=base_disk)
            run_cmd(["arch-chroot", INSTALL_DIR, "sh", "-c", full_cmd])

        if c.bootloader == "systemd-boot":
            self._setup_systemd_boot()

        self.log_t("log_bootloader_done")

    def _setup_systemd_boot(self):
        entries_dir = os.path.join(INSTALL_DIR, "boot", "loader", "entries")
        os.makedirs(entries_dir, exist_ok=True)

        root_dev = self._get_part_dev("/")
        uuid = ""
        try:
            result = run_cmd(
                ["blkid", "-s", "UUID", "-o", "value", root_dev],
                capture=True
            )
            uuid = result.stdout.strip()
        except Exception:
            pass

        if not uuid:
            try:
                result = run_cmd(
                    ["blkid", "-s", "PARTUUID", "-o", "value", root_dev],
                    capture=True
                )
                uuid = result.stdout.strip()
            except Exception:
                pass

        entry = (
            f"title   licOS\n"
            f"linux   /vmlinuz-linux\n"
            f"initrd  /initramfs-linux.img\n"
            f"options root={'UUID=' + uuid if uuid else root_dev} rw\n"
        )
        entry_path = os.path.join(entries_dir, "licos.conf")
        with open(entry_path, "w") as f:
            f.write(entry)

        loader_conf = os.path.join(INSTALL_DIR, "boot", "loader",
                                   "loader.conf")
        with open(loader_conf, "w") as f:
            f.write("default licos\n")
            f.write("timeout 4\n")
            f.write("console-mode keep\n")

    def enable_display_manager(self):
        if self.config.display_manager:
            self.log_t("log_enabling_dm")
            run_cmd([
                "arch-chroot", INSTALL_DIR,
                "systemctl", "enable", self.config.display_manager
            ])
            self.log_t("log_dm_done")

    def set_keyboard_layout(self):
        if self.config.keyboard_layout and self.config.keyboard_layout != "us":
            vconsole = os.path.join(INSTALL_DIR, "etc", "vconsole.conf")
            with open(vconsole, "w") as f:
                f.write(f"KEYMAP={self.config.keyboard_layout}\n")

    def copy_mirrorlist(self):
        mirror_src = "/etc/pacman.d/mirrorlist"
        mirror_dst = os.path.join(INSTALL_DIR, "etc", "pacman.d", "mirrorlist")
        if os.path.exists(mirror_src):
            import shutil
            os.makedirs(os.path.dirname(mirror_dst), exist_ok=True)
            shutil.copy2(mirror_src, mirror_dst)
            self.log("  Mirrorlist copied to target system")

    def install(self):
        steps = [
            (_("log_preparing"), self.prepare_disk),
            (_("log_formatting"), self.format_partitions),
            (_("log_mounting"), self.mount_partitions),
            (_("log_installing_base"), self.install_base),
            (_("log_generating_fstab"), self.generate_fstab),
            ("Mirrorlist", self.copy_mirrorlist),
            (_("log_configuring"), self.configure_system),
            (_("log_bootloader"), self.install_bootloader),
            (_("log_enabling_dm"), self.enable_display_manager),
            ("Keyboard layout", self.set_keyboard_layout),
        ]

        total = len(steps)
        for i, (name, func) in enumerate(steps):
            self.log(f"[{i + 1}/{total}] {name}")
            func()
            self.log(f"[OK] {name}")

        self.log_t("log_done")
        return True

    def cleanup(self):
        self.log_t("log_cleanup")
        try:
            try:
                run_cmd(["swapoff", "-a"], check=False)
            except Exception:
                pass
            run_cmd(["umount", "-R", INSTALL_DIR], check=False)
        except Exception:
            pass
        self.log_t("log_cleanup_done")
