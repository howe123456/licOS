#!/usr/bin/env bash
#
# licOS v3.0 - post-install customization
# Runs inside the airootfs chroot AFTER package installation.
# Writes custom configs for XFCE, LightDM, Plymouth, and shells.

set -euo pipefail

# --- Ensure directories exist ---
mkdir -p /etc/skel
mkdir -p /etc/xdg/xfce4/panel
mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml

# --- skel .zshrc (default for new users) ---
cat > /etc/skel/.zshrc << 'ZTHELP'
[[ -o interactive ]] || return 0

# licOS v3.0 - default .zshrc for new users

print -P ""
print -P "%F{cyan}╔══════════════════════════════════════════════╗%f"
print -P "%F{cyan}║  %F{yellow}        Welcome to licOS v3.0!%F{cyan}             ║%f"
print -P "%F{cyan}║  %F{green}     Arch Linux with XFCE Desktop%F{cyan}         ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╠══════════════════════════════════════════════╣%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}licos%F{white}' to start the installer%F{cyan}         ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}fetch%F{white}' for system info%F{cyan}               ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╚══════════════════════════════════════════════╝%f"
print -P ""

alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
ZTHELP

# --- skel .bashrc (default for new users) ---
cat > /etc/skel/.bashrc << 'BTHELP'
[[ $- != *i* ]] && return

# licOS v3.0 - default .bashrc for new users

echo -e "\e[36m╔══════════════════════════════════════════════╗\e[0m"
echo -e "\e[36m║  \e[33m        Welcome to licOS v3.0!\e[36m             ║\e[0m"
echo -e "\e[36m║  \e[32m     Arch Linux with XFCE Desktop\e[36m         ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╠══════════════════════════════════════════════╣\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m║  \e[97mType '\e[32mlicos\e[97m' to start the installer\e[36m         ║\e[0m"
echo -e "\e[36m║  \e[97mType '\e[32mfetch\e[97m' for system info\e[36m               ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╚══════════════════════════════════════════════╝\e[0m"
echo ""

alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
BTHELP

# --- XFCE panel default.xml ---
cat > /etc/xdg/xfce4/panel/default.xml << 'PANEL'
<?xml version="1.0" encoding="UTF-8"?>

<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="30"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/>
        <value type="int" value="2"/>
        <value type="int" value="3"/>
        <value type="int" value="4"/>
        <value type="int" value="5"/>
        <value type="int" value="6"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="applicationsmenu">
      <property name="show-button-title" type="bool" value="true"/>
      <property name="show-button-icon" type="bool" value="false"/>
      <property name="button-title" type="string" value="licOS"/>
    </property>
    <property name="plugin-2" type="string" value="tasklist">
      <property name="show-wireframes" type="bool" value="false"/>
      <property name="show-handle" type="bool" value="false"/>
    </property>
    <property name="plugin-3" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-4" type="string" value="pager"/>
    <property name="plugin-5" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-6" type="string" value="datetime">
      <property name="format" type="string" value="%Y-%m-%d %H:%M"/>
    </property>
  </property>
</channel>
PANEL

# --- XFCE xsettings.xml (GTK theme) ---
cat > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml << 'XSET'
<?xml version="1.0" encoding="UTF-8"?>

<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="licOS-dark"/>
    <property name="IconThemeName" type="string" value="Adwaita"/>
  </property>
</channel>
XSET

# --- root .zshrc (live user) ---
cat > /root/.zshrc << 'ZROOT'
[[ -o interactive ]] || return 0

clear

