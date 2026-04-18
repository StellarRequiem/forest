#!/bin/bash
# 📊 M4 MAC MINI AI TOOLS MEMORY MONITOR
# Prevents thermal throttling by watching memory pressure

set -e

THRESHOLD=1500        # MB minimum free
CRITICAL=800          # MB - emergency stop threshold
CHECK_INTERVAL=10     # seconds
LOG_FILE="$HOME/.ai_monitor.log"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_memory_stats() {
    vm_stat | grep -E "Pages free:|Pages active:|Pages wired"
}

check_memory() {
    free_mb=$(vm_stat | grep "Pages free" | awk '{print int($3 * 16 / 1024)}')
    echo $free_mb
}

get_status_color() {
    local mb=$1
    if [ $mb -lt $CRITICAL ]; then
        echo $RED
    elif [ $mb -lt $THRESHOLD ]; then
        echo $YELLOW
    else
        echo $GREEN
    fi
}

get_ai_process_count() {
    ps aux | grep -E "ollama|aider|Continue" | grep -v grep | wc -l
}

emergency_stop() {
    log "🚨 EMERGENCY STOP: Memory critical (${1}MB free)"
    
    echo -e "${RED}"
    echo "🚨 EMERGENCY MEMORY STOP 🚨"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for process in ollama aider "Docker"; do
        if pgrep -f "$process" > /dev/null 2>&1; then
            echo "Killing $process..."
            pkill -f "$process" || true
            sleep 1
        fi
    done
    
    echo "✅ AI tools stopped"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
    
    log "✅ Emergency stop completed"
}

# Startup
clear
echo -e "${BLUE}"
echo "📊 M4 MAC MINI AI TOOLS MEMORY MONITOR"
echo "======================================"
echo -e "${NC}"
echo ""
echo "Settings:"
echo "  • Check interval: ${CHECK_INTERVAL}s"
echo "  • Warn threshold: ${THRESHOLD}MB free"
echo "  • Emergency stop: ${CRITICAL}MB free"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log "🟢 Monitor started"

iteration=0
while true; do
    iteration=$((iteration + 1))
    free_mb=$(check_memory)
    color=$(get_status_color $free_mb)
    processes=$(get_ai_process_count)
    
    # Format output
    clear
    echo -e "${BLUE}📊 AI TOOLS MEMORY MONITOR (Iteration $iteration)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Memory status
    echo -e "${color}Free Memory: ${free_mb}MB${NC}"
    
    if [ $free_mb -ge $THRESHOLD ]; then
        echo -e "${GREEN}✅ Healthy${NC}"
    elif [ $free_mb -ge $CRITICAL ]; then
        echo -e "${YELLOW}⚠️  Warning${NC}"
    else
        echo -e "${RED}🚨 Critical${NC}"
    fi
    
    echo ""
    echo "Thresholds:"
    echo -e "  Healthy:  > ${THRESHOLD}MB ${GREEN}✅${NC}"
    echo -e "  Warning:  $((CRITICAL))-${THRESHOLD}MB ${YELLOW}⚠️${NC}"
    echo -e "  Critical: < ${CRITICAL}MB ${RED}🚨${NC}"
    
    echo ""
    echo "AI Processes: $processes"
    
    echo ""
    echo "Detailed Memory:"
    get_memory_stats | sed 's/^/  /'
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Next check in ${CHECK_INTERVAL}s... (Ctrl+C to stop)"
    
    # Emergency check
    if [ $free_mb -lt $CRITICAL ]; then
        emergency_stop $free_mb
        exit 1
    fi
    
    # Warning check
    if [ $free_mb -lt $THRESHOLD ]; then
        if [ $((iteration % 3)) -eq 0 ]; then  # Log every 3rd check
            log "⚠️  Memory warning: ${free_mb}MB free"
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
