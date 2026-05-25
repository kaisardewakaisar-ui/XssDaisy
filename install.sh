#!/usr/bin/env bash
# XssDaisy - Installer
# Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock

RED='\033[0;31m'; GREEN='\033[0;32m'; PURPLE='\033[0;35m'; NC='\033[0m'; BOLD='\033[1m'

clear
echo -e "${PURPLE}${BOLD}"
echo " ██╗  ██╗███████╗███████╗██████╗  █████╗ ██╗███████╗██╗   ██╗"
echo " ╚██╗██╔╝██╔════╝██╔════╝██╔══██╗██╔══██╗██║██╔════╝╚██╗ ██╔╝"
echo "  ╚███╔╝ ███████╗███████╗██║  ██║███████║██║███████╗ ╚████╔╝ "
echo "  ██╔██╗ ╚════██║╚════██║██║  ██║██╔══██║██║╚════██║  ╚██╔╝  "
echo " ██╔╝ ██╗███████║███████║██████╔╝██║  ██║██║███████║   ██║   "
echo " ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝  "
echo -e "${NC}${GREEN}  Installer v3.0 | Author: KaisarYetiandi${NC}"
echo -e "${PURPLE}  github.com/KaisarYetiandi | t.me/Darkness_Lock${NC}"
echo ""

ok() { echo -e "${GREEN}[+]${NC} $1"; }
err(){ echo -e "${RED}[!]${NC} $1"; }

# Python deps
ok "Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages -q 2>/dev/null || \
pip3 install -r requirements.txt -q 2>/dev/null || \
{ err "pip install failed — try manually: pip install -r requirements.txt"; }

# katana
if ! command -v katana &>/dev/null; then
    ok "Installing katana..."
    go install github.com/projectdiscovery/katana/cmd/katana@latest 2>/dev/null && ok "katana installed" || err "katana install failed (needs Go)"
else
    ok "katana already installed"
fi

# wafw00f
if ! command -v wafw00f &>/dev/null; then
    ok "Installing wafw00f..."
    pip install wafw00f --break-system-packages -q 2>/dev/null && ok "wafw00f installed" || err "wafw00f install failed"
else
    ok "wafw00f already installed"
fi

echo ""
ok "XssDaisy is ready!"
echo -e "${PURPLE}  Usage: python main.py -u http://target.com/?id=1${NC}"
echo -e "${PURPLE}  Help : python main.py --help${NC}"
