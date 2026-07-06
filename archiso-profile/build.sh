#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR"
WORK_DIR="$PROFILE_DIR/work"
OUT_DIR="$PROFILE_DIR/out"
PACMAN_CONF="$PROFILE_DIR/pacman.conf"
PACKAGES_FILE="$PROFILE_DIR/packages.x86_64"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${CYAN}  licOS ISO Builder                          ${NC}"
echo -e "${CYAN}  Profile: $PROFILE_DIR${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"

# ── Step 0: Start local nginx cache proxy ─────────────
echo -e "\n${YELLOW}[0/5] Starting local nginx cache proxy...${NC}"
if systemctl is-active --quiet nginx 2>/dev/null; then
  echo -e "  ${GREEN}nginx already running (cache proxy active)${NC}"
else
  echo "  Starting nginx..."
  sudo systemctl start nginx || {
    echo -e "  ${YELLOW}nginx not available — fallback to direct download${NC}"
  }
fi

# Verify proxy is reachable
if curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1; then
  echo -e "  ${GREEN}Local cache proxy: http://127.0.0.1:8080/archlinux/ ${NC}"
else
  echo -e "  ${YELLOW}Local cache proxy unreachable — will use USTC mirror directly${NC}"
fi
echo ""

# ── Step 1: Pre-download packages to host cache ────────
echo -e "\n${YELLOW}[1/5] Pre-downloading packages to host cache...${NC}"
if [[ -f "$PACKAGES_FILE" ]]; then
  PACKAGES=$(grep -v '^#' "$PACKAGES_FILE" | tr '\n' ' ')
  TOTAL_PKGS=$(echo "$PACKAGES" | wc -w)
  echo -e "  Packages to fetch: $TOTAL_PKGS"

  # Check how many are already cached
  CACHED=0
  for pkg in $PACKAGES; do
    if ls /var/cache/pacman/pkg/$pkg-*.pkg.tar.* &>/dev/null 2>&1; then
      ((CACHED++)) || true
    fi
  done
  echo -e "  Already cached: $CACHED / $TOTAL_PKGS"

  if [[ $CACHED -lt $TOTAL_PKGS ]]; then
    echo "  Downloading missing packages..."
    # pacman -Syw downloads to host cache (--cachedir)
    # Host's /etc/pacman.conf now uses local proxy as primary server
    sudo pacman -Syw --noconfirm --cachedir /var/cache/pacman/pkg/ $PACKAGES 2>&1 | \
      grep -E '(downloading| Packages|already up to date|warning:|error:)' || true
  else
    echo -e "  ${GREEN}All packages already cached — skipping download${NC}"
  fi
else
  echo -e "  ${YELLOW}No packages.x86_64 found, skipping pre-download.${NC}"
fi

# ── Step 2: Check and cleanup stale mounts ──────────────
echo -e "\n${YELLOW}[2/5] Checking for stale mounts...${NC}"
if mountpoint -q "$WORK_DIR/airootfs/dev" 2>/dev/null; then
  echo "  Cleaning stale chroot mounts..."
  sudo umount -R "$WORK_DIR/airootfs" 2>/dev/null || true
fi

# Only remove work/ if it has incompatible data (e.g. old archiso version)
# Otherwise keep it for incremental rebuild — saves ~80% time
if [[ -d "$WORK_DIR" ]]; then
  echo -e "  ${GREEN}work/ preserved — incremental rebuild${NC}"
else
  echo "  work/ will be created fresh"
fi

# ── Step 3: Run mkarchiso ──────────────────────────────
echo -e "\n${YELLOW}[3/5] Running mkarchiso...${NC}"
echo -e "  ${GREEN}work/  → preserved (incremental rebuild)${NC}"
echo -e "  ${GREEN}out/   → ISO output${NC}"
echo ""

START_TIME=$(date +%s)
sudo mkarchiso -v "$PROFILE_DIR"
BUILD_DURATION=$(( $(date +%s) - START_TIME ))

# ── Step 4: Show result ────────────────────────────────
echo -e "\n${YELLOW}[4/5] Build complete${NC}"
echo -e "  ${GREEN}Duration: ${BUILD_DURATION}s ($(( BUILD_DURATION / 60 ))m $(( BUILD_DURATION % 60 ))s)${NC}"

ISO_FILE=$(ls -t "$OUT_DIR"/*.iso 2>/dev/null | head -1)
if [[ -n "$ISO_FILE" ]]; then
  ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
  echo -e "  ${GREEN}ISO: $ISO_FILE${NC}"
  echo -e "  ${GREEN}Size: $ISO_SIZE${NC}"
else
  echo -e "  ${YELLOW}No ISO found in $OUT_DIR/${NC}"
fi

# ── Step 5: Show cache stats ────────────────────────────
echo -e "\n${YELLOW}[5/5] Cache stats${NC}"
if [[ -d /var/cache/nginx/archlinux ]]; then
  CACHE_SIZE=$(du -sh /var/cache/nginx/archlinux 2>/dev/null | cut -f1)
  HOST_CACHE=$(du -sh /var/cache/pacman/pkg/ 2>/dev/null | cut -f1)
  echo -e "  ${GREEN}nginx proxy cache: $CACHE_SIZE${NC}"
  echo -e "  ${GREEN}Host pacman cache:  $HOST_CACHE${NC}"
fi

echo -e "\n${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Done!                                       ${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
