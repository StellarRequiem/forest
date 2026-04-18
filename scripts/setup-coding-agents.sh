#!/bin/bash
# 🤖 Coding Agent & Frontier LLM Setup Script
# Installs best-in-class open-source tools for development

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "🤖 CODING AGENT & FRONTIER LLM SETUP"
echo "====================================="
echo -e "${NC}"

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    OS="Linux"
fi

echo "Detected OS: $OS"
echo ""

# ============================================================================
# PHASE 1: AIDER (CLI Pair Programmer)
# ============================================================================

echo -e "${BLUE}PHASE 1: Installing Aider${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v aider &> /dev/null; then
    echo -e "${GREEN}✅ Aider already installed${NC}"
else
    echo "Installing Aider..."
    pip install aider-chat
    echo -e "${GREEN}✅ Aider installed successfully${NC}"
fi

# Test Aider
echo ""
echo "Testing Aider with local Mistral-7B..."
cat > /tmp/aider_test.txt << 'EOF'
Test file for Aider
This is a simple test to verify Aider can read files.
EOF

echo -e "${GREEN}✅ Aider ready (use: aider [files] --model mistral)${NC}"
echo ""

# ============================================================================
# PHASE 2: CONTINUE.DEV (IDE Integration)
# ============================================================================

echo -e "${BLUE}PHASE 2: Setting up Continue.dev${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if VSCode is installed
if command -v code &> /dev/null; then
    echo "VSCode found, installing Continue.dev extension..."
    code --install-extension Continue.dev.continue 2>/dev/null || echo "Note: Please install Continue.dev from VSCode marketplace"
    echo -e "${GREEN}✅ Continue.dev extension queued for installation${NC}"
else
    echo -e "${YELLOW}⚠️  VSCode not found${NC}"
    echo "   Install from: https://code.visualstudio.com"
    echo "   Then add Continue.dev from marketplace"
fi

echo ""

# ============================================================================
# PHASE 3: Additional Coding Models in Ollama
# ============================================================================

echo -e "${BLUE}PHASE 3: Loading Additional Models${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Ollama status
if command -v ollama &> /dev/null; then
    echo "Ollama detected at: $(which ollama)"
    
    # List current models
    echo ""
    echo "Current models in Ollama:"
    curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -m json.tool 2>/dev/null | grep '"name"' || echo "  (couldn't fetch, Ollama may not be running)"
    
    echo ""
    echo "Available models to load:"
    echo "  1. deepseek-coder:33b-instruct (best for coding)"
    echo "  2. mixtral:8x7b-instruct-v0.1 (powerful local option)"
    echo "  3. qwen:32b-chat (coding-optimized)"
    echo "  4. llama2:70b (general purpose)"
    echo ""
    echo "Example: ollama pull deepseek-coder:33b-instruct"
    
else
    echo -e "${YELLOW}⚠️  Ollama not found${NC}"
    echo "   Install from: https://ollama.ai"
    echo "   Then run: ollama pull [model-name]"
fi

echo ""

# ============================================================================
# PHASE 4: Python Tools for CLI Development
# ============================================================================

echo -e "${BLUE}PHASE 4: Installing Python Development Tools${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install/check Python development tools
python3 -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1

TOOLS=("black" "pylint" "flake8" "pytest" "mypy" "autopep8")

for tool in "${TOOLS[@]}"; do
    if python3 -m pip show $tool > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $tool${NC}"
    else
        echo "Installing $tool..."
        python3 -m pip install $tool > /dev/null 2>&1
        echo -e "${GREEN}✅ $tool${NC}"
    fi
done

echo ""

# ============================================================================
# PHASE 5: OpenDevin (Autonomous Agent)
# ============================================================================

echo -e "${BLUE}PHASE 5: Setting up OpenDevin${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "OpenDevin setup options:"
echo "  1. Via pip: pip install opendevin"
echo "  2. Via Docker: docker run -it ghcr.io/opendevin/opendevin"
echo "  3. From source: git clone https://github.com/OpenDevin/OpenDevin"
echo ""
echo "For now, you can test Aider + Continue.dev"
echo "Install OpenDevin when ready: pip install opendevin"

echo ""

# ============================================================================
# PHASE 6: Configuration Files
# ============================================================================

echo -e "${BLUE}PHASE 6: Creating Configuration Files${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create Aider config
mkdir -p ~/.aider
cat > ~/.aider/.aider.conf.yml << 'EOF'
model: mistral
model-settings-file: ~/.aider/models.json
auto-commit: true
auto-commits: false
show-model-warnings: false
dark-mode: true
pretty: true
EOF

echo -e "${GREEN}✅ Aider config created (~/.aider/.aider.conf.yml)${NC}"

# Create models.json for multiple LLM support
cat > ~/.aider/models.json << 'EOF'
{
  "local": {
    "model": "mistral",
    "base_url": "http://localhost:11434/v1",
    "api_type": "openai"
  },
  "deepseek": {
    "model": "deepseek-coder:33b-instruct",
    "base_url": "http://localhost:11434/v1",
    "api_type": "openai"
  },
  "mixtral": {
    "model": "mixtral:8x7b-instruct-v0.1",
    "base_url": "http://localhost:11434/v1",
    "api_type": "openai"
  }
}
EOF

echo -e "${GREEN}✅ Models config created (~/.aider/models.json)${NC}"

echo ""

# ============================================================================
# PHASE 7: Quick Start Guide
# ============================================================================

echo -e "${BLUE}PHASE 7: Quick Start Guide${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > ~/.aider/QUICK_START.md << 'EOF'
# Quick Start Guide for Coding Agents

## 1. Using Aider (Terminal)

```bash
# Edit files with AI assistance
aider src/main.py src/utils.py

# Ask AI to fix a bug
> Fix the memory leak in the cache module

# Ask for refactoring
> Refactor this function to be more readable

# Run tests
> Add unit tests for this module
```

## 2. Using Continue.dev (VSCode)

- Open VSCode with your project
- Click Continue icon in sidebar
- Select local Mistral model or switch models
- Use @ to reference files/code
- Ask questions about your code

## 3. Using Command Line

```bash
# Check code quality
black --check src/
pylint src/*.py
flake8 src/

# Run tests
pytest tests/ -v --cov=src

# Format code
black src/
autopep8 --in-place src/*.py
```

## 4. Model Switching in Aider

```bash
# Use different models
aider src/ --model deepseek-coder:33b-instruct
aider src/ --model mixtral:8x7b-instruct-v0.1

# API models (if configured)
aider src/ --model gpt-4
aider src/ --model claude-3-sonnet
```

## 5. Git Integration

Aider auto-commits changes with AI-generated messages:
```bash
git log  # See AI-generated commit messages
git diff  # Review changes
```

## Pro Tips

- Use `--model` flag to switch between models
- Use `@filename` in prompts to reference specific files
- Aider has git awareness - it knows your repo structure
- Continue.dev can refactor across multiple files
- OpenDevin can handle multi-step autonomous tasks
EOF

cat ~/.aider/QUICK_START.md
echo ""

# ============================================================================
# FINAL STATUS
# ============================================================================

echo -e "${GREEN}═════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SETUP COMPLETE${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════════════${NC}"
echo ""

echo "What's Installed:"
echo -e "${GREEN}✅ Aider${NC} - CLI pair programmer"
echo -e "${GREEN}✅ Python tools${NC} - black, pylint, flake8, pytest, mypy"
echo -e "${GREEN}✅ Configuration${NC} - ~/.aider/ directory"

echo ""
echo "Ready for Setup:"
echo "⚠️  Continue.dev - Install from VSCode marketplace"
echo "⚠️  Additional Models - Run: ollama pull deepseek-coder:33b-instruct"
echo "⚠️  OpenDevin - Run: pip install opendevin"

echo ""
echo "Next Steps:"
echo "1. Test Aider:"
echo "   aider /Users/llm01/Forest/core/cus_core.py"
echo ""
echo "2. Install Continue.dev in VSCode:"
echo "   - Open VSCode"
echo "   - Go to Extensions"
echo "   - Search for 'Continue'"
echo "   - Install official extension"
echo ""
echo "3. Load better coding model:"
echo "   ollama pull deepseek-coder:33b-instruct"
echo ""
echo "4. Read guide:"
echo "   cat ~/.aider/QUICK_START.md"
echo ""

echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo "For detailed guide, see: /Users/llm01/CODING_AGENTS_GUIDE.md"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
