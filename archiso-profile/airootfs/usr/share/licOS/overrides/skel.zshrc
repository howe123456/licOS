[[ -o interactive ]] || return 0

# licOS v3.0 - default .zshrc for new users

print -P ""
print -P "%F{cyan}╔══════════════════════════════════════════════╗%f"
print -P "%F{cyan}║  %F{yellow}        Welcome to licOS v3.0!%F{cyan}             ║%f"
print -P "%F{cyan}║  %F{green}     Arch Linux with XFCE Desktop%F{cyan}         ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╠══════════════════════════════════════════════╣%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}launcher%F{white}' to open the main menu%F{cyan}       ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}licos%F{white}' to start the installer%F{cyan}         ║%f"
print -P "%F{cyan}║  %F{white}Type '%F{green}fetch%F{white}' for system info%F{cyan}               ║%f"
print -P "%F{cyan}║                                              ║%f"
print -P "%F{cyan}╚══════════════════════════════════════════════╝%f"
print -P ""

alias launcher='licos-launcher'
alias licos='/root/licOS/licos-installer'
alias fetch='licos-fetch'
alias welcome='licos-welcome'
