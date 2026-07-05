# ╲ ╳ ╱ licOS

> 基于 Arch Linux 的发行版，配备现代化 TUI 安装器、Plymouth 闪电动画开机画面和 XFCE 桌面环境 — v3.0

licOS 是一个基于 Arch Linux 的发行版，专注于简洁和现代桌面计算。它配备了基于 curses 的终端界面安装器，支持 12 种语言、LUKS 加密、灵活分区，以及一个在开机和安装器中动态劈下的闪电徽标。

## 特性

### v3.0 新增

- **Plymouth 开机动画** — 闪电火花动画 + 进度条
- **XFCE 桌面** — 预配置暗色主题（licOS-dark）和闪电壁纸
- **LightDM 自动登录** — 开机自动进入 XFCE 桌面
- **licos-fetch** — 系统信息 CLI 工具，带闪电 ASCII 艺术
- **licos-welcome** — 交互式欢迎仪表盘（TUI）
- **I/W/F/S/R 快捷键** — 开机快捷键：安装/欢迎/系统信息/Shell/重启
- **CJK 终端字体** — 内置文泉驿正黑（wqy-zenhei）字体，终端完美显示中日韩字符
- **Unicode 控制台** — `ter-132n` 宽 Unicode 控制台字体 + UTF-8 语言环境

### 安装器

- **TUI 安装器** — 简洁的终端界面，键盘导航，侧边栏进度指示
- **12 种语言** — 中文、English、日本語、한국어、Français、Deutsch、Español 等
- **桌面环境** — GNOME、KDE Plasma、XFCE、LXQt、Cinnamon、MATE、i3、Sway
- **LUKS 加密** — LUKS2 + argon2id 磁盘加密（按 E 键切换）
- **灵活分区** — 自动（整盘）或手动，支持 BIOS 和 UEFI
- **文件系统选择** — ext4、btrfs、xfs、f2fs
- **软件包分组** — 开发工具、多媒体、办公、打印、蓝牙、游戏


## 快速开始

### 从 ISO 启动

1. 从 [Releases](https://github.com/howe123456/licOS/releases/tag/v3.0.0) 下载最新 ISO
2. 写入 U 盘：
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. 从 U 盘启动
4. 观看 Plymouth 闪电动画，然后按 **I** 安装或按 **F** 查看系统信息

### 从源码构建

```bash
# 安装依赖
sudo pacman -S archiso

# 克隆并构建
git clone https://github.com/licOS/licOS.git
cd licOS
sudo mkarchiso -v archiso-profile/

# 输出 ISO 在 out/（约 1.8 GB）
ls out/*.iso
```

### 在 QEMU 中运行

```bash
# BIOS
qemu-system-x86_64 -cdrom out/licOS-*.iso -m 4G -enable-kvm

# UEFI
qemu-system-x86_64 -bios /usr/share/edk2/x64/OVMF.4m.fd \
  -cdrom out/licOS-*.iso -m 4G -enable-kvm
```

## 项目结构

```
licOS/
├── installer/                  # Python TUI 安装器
│   ├── core/                   # 安装引擎
│   │   ├── config.py           # 默认配置（桌面环境、软件包等）
│   │   ├── installer.py        # 分区、pacstrap、chroot、引导
│   │   └── utils.py            # 磁盘检测、网络检查等
│   ├── i18n/                   # 国际化
│   │   ├── languages.py        # 12 种语言定义
│   │   └── translations.py     # 翻译字典（1100+ 行）
│   ├── tui/                    # 终端界面
│   │   ├── framework.py        # 控件库（curses）+ 闪电徽标
│   │   └── screens.py          # 10 个安装界面
│   └── __main__.py             # 入口
├── archiso-profile/            # ISO 构建配置
│   ├── grub/                   # GRUB 配置（UEFI）
│   ├── syslinux/               # SYSLINUX 配置（BIOS）
│   ├── airootfs/               # 运行环境覆盖
│   │   ├── etc/                # 系统配置
│   │   │   ├── lightdm/        # LightDM 自动登录 + greeter
│   │   │   ├── mkinitcpio.conf.d/  # mkinitcpio（含 plymouth hook）
│   │   │   ├── skel/           # 默认用户 shell 配置
│   │   │   └── xdg/            # XFCE 面板、xfwm4、xsettings
│   │   ├── root/               # root 用户（运行环境）
│   │   │   ├── .zshrc / .bashrc    # 欢迎横幅 + 快捷键
│   │   │   ├── customize_airootfs.sh  # 安装后自定义脚本
│   │   │   └── licOS/
│   │   │       ├── licos-installer   # Shell 启动脚本
│   │   │       └── welcome/         # 欢迎 TUI 应用
│   │   ├── usr/
│   │   │   ├── local/bin/       # licos-fetch、licos-welcome
│   │   │   ├── share/
│   │   │   │   ├── plymouth/    # licOS-spark 开机主题
│   │   │   │   ├── themes/      # licOS-dark GTK 主题
│   │   │   │   └── backgrounds/ # 闪电壁纸
│   │   │   └── .../
│   │   └── .../
│   ├── packages.x86_64          # 软件包列表
│   ├── profiledef.sh            # 构建配置 + 文件权限
│   └── pacman.conf              # Pacman 配置
├── out/                         # 构建的 ISO 镜像
├── README.md
├── README.zh.md
└── LICENSE
```

## 安装流程

| 步骤 | 界面 | 说明 |
|------|------|------|
| 1 | 语言选择 | 从 12 种语言中选择 |
| 2 | 键盘布局 | 选择键盘布局 |
| 3 | 区域与时区 | 设置区域和时区 |
| 4 | 磁盘选择 | 选择目标磁盘和文件系统 |
| 5 | 分区方式 | 自动或手动分区（E=加密） |
| 6 | 桌面环境 | 选择桌面环境 |
| 7 | 附加软件包 | 选择附加软件包分组 |
| 8 | 用户设置 | 配置主机名、用户、密码 |
| 9 | 安装摘要 | 审查安装设置 |
| 10 | 安装进度 | 进度条和日志输出 |

## 开源协议

[MIT](LICENSE)
