# ╲ ╳ ╱ licOS

> 基于 Arch Linux 的发行版，配备现代化的 TUI 安装器和动态闪电徽标。

licOS 是一个基于 Arch Linux 的发行版，专注于简洁和现代桌面计算。它配备了基于 curses 的终端用户界面安装器，支持 12 种语言、多种桌面环境、自动化分区，以及一个在启动时和安装器右上角动态劈下的闪电徽标。

## 特性

- **TUI 安装器** — 简洁的终端界面，键盘导航，侧边栏进度指示
- **12 种语言** — 中文、English、日本語、한국어、Français、Deutsch、Español 等
- **桌面环境** — GNOME、KDE Plasma、XFCE、LXQt、Cinnamon、MATE、i3、Sway
- **灵活分区** — 自动（整盘）或手动，支持 BIOS 和 UEFI
- **文件系统选择** — ext4、btrfs、xfs、f2fs
- **软件包分组** — 开发工具、多媒体、办公、打印、蓝牙、游戏
- **动态闪电徽标** — 开机时和安装器右上角播放一次劈闪动画，随后静止
- **Live ISO** — 基于 archiso 构建的可启动 BIOS/UEFI 镜像

## 快速开始

### 从 ISO 启动

1. 从 [Releases](https://github.com/licOS/licOS/releases) 下载最新 ISO
2. 写入 U 盘：
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. 从 U 盘启动
4. 观看闪电动画，然后在欢迎界面输入 `licos` 启动安装器

### 从源码构建

```bash
# 安装依赖
sudo pacman -S archiso

# 克隆并构建
git clone https://github.com/licOS/licOS.git
cd licOS
sudo mkarchiso -v archiso-profile/

# 输出 ISO 在 out/
ls out/*.iso
```

### 在 QEMU 中运行

```bash
qemu-system-x86_64 -cdrom out/licOS-*.iso -m 4G -enable-kvm
```

## 项目结构

```
licOS/
├── installer/              # Python TUI 安装器
│   ├── core/               # 安装引擎
│   │   ├── config.py       # 默认配置（桌面环境、软件包等）
│   │   ├── installer.py    # 分区、pacstrap、chroot、引导
│   │   └── utils.py        # 磁盘检测、网络检查等
│   ├── i18n/               # 国际化
│   │   ├── languages.py    # 12 种语言定义
│   │   └── translations.py # 翻译字典（1100+ 行）
│   ├── tui/                # 终端界面
│   │   ├── framework.py    # 控件库（curses）+ 闪电徽标
│   │   └── screens.py      # 10 个安装界面
│   └── __main__.py         # 入口
├── archiso-profile/        # ISO 构建配置（GRUB、Syslinux、systemd-boot）
├── licos-installer         # Shell 启动脚本
├── out/                    # 构建的 ISO 镜像
├── README.md
└── LICENSE
```

## 安装流程

| 步骤 | 界面 | 说明 |
|------|------|------|
| 1 | 语言选择 | 从 12 种语言中选择 |
| 2 | 键盘布局 | 选择键盘布局 |
| 3 | 区域与时区 | 设置区域和时区 |
| 4 | 磁盘选择 | 选择目标磁盘和文件系统 |
| 5 | 分区方式 | 自动或手动分区 |
| 6 | 桌面环境 | 选择桌面环境 |
| 7 | 附加软件包 | 选择附加软件包分组 |
| 8 | 用户设置 | 配置主机名、用户、密码 |
| 9 | 安装摘要 | 审查安装设置 |
| 10 | 安装进度 | 进度条和日志输出 |

## 开源协议

[MIT](LICENSE)
