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
print -P "%F{cyan}║  %F{yellow}      Welcome to licOS v3.0!%F{cyan}             %F{yellow}╳%F{cyan} ║%f"
print -P "%F{cyan}║  %F{green}    Lightning XFCE Desktop%F{cyan}              %F{yellow}╱%F{cyan} ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╠══════════════════════════════════════════════╣%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}1%F{white}] %F{yellow}⚡ 特色桌面%F{cyan}  (Desktop Showcase)     ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}I%F{white}] Install licOS%F{cyan}                       ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}W%F{white}] Welcome Dashboard%F{cyan}                  ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}F%F{white}] System Info (licos-fetch)%F{cyan}           ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}S%F{white}] Shell (stay here)%F{cyan}                  ║%f"
print -P "%F{cyan}║  %F{white}[%F{yellow}R%F{white}] Reboot%F{cyan}                             ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}Type \`launcher\` to open the main menu%F{cyan}      ║%f"
print -P "%F{cyan}╚══════════════════════════════════════════════╝%f"
print -P ""

# Key handler: wait 5 seconds for a keypress
read -t 5 -k 1 _choice
case "${_choice}" in
  [1])  licos-launcher ;;
  [iI]) /root/licOS/licos-installer ;;
  [wW]) licos-welcome ;;
  [fF]) licos-fetch ;;
  [rR]) sudo reboot ;;
esac
unset _choice

alias launcher='licos-launcher'
alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
