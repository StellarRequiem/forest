#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Forest CUS — Double-click to launch
#
#  macOS: Double-clicking a .command file opens Terminal and runs this script.
#  No installation beyond git clone required.
# ─────────────────────────────────────────────────────────────────────────────

# Move to the project directory (same folder as this script)
FOREST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${FOREST_DIR}"

# ── Terminal formatting ───────────────────────────────────────────────────────
BOLD="\033[1m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"
CYAN="\033[36m"; DIM="\033[2m"; RESET="\033[0m"

clear
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   🌲  Forest CUS                         ║"
echo "  ║       Blue-Team AI Monitoring             ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"

# ── Step 1: Check Ollama ──────────────────────────────────────────────────────
echo -e "${BOLD}  Checking requirements…${RESET}"
echo ""

if ! command -v ollama &>/dev/null; then
    echo -e "${RED}  ✗ Ollama is not installed.${RESET}"
    echo ""
    echo "  Forest CUS uses local AI models via Ollama."
    echo "  Install it from: https://ollama.ai"
    echo ""
    echo -n "  Open Ollama download page? [Y/n] "
    read -r ans
    if [[ "${ans:-Y}" =~ ^[Yy] ]]; then
        open "https://ollama.ai"
    fi
    echo ""
    echo "  After installing Ollama, double-click Forest.command again."
    echo -e "${DIM}  (Press Enter to close)${RESET}"
    read -r
    exit 1
fi
echo -e "${GREEN}  ✓ Ollama found${RESET}"

# ── Step 2: First-run setup ───────────────────────────────────────────────────
if [[ ! -f "${FOREST_DIR}/venv/bin/activate" ]]; then
    echo ""
    echo -e "${YELLOW}  ⚠  First-time setup required (downloads ~4.5 GB of AI models)${RESET}"
    echo -e "     This runs once and takes about 5–10 minutes."
    echo ""
    echo -n "  Run setup now? [Y/n] "
    read -r ans
    if [[ "${ans:-Y}" =~ ^[Yy] ]]; then
        echo ""
        bash "${FOREST_DIR}/setup.sh"
        if [[ $? -ne 0 ]]; then
            echo -e "${RED}  Setup failed. Check the output above for errors.${RESET}"
            echo -e "${DIM}  (Press Enter to close)${RESET}"
            read -r
            exit 1
        fi
    else
        echo "  Setup skipped. Run setup.sh manually when ready."
        echo -e "${DIM}  (Press Enter to close)${RESET}"
        read -r
        exit 0
    fi
fi

# ── Step 3: Activate venv ─────────────────────────────────────────────────────
# shellcheck disable=SC1091
source "${FOREST_DIR}/venv/bin/activate"
echo -e "${GREEN}  ✓ Environment ready${RESET}"

# ── Step 4: Ensure Ollama is running ─────────────────────────────────────────
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${YELLOW}  ⚠  Starting Ollama…${RESET}"
    ollama serve &>/dev/null &
    sleep 3
fi
echo -e "${GREEN}  ✓ Ollama running${RESET}"

# ── Step 5: Start monitoring ──────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  Starting Forest CUS…${RESET}"

# Stop any stale process
VAULT_DIR="${HOME}/ForestVault"
PID_FILE="${VAULT_DIR}/.monitor_pid"
if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo -e "${DIM}  Monitor already running (PID $(cat "${PID_FILE}"))${RESET}"
else
    mkdir -p "${VAULT_DIR}"
    rm -f "${VAULT_DIR}/.paused"
    nohup python3 "${FOREST_DIR}/core/cus_langgraph.py" \
        --continuous 30 --alert \
        > "${VAULT_DIR}/monitor.log" 2>&1 &
    echo "$!" > "${PID_FILE}"
    echo -e "${GREEN}  ✓ Monitoring started (every 30 min, desktop alerts on threats)${RESET}"
fi

# ── Step 6: Open dashboard ────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  Opening dashboard…${RESET}"

# Kill stale Streamlit
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
sleep 1

streamlit run "${FOREST_DIR}/dashboard/app.py" \
    --server.headless true \
    --server.port 8501 \
    --browser.gatherUsageStats false \
    > "${VAULT_DIR}/dashboard.log" 2>&1 &
sleep 3

open "http://localhost:8501"
echo -e "${GREEN}  ✓ Dashboard at http://localhost:8501${RESET}"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}  🌲 Forest CUS is running!${RESET}"
echo ""
echo -e "  ${BOLD}Dashboard:${RESET}   http://localhost:8501"
echo -e "  ${BOLD}Monitor log:${RESET} ${VAULT_DIR}/monitor.log"
echo ""
echo -e "${DIM}  Quick commands (in a new Terminal window):${RESET}"
echo "    forest pause     — pause monitoring"
echo "    forest stop      — stop completely"
echo "    forest status    — check what's running"
echo ""
echo -e "${DIM}  Close this window at any time — monitoring continues in the background.${RESET}"
echo ""
