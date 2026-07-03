if [ -z "$PS1" ]; then
    return
fi

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

echo -e "\e[36m╔══════════════════════════════════════════════╗\e[0m"
echo -e "\e[36m║                                            \e[33m╲\e[36m ║\e[0m"
echo -e "\e[36m║  \e[33m        Welcome to licOS Linux\e[36m           \e[33m╳\e[36m ║\e[0m"
echo -e "\e[36m║  \e[32m     Arch Linux-based distribution\e[36m      \e[33m╱\e[36m ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╠══════════════════════════════════════════════╣\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m║  \e[97mType '\e[32mlicos\e[97m' to start the installer\e[36m         ║\e[0m"
echo -e "\e[36m║  \e[97mType '\e[32mhelp\e[97m'  for available commands\e[36m         ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╚══════════════════════════════════════════════╝\e[0m"
echo ""

alias licos='/root/licOS/licos-installer'
