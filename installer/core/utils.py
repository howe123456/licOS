import os
import re
import subprocess
from typing import List, Dict, Optional, Tuple


def run_cmd(cmd: List[str], check: bool = True,
            capture: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n{result.stderr}"
        )
    return result


def run_cmd_live(cmd: List[str], log_func=None) -> int:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    for line in process.stdout:
        line = line.rstrip()
        if log_func:
            log_func(line)
    process.wait()
    return process.returncode


def detect_uefi() -> bool:
    return os.path.exists("/sys/firmware/efi")


def get_disks() -> List[Dict]:
    disks = []
    try:
        for dev in os.listdir("/sys/block"):
            if dev.startswith(("sd", "nvme", "vd", "hd", "mmcblk", "loop")):
                path = f"/dev/{dev}"
                removable = False
                try:
                    with open(f"/sys/block/{dev}/removable") as f:
                        removable = f.read().strip() == "1"
                except Exception:
                    pass
                if removable:
                    continue
                size_str = "?"
                try:
                    result = run_cmd(
                        ["lsblk", "-d", "-n", "-o", "SIZE", path],
                        capture=True
                    )
                    size_str = result.stdout.strip()
                except Exception:
                    pass
                model = ""
                try:
                    mp = f"/sys/block/{dev}/device/model"
                    if os.path.exists(mp):
                        with open(mp) as f:
                            model = f.read().strip()
                except Exception:
                    pass
                disks.append({
                    "path": path,
                    "name": dev,
                    "size": size_str,
                    "model": model,
                    "type": "nvme" if dev.startswith("nvme") else "sata",
                })
    except Exception:
        pass
    return disks


def get_partitions(disk: str) -> List[Dict]:
    parts = []
    try:
        result = run_cmd(
            ["lsblk", "-n", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT",
             disk], capture=True
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line:
                parts.append(line.strip())
    except Exception:
        pass
    return parts


def get_memory() -> Tuple[str, str]:
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        avail_gb = mem.available / (1024 ** 3)
        return f"{total_gb:.1f} GB", f"{avail_gb:.1f} GB"
    except Exception:
        return "?", "?"


def get_cpu_info() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except Exception:
        pass
    return "Unknown"


def check_internet() -> bool:
    result = run_cmd(["ping", "-c", "1", "-W", "3", "archlinux.org"],
                     check=False)
    return result.returncode == 0


def check_arch_iso() -> bool:
    return (os.path.exists("/etc/arch-release") or
            os.path.exists("/usr/bin/pacstrap"))


def get_timezones() -> List[str]:
    zones = []
    try:
        for root, dirs, files in os.walk("/usr/share/zoneinfo"):
            for f in files:
                path = os.path.join(root, f)
                rel = path.replace("/usr/share/zoneinfo/", "")
                if "/" in rel:
                    zones.append(rel)
    except Exception:
        pass
    zones.sort()
    return zones


def human_size(bytes_val: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"


def get_disk_prefix(disk: str) -> str:
    if re.match(r"/dev/nvme\d+n\d+", disk):
        return f"{disk}p"
    if re.match(r"/dev/mmcblk\d+", disk):
        return f"{disk}p"
    if re.match(r"/dev/loop\d+", disk):
        return f"{disk}p"
    return disk


def get_base_disk(dev: str) -> str:
    m = re.match(r"(/dev/nvme\d+n\d+)", dev)
    if m:
        return m.group(1)
    m = re.match(r"(/dev/mmcblk\d+)", dev)
    if m:
        return m.group(1)
    m = re.match(r"(/dev/loop\d+)", dev)
    if m:
        return m.group(1)
    m = re.match(r"(/dev/[a-z]+)", dev)
    if m:
        return m.group(1)
    return dev
#hello world 