#!/usr/bin/env bash
# Forest CUS — one-command installer
# Usage: bash setup.sh
# Tested on: macOS 13+, Ubuntu 22.04+

set -e

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}  ✓${RESET} $*"; }
warn() { echo -e "${YELLOW}  ⚠${RESET} $*"; }
fail() { echo -e "${RED}  ✗${RESET} $*"; exit 1; }
step() { echo -e "\n${BOLD}$*${RESET}"; }

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Forest CUS — Installer v1.0        ║"
echo "  ║   Blue-Team AI Monitoring Swarm       ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${RESET}"

# ── 1. Python version ─────────────────────────────────────────────────────────
step "1/5  Checking Python version"

PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(sys.version_info[:2])")
        if [[ "$ver" > "(3, 9)" ]]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

[[ -z "$PYTHON" ]] && fail "Python 3.10+ required. Install from https://python.org"
ok "Using $PYTHON ($($PYTHON --version))"

# ── 2. Virtual environment ────────────────────────────────────────────────────
step "2/5  Setting up virtual environment"

if [[ ! -d "venv" ]]; then
    $PYTHON -m venv venv
    ok "Created venv/"
else
    ok "venv/ already exists — skipping creation"
fi

# shellcheck disable=SC1091
source venv/bin/activate

pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
ok "Python dependencies installed"

# ── 3. Ollama ─────────────────────────────────────────────────────────────────
step "3/5  Checking Ollama"

if ! command -v ollama &>/dev/null; then
    warn "Ollama not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            brew install --cask ollama
        else
            warn "Homebrew not found. Download Ollama manually from https://ollama.ai"
            warn "Then re-run this script."
            OLLAMA_MISSING=1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        warn "Unknown OS. Download Ollama from https://ollama.ai and re-run."
        OLLAMA_MISSING=1
    fi
fi

if [[ -z "${OLLAMA_MISSING:-}" ]]; then
    ok "Ollama found: $(ollama --version 2>/dev/null || echo 'version unknown')"

    # Start Ollama if not running
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        warn "Ollama is not running. Starting it in the background..."
        ollama serve &>/dev/null &
        sleep 3
    fi

    # Pull required models
    echo ""
    echo "  Pulling models (this downloads ~4.5 GB total on first run):"
    echo "  You can Ctrl-C and resume later — already-pulled models are skipped."
    echo ""

    for model in "qwen2.5:3b" "llama3.2:3b" "nomic-embed-text"; do
        echo -n "  Pulling $model ... "
        if ollama pull "$model" 2>&1 | tail -1 | grep -q "already"; then
            ok "already present"
        else
            ok "done"
        fi
    done
fi

# ── 4. ForestVault directory ──────────────────────────────────────────────────
step "4/5  Initialising ForestVault"

VAULT="${HOME}/ForestVault"
mkdir -p "$VAULT/proposals" "$VAULT/proposals_archive"
ok "ForestVault ready at $VAULT"

# ── 5. .env file ──────────────────────────────────────────────────────────────
step "5/5  Environment config"

if [[ ! -f ".env" ]]; then
    cp .env.example .env
    ok "Created .env from .env.example"
    warn "Optional: add your AbuseIPDB API key to .env for threat intel lookups"
    warn "  Get a free key at https://www.abuseipdb.com"
else
    ok ".env already exists — not overwriting"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}  ✓ Forest CUS is ready!${RESET}"
echo ""
echo "  Quick start:"
echo "    source venv/bin/activate"
echo "    echo \"yes\" | python3 core/cus_langgraph.py"
echo ""
echo "  Dashboard:"
echo "    ./bin/forest-dash    # → http://localhost:8501"
echo ""
echo "  Continuous monitoring (every 30 min):"
echo "    python3 core/cus_langgraph.py --continuous 30 --alert"
echo ""
echo "  Optional: add your AbuseIPDB key to .env for threat intel:"
echo "    echo 'ABUSEIPDB_API_KEY=your_key_here' >> .env"
echo "    source .env"
echo ""
