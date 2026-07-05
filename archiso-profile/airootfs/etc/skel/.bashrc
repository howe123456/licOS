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
