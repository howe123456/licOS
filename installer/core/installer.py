import os
import re
from typing import List, Dict, Optional, Callable
from installer.core.utils import run_cmd, run_cmd_live, detect_uefi, get_disk_prefix
from installer.core.config import (
    BASE_PACKAGES, INSTALL_DIR, CHROOT_COMMANDS,
    BOOTLOADER_UEFI_CMDS, BOOTLOADER_BIOS_CMDS, ADDITIONAL_PACKAGE_GROUPS,
)
from installer.i18n.translations import _

CRYPT_ROOT_NAME = "cryptroot"


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

    def set_default_partitions(self, uefi: bool = True):
        fs = self.filesystem
        if uefi:
            self.partitions = {
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
            self.partitions = {
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

    def _get_root_dev(self) -> str:
        prefix = get_disk_prefix(self.config.disk)
        root_num = self.config.partitions.get("/", {}).get("num", 1)
        return f"{prefix}{root_num}"

    def setup_encryption(self):
        if not self.config.encrypt:
            return
        self.log_t("log_encrypting")
        root_dev = self._get_root_dev()
        encrypt_pass = self.config.encrypt_password or self.config.root_password
        if not encrypt_pass:
            raise RuntimeError("Encryption password not set!")

        pass_file = "/tmp/cryptpass"
        with open(pass_file, "w") as f:
            f.write(encrypt_pass)
        run_cmd([
            "cryptsetup", "luksFormat", "--type", "luks2",
            "--pbkdf", "argon2id", "--iter-time", "2000",
            "--batch-mode", "--key-file", pass_file, root_dev
        ])
        run_cmd([
            "cryptsetup", "open", "--key-file", pass_file,
            root_dev, CRYPT_ROOT_NAME
        ])
        os.remove(pass_file)
        self.log(f"  {root_dev}: LUKS2 encrypted -> /dev/mapper/{CRYPT_ROOT_NAME}")
        self.log_t("log_encrypt_done")

    def format_partitions(self):
        self.log_t("log_formatting")
        c = self.config
        for mount, info in c.partitions.items():
            num = info.get("num")
            prefix = get_disk_prefix(c.disk)
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

            # If encrypted root, format the mapped device not the raw partition
            if mount == "/" and c.encrypt:
                map_dev = f"/dev/mapper/{CRYPT_ROOT_NAME}"
            else:
                map_dev = dev

            if fs == "btrfs":
                run_cmd(["mkfs.btrfs", "-f", map_dev])
            elif fs == "xfs":
                run_cmd(["mkfs.xfs", "-f", map_dev])
            elif fs == "f2fs":
                run_cmd(["mkfs.f2fs", "-f", map_dev])
            else:
                run_cmd(["mkfs.ext4", "-F", map_dev])
            self.log(f"  {map_dev}: {fs}")

        self.log_t("log_format_done")

    def mount_partitions(self):
        self.log_t("log_mounting")
        os.makedirs(INSTALL_DIR, exist_ok=True)
        c = self.config

        swap_dev = None
        root_mounted = False

        for mount, info in c.partitions.items():
            num = info.get("num")
            prefix = get_disk_prefix(c.disk)
            dev = f"{prefix}{num}"

            if mount == "swap":
                swap_dev = dev
                continue

            # If encrypted root, mount the mapped device
            if mount == "/" and c.encrypt:
                mount_dev = f"/dev/mapper/{CRYPT_ROOT_NAME}"
            else:
                mount_dev = dev

            if info.get("boot", False):
                target = os.path.join(INSTALL_DIR, "boot")
                os.makedirs(target, exist_ok=True)
                run_cmd(["mount", mount_dev, target])
                self.log(f"  {mount_dev} -> {target}")
            elif mount == "/":
                run_cmd(["mount", mount_dev, INSTALL_DIR])
                root_mounted = True
                self.log(f"  {mount_dev} -> {INSTALL_DIR}")
            else:
                target = os.path.join(INSTALL_DIR, mount.lstrip("/"))
                os.makedirs(target, exist_ok=True)
                run_cmd(["mount", mount_dev, target])
                self.log(f"  {mount_dev} -> {target}")

        if not root_mounted and c.partitions:
            raise RuntimeError("Root partition (/) not found in config!")

        if swap_dev:
            run_cmd(["swapon", swap_dev])
            self.log(f"  {swap_dev}: swap activated")

        self.log_t("log_mount_done")

    def _get_root_uuid(self) -> str:
        root_dev = self._get_root_dev()
        try:
            result = run_cmd(
                ["blkid", "-s", "UUID", "-o", "value", root_dev], capture=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def install_base(self):
        self.log_t("log_installing_base")
        packages = BASE_PACKAGES.copy()

        if self.config.encrypt and "cryptsetup" not in packages:
            packages.insert(0, "cryptsetup")

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

    def _setup_mkinitcpio_encrypt(self):
        if not self.config.encrypt:
            return
        self.log_t("log_mkinitcpio_encrypt")
        conf_path = os.path.join(INSTALL_DIR, "etc", "mkinitcpio.conf")
        if not os.path.exists(conf_path):
            self.log("  mkinitcpio.conf not found, skipping")
            return

        with open(conf_path, "r") as f:
            content = f.read()

        # Insert "encrypt" hook before "filesystems" in the HOOKS array
        content = re.sub(
            r'^(HOOKS=\([^)]*?\b)(filesystems\b)',
            r'\1encrypt \2',
            content,
            count=1, flags=re.MULTILINE
        )

        with open(conf_path, "w") as f:
            f.write(content)

        run_cmd([
            "arch-chroot", INSTALL_DIR,
            "mkinitcpio", "-P"
        ])
        self.log_t("log_mkinitcpio_encrypt_done")

    def _add_cryptdevice_to_grub(self):
        root_uuid = self._get_root_uuid()
        if not root_uuid:
            self.log("  Warning: could not determine root UUID for cryptdevice")
            return

        grub_cfg = os.path.join(INSTALL_DIR, "etc", "default", "grub")
        if not os.path.exists(grub_cfg):
            self.log("  /etc/default/grub not found, skipping")
            return

        crypt_cmd = f"cryptdevice=UUID={root_uuid}:{CRYPT_ROOT_NAME}"
        with open(grub_cfg, "r") as f:
            content = f.read()

        content = re.sub(
            r'^GRUB_CMDLINE_LINUX="(.*?)"',
            lambda m: f'GRUB_CMDLINE_LINUX="{m.group(1)} {crypt_cmd}"',
            content, count=1, flags=re.MULTILINE
        )

        with open(grub_cfg, "w") as f:
            f.write(content)

        base_disk = re.sub(r"p?\d+$", "", self.config.disk)
        if self.config.disk.startswith("/dev/nvme"):
            m = re.match(r"(/dev/nvme\d+n\d+)", self.config.disk)
            if m:
                base_disk = m.group(1)

        run_cmd([
            "arch-chroot", INSTALL_DIR,
            "grub-mkconfig", "-o", "/boot/grub/grub.cfg"
        ])

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
                username=c.username,
            )
            self.log(f"  {label}...")
            run_cmd(["arch-chroot", INSTALL_DIR, "sh", "-c", cmd])

        # Set passwords via stdin script to avoid shell escaping issues
        pass_script = os.path.join(INSTALL_DIR, "tmp", "setpass.sh")
        os.makedirs(os.path.join(INSTALL_DIR, "tmp"), exist_ok=True)
        with open(pass_script, "w") as f:
            f.write("#!/bin/sh\n")
            f.write('read root_pass\n')
            f.write('read user_pass\n')
            f.write('read user_name\n')
            f.write('printf \'%s\\n\' "$root_pass" "$root_pass" | passwd\n')
            f.write('printf \'%s\\n\' "$user_pass" "$user_pass" | passwd "$user_name"\n')
        os.chmod(pass_script, 0o700)

        self.log("  Setting root password...")
        import subprocess
        proc = subprocess.Popen(
            ["arch-chroot", INSTALL_DIR, "sh", "/tmp/setpass.sh"],
            stdin=subprocess.PIPE, text=True
        )
        proc.communicate(input=f"{c.root_password}\n{c.user_password}\n{c.username}\n")
        os.remove(pass_script)

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

        if c.encrypt and c.bootloader == "grub":
            self._add_cryptdevice_to_grub()

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

        crypt_cmdline = f"cryptdevice=UUID={uuid}:{CRYPT_ROOT_NAME} root=/dev/mapper/{CRYPT_ROOT_NAME}" if self.config.encrypt and uuid else f"root={'UUID=' + uuid if uuid else root_dev}"
        entry = (
            f"title   licOS\n"
            f"linux   /vmlinuz-linux\n"
            f"initrd  /initramfs-linux.img\n"
            f"options {crypt_cmdline} rw\n"
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

    def install(self):
        steps = [
            (_("log_preparing"), self.prepare_disk),
            (_("log_encrypting"), self.setup_encryption),
            (_("log_formatting"), self.format_partitions),
            (_("log_mounting"), self.mount_partitions),
            (_("log_installing_base"), self.install_base),
            (_("log_generating_fstab"), self.generate_fstab),
            (_("log_mkinitcpio_encrypt"), self._setup_mkinitcpio_encrypt),
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
        if self.config.encrypt:
            try:
                run_cmd(["cryptsetup", "close", CRYPT_ROOT_NAME], check=False)
                self.log(f"  /dev/mapper/{CRYPT_ROOT_NAME}: closed")
            except Exception as e:
                self.log(f"  cryptsetup close warning: {e}")
        try:
            result = run_cmd(["swapoff", "-a"], check=False)
            if result.returncode != 0:
                self.log(f"  swapoff warning (non-fatal): {result.stderr}")
        except Exception as e:
            self.log(f"  swapoff error (non-fatal): {e}")
        try:
            result = run_cmd(["umount", "-R", INSTALL_DIR], check=False)
            if result.returncode != 0:
                self.log(f"  umount warning (non-fatal): {result.stderr}")
        except Exception as e:
            self.log(f"  umount error (non-fatal): {e}")
        self.log_t("log_cleanup_done")
#hello world