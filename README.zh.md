# ╲ ╳ ╱ licOS

> 基于 Arch Linux 的发行版，配备现代化 TUI 安装器、Plymouth 闪电动画开机画面和 XFCE 桌面环境 — v4.0 LTS

licOS 是一个基于 Arch Linux 的发行版，专注于简洁和现代桌面计算。它配备了基于 curses 的终端界面安装器，支持 12 种语言、LUKS 加密、灵活分区、在开机和安装器中动态劈下的闪电徽标，以及通过交互式 TUI 启动器展示 XFCE 暗色桌面主题（licOS-dark）的功能。本项目有局限性。

## 特性

### v4.0 LTS — 首个长期支持版本

- **lidlm（macOS 桌面）** — macOS 风格桌面：顶部菜单栏 + 底部 Dock（自动隐藏）
- **lidlh（混合桌面）** — 混合桌面：单个底部面板，融合传统应用菜单和现代 Dock 元素
- **licfetch** — 闪电字符画系统信息工具（Python，类似 fastfetch/neofetch，将 "A" 改为大 ╲╳╱ 闪电）
- **大型闪电艺术** — 所有闪电动画升级为 8 行以上的框线字符画：Plymouth 开机动画、欢迎界面、licfetch
- **启动画面** — SYSLINUX 和 systemd-boot 显示 "archlinux & licOS" 品牌标识
- **安装提速** — 运行环境启用 `ParallelDownloads=20`、精简镜像源列表（USTC、清华、阿里 + 备用）
- **CJK 字体修复** — wqy-zenhei 通过 pacman 安装，`licos-cjk.service` 保证字体立即可用

### v3.0 新增

- **C 语言重写** — 所有 Shell 工具重写为编译型 C 二进制（~15K）：licos-launcher、licos-about、licos-fetch、licos-welcome、licos-setup
- **licos-setup 服务** — 新增 systemd 专用服务，首次启动自动应用系统覆盖配置（zshrc、XFCE 面板）
- **licos-about** — 交互式桌面展示，突出 licOS 特色功能
- **licos-launcher** — 开机 TUI 主菜单，含桌面展示入口
- **1/I/W/F/S/R 快捷键** — 开机快捷键：启动器/安装/欢迎/系统信息/Shell/重启
- **Shell 品牌定制** — .zshrc / .bashrc 自定义 MOTD 和提示符

### v2.0 新增

- **Plymouth 开机动画** — 闪电火花动画 + 进度条
- **XFCE 桌面** — 预配置暗色主题（licOS-dark）和闪电壁纸
- **LightDM 自动登录** — 开机自动进入 XFCE 桌面
- **licos-fetch** — 系统信息 CLI 工具，带闪电 ASCII 艺术（Shell 版本）
- **licos-welcome** — 交互式欢迎仪表盘（Shell 版本）
- **CJK 终端字体** — 内置文泉驿正黑（wqy-zenhei）字体
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

1. 从 [Releases](https://github.com/howe123456/licOS/releases/tag/v4.0) 下载最新 ISO
2. 写入 U 盘：
   ```bash
   sudo dd bs=4M if=licOS-*.iso of=/dev/sdX status=progress
   ```
3. 从 U 盘启动
4. 观看 Plymouth 闪电动画，然后按 **1** 浏览桌面展示、**I** 安装或 **F** 查看系统信息

### 从源码构建

```bash
# 安装依赖（可选：nginx 用于本地缓存代理）
sudo pacman -S archiso nginx

# 克隆并构建
git clone https://github.com/licOS/licOS.git
cd licOS

# 快速构建（预下载包、缓存代理、增量构建）
sudo ./archiso-profile/build.sh

# 手动构建
sudo mkarchiso -v archiso-profile/

# 输出 ISO 在 out/（约 1.8 GB）
ls out/*.iso
```

> **构建加速**：
> - `build.sh` 自动启动本地 nginx 缓存代理（`localhost:8080`）
> - 包在 `mkarchiso` 运行前预下载到主机缓存
> - 默认使用 USTC 镜像（国内最快）
> - `ParallelDownloads=20` 并发下载
> - `work/` 目录保留，支持增量构建（重复构建只需 ~5 分钟）
> - 设置 nginx 缓存代理：`sudo systemctl enable --now nginx`

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
│   │   │   └── xdg/            # 桌面面板配置（XFCE、lidlm、lidlh）
│   │   ├── root/               # root 用户（运行环境）
│   │   │   ├── .zshrc / .bashrc    # 欢迎横幅 + 快捷键
│   │   │   ├── start-licos     # 备用启动器（C ELF，15K）
│   │   │   ├── customize_airootfs.sh  # 安装后自定义脚本
│   │   │   └── licOS/
│   │   │       ├── licos-installer   # 安装器（C ELF，15K）
│   │   │       └── welcome/         # 欢迎 TUI 应用
│   │   ├── usr/
│   │   │   ├── local/bin/       # CLI 工具和桌面入口
│   │   │   │   ├── licos-fetch、licos-welcome、licos-launcher、...
│   │   │   │   ├── licos-setup、lidlm-setup、lidlh-setup
│   │   │   ├── share/
│   │   │   │   ├── xsessions/   # lidlm.desktop、lidlh.desktop
│   │   │   │   ├── systemd/bootctl/  # splash-arch.bmp（UEFI 启动画面）
│   │   │   │   ├── plymouth/    # licOS-spark 开机主题
│   │   │   │   ├── themes/      # licOS-dark GTK 主题
│   │   │   │   ├── backgrounds/ # 闪电壁纸
│   │   │   │   └── overrides/   # 首次启动覆盖配置
│   │   │   │       ├── root.zshrc
│   │   │   │       ├── skel.zshrc
│   │   │   │       ├── xfce4-panel.xml
│   │   │   │       └── xfce4-xsettings.xml
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

> *"希望有一天大家不再问'怎么装 arch'，而是直接问'licOS 的下个版本什么时候出'。"*

## 开源协议

[MIT](LICENSE)