# Lightning bolt animation (plays once before welcome banner)
_licos_anim() {
  local cols="${COLUMNS:-80}" lx=$(( cols - 8 ))
  printf '\e[?25l'
  printf "\e[2;${lx}H     \e[3;${lx}H     \e[4;${lx}H     "; sleep 0.08
  printf "\e[2;${lx}H\e[2m  .  \e[3;${lx}H\e[2m ... \e[4;${lx}H\e[2m  .  \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  \\\\  \e[4;${lx}H\e[33m   / \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  X  \e[4;${lx}H\e[33m /   \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[1;37m === \e[3;${lx}H\e[1;37m =O= \e[4;${lx}H\e[1;37m === \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  X  \e[4;${lx}H\e[33m /   \e[0m"
  printf '\e[?25h'
}
_licos_anim
unset -f _licos_anim

print -P ""
print -P "%F{cyan}╔══════════════════════════════════════════════╗%f"
print -P "%F{cyan}║                                            %F{yellow}╲%F{cyan} ║%f"
print -P "%F{cyan}║  %F{yellow}       Welcome to licOS v3.0!%F{cyan}            %F{yellow}╳%F{cyan} ║%f"
print -P "%F{cyan}║  %F{green}     Arch Linux with XFCE Desktop%F{cyan}        %F{yellow}╱%F{cyan} ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╠══════════════════════════════════════════════╣%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}I%F{white}] Install licOS%F{cyan}                       ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}W%F{white}] Welcome Dashboard%F{cyan}                  ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}F%F{white}] System Info (licos-fetch)%F{cyan}           ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}S%F{white}] Shell (stay here)%F{cyan}                  ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}R%F{white}] Reboot%F{cyan}                             ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╚══════════════════════════════════════════════╝%f"
print -P ""

# Key handler: wait 5 seconds for a keypress
read -t 5 -k 1 _choice
case "${_choice}" in
  [iI]) /root/licOS/licos-installer ;;
  [wW]) licos-welcome ;;
  [fF]) licos-fetch ;;
  [rR]) sudo reboot ;;
esac
unset _choice

alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
ZROOT

# --- root .bashrc (live user) ---
cat > /root/.bashrc << 'BROOT'
[[ $- != *i* ]] && return

clear

# Lightning bolt animation
_licos_anim() {
  local cols="${COLUMNS:-80}" lx=$(( cols - 8 ))
  printf '\e[?25l'
  printf "\e[2;${lx}H     \e[3;${lx}H     \e[4;${lx}H     "; sleep 0.08
  printf "\e[2;${lx}H\e[2m  .  \e[3;${lx}H\e[2m ... \e[4;${lx}H\e[2m  .  \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  \\\\  \e[4;${lx}H\e[33m   / \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  X  \e[4;${lx}H\e[33m /   \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[1;37m === \e[3;${lx}H\e[1;37m =O= \e[4;${lx}H\e[1;37m === \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m \\\\   \e[3;${lx}H\e[33m  X  \e[4;${lx}H\e[33m /   \e[0m"
  printf '\e[?25h'
}
_licos_anim
unset -f _licos_anim

echo ""
echo -e "\e[36m╔══════════════════════════════════════════════╗\e[0m"
echo -e "\e[36m║                                            \e[33m╲\e[36m ║\e[0m"
echo -e "\e[36m║  \e[33m       Welcome to licOS v3.0!\e[36m             \e[33m╳\e[36m ║\e[0m"
echo -e "\e[36m║  \e[32m     Arch Linux with XFCE Desktop\e[36m         \e[33m╱\e[36m ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╠══════════════════════════════════════════════╣\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mI\e[97m] Install licOS\e[36m                       ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mW\e[97m] Welcome Dashboard\e[36m                  ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mF\e[97m] System Info (licos-fetch)\e[36m           ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mS\e[97m] Shell (stay here)\e[36m                  ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mR\e[97m] Reboot\e[36m                             ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╚══════════════════════════════════════════════╝\e[0m"
echo ""

read -t 5 -n 1 _choice
case "${_choice}" in
  [iI]) /root/licOS/licos-installer ;;
  [wW]) licos-welcome ;;
  [fF]) licos-fetch ;;
  [rR]) sudo reboot ;;
esac
unset _choice

alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
BROOT

echo "licOS v3.0 customization complete."
