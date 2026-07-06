#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="licOS"
iso_label="LICOS_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="licOS <https://licos.dev>"
iso_application="licOS Linux Live/Installer DVD v2.1"
iso_version="2.1"
install_dir="licos"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/etc/systemd/system/licos-setup.service"]="0:0:644"
  ["/etc/systemd/system/licos-cjk.service"]="0:0:644"
  ["/etc/systemd/system/licos-locale.service"]="0:0:644"
  ["/etc/locale.gen"]="0:0:644"
  ["/etc/fonts/local.conf"]="0:0:644"
  ["/root/.config/xfce4/terminal/terminalrc"]="0:0:644"
  ["/etc/skel/.config/xfce4/terminal/terminalrc"]="0:0:644"
  ["/root/start-licos"]="0:0:755"
  ["/root/licOS/licos-installer"]="0:0:755"
  ["/root/licOS/welcome/welcome.py"]="0:0:755"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/licos-fetch"]="0:0:755"
  ["/usr/local/bin/licos-welcome"]="0:0:755"
  ["/usr/local/bin/licos-launcher"]="0:0:755"
  ["/usr/local/bin/licos-about"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/licos-setup"]="0:0:755"
)