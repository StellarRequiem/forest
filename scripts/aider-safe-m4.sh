#!/bin/bash
# 🔧 M4 MAC MINI SAFE AIDER LAUNCHER
# Monitors memory and prevents thermal issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MEMORY_THRESHOLD=1500  # MB - minimum free memory required
MEMORY_WARN=2500       # MB - warning threshold

check_memory() {
    free_mb=$(vm_stat | grep "Pages free" | awk '{print int($3 * 16 / 1024)}')
    echo $free_mb
}

get_color() {
    local mb=$1
    if [ $mb -lt $MEMORY_THRESHOLD ]; then
        echo $RED
    elif [ $mb -lt $MEMORY_WARN ]; then
        echo $YELLOW
    else
        echo $GREEN
    fi
}

echo -e "${BLUE}"
echo "🔧 M4 MAC MINI SAFE AIDER LAUNCHER"
echo "==================================="
echo -e "${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama not running${NC}"
    echo "   Start with: docker start ollama-container"
    exit 1
fi

echo -e "${GREEN}✅ Ollama responding${NC}"

# Check memory
free_mb=$(check_memory)
color=$(get_color $free_mb)

echo -e "${color}Free memory: ${free_mb}MB${NC}"

if [ $free_mb -lt $MEMORY_THRESHOLD ]; then
    echo -e "${RED}❌ INSUFFICIENT MEMORY${NC}"
    echo "   Need: ${MEMORY_THRESHOLD}MB free"
    echo "   Have: ${free_mb}MB"
    echo ""
    echo "   Try:"
    echo "   - Close unnecessary apps"
    echo "   - Kill Discord/Chrome"
    echo "   - Restart: killall Finder; killall Dock"
    exit 1
elif [ $free_mb -lt $MEMORY_WARN ]; then
    echo -e "${YELLOW}⚠️  WARNING: Memory is tight${NC}"
    echo "   Recommended: > ${MEMORY_WARN}MB"
    echo "   Proceeding with caution..."
    sleep 3
fi

# Check if Docker image exists
if ! docker image inspect paulgauthier/aider:latest > /dev/null 2>&1; then
    echo -e "${YELLOW}Aider image not found, pulling...${NC}"
    docker pull paulgauthier/aider:latest
fi

# Build command
FILES="${@:-.}"  # Use current dir if no args

echo ""
echo -e "${BLUE}Starting Aider with:${NC}"
echo "  Model: mistral"
echo "  Files: $FILES"
echo "  Memory limit: Monitored (${MEMORY_THRESHOLD}MB minimum)"
echo ""
echo "⚠️  TIPS FOR M4:"
echo "  • Keep sessions < 60 minutes"
echo "  • Use focused, small files"
echo "  • If fan ramps up, quit immediately"
echo ""

# Start Aider with safe options
docker run -it \
  --memory="4g" \
  --memory-reservation="2g" \
  -v "$(pwd):/workspace" \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  paulgauthier/aider:latest \
  --model ollama/mistral \
  --no-stream \
  --no-auto-commits \
  --chat-history-file /dev/null \
  $FILES

echo ""
echo -e "${GREEN}✅ Aider session ended${NC}"

# Check memory after
free_mb_after=$(check_memory)
echo -e "Memory after: ${free_mb_after}MB"

if [ $free_mb_after -lt 2000 ]; then
    echo -e "${YELLOW}⚠️  Consider restarting Ollama to free memory${NC}"
fi
