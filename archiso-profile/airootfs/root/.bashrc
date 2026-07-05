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
echo -e "\e[36m║  \e[33m      Welcome to licOS v3.0!\e[36m             \e[33m╳\e[36m ║\e[0m"
echo -e "\e[36m║  \e[32m    Lightning XFCE Desktop\e[36m              \e[33m╱\e[36m ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m╠══════════════════════════════════════════════╣\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33m1\e[97m] \e[33m⚡ 特色桌面\e[36m  (Desktop Showcase)     ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mI\e[97m] Install licOS\e[36m                       ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mW\e[97m] Welcome Dashboard\e[36m                  ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mF\e[97m] System Info (licos-fetch)\e[36m           ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mS\e[97m] Shell (stay here)\e[36m                  ║\e[0m"
echo -e "\e[36m║  \e[97m[\e[33mR\e[97m] Reboot\e[36m                             ║\e[0m"
echo -e "\e[36m║                                              ║\e[0m"
echo -e "\e[36m║  \e[97mType \`launcher\` to open the main menu\e[36m      ║\e[0m"
echo -e "\e[36m╚══════════════════════════════════════════════╝\e[0m"
echo ""

read -t 5 -n 1 _choice
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
