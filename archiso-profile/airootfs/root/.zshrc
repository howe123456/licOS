[[ -o interactive ]] || return 0

clear

# Lightning bolt animation (plays once before welcome banner)
_licos_anim() {
  local cols="${COLUMNS:-80}" lx=$(( cols - 8 ))
  printf '\e[?25l'
  printf "\e[2;${lx}H     \e[3;${lx}H     \e[4;${lx}H     "; sleep 0.08
  printf "\e[2;${lx}H\e[2m  ·  \e[3;${lx}H\e[2m ··· \e[4;${lx}H\e[2m  ·  \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m ╲   \e[3;${lx}H\e[33m  ╲  \e[4;${lx}H\e[33m   ╱ \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m ╲   \e[3;${lx}H\e[33m  ╳  \e[4;${lx}H\e[33m ╱   \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[1;37m ═══ \e[3;${lx}H\e[1;37m ═╬═ \e[4;${lx}H\e[1;37m ═══ \e[0m"; sleep 0.08
  printf "\e[2;${lx}H\e[33m ╲   \e[3;${lx}H\e[33m  ╳  \e[4;${lx}H\e[33m ╱   \e[0m"
  printf '\e[?25h'
}
_licos_anim
unset -f _licos_anim

print -P ""
print -P "%F{cyan}╔══════════════════════════════════════════════╗%f"
print -P "%F{cyan}║                                            %F{yellow}╲%F{cyan} ║%f"
print -P "%F{cyan}║  %F{yellow}        Welcome to licOS Linux%F{cyan}           %F{yellow}╳%F{cyan} ║%f"
print -P "%F{cyan}║  %F{green}     Arch Linux-based distribution%F{cyan}      %F{yellow}╱%F{cyan} ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╠══════════════════════════════════════════════╣%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}licos%F{white}' to start the installer%F{cyan}         ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}help%F{white}'  for available commands%F{cyan}         ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╚══════════════════════════════════════════════╝%f"
print -P ""

alias licos='/root/licOS/licos-installer'
