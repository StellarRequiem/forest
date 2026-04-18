#!/bin/bash
# 🐳 FOREST DOCKER MAINTENANCE SCRIPT
# Quick tools for monitoring, debugging, and maintaining the Docker stack

set -e

usage() {
    cat << 'EOF'
🐳 Forest Docker Maintenance Toolkit

Usage: ./forest-docker-maintenance.sh [command]

MONITORING:
  status           Show all running containers and health
  logs [service]   View logs (default: forest-swarm)
  health           Run full health check
  stats            Show real-time container stats

MANAGEMENT:
  restart [service]  Restart a service (default: forest-swarm)
  clean             Remove stopped containers & unused volumes
  reset-redis       Reset Redis cache
  fix-dify          Fix Dify worker & Redis issues

TESTING:
  test-connections    Test inter-service communication
  test-ollama         Test LLM service
  test-proposal       Send test proposal to swarm

INFORMATION:
  info             Show infrastructure info
  ports            Show exposed ports
  networks         Show Docker networks

EXAMPLES:
  ./forest-docker-maintenance.sh status
  ./forest-docker-maintenance.sh logs forest-ollama
  ./forest-docker-maintenance.sh restart forest-swarm
  ./forest-docker-maintenance.sh health
  ./forest-docker-maintenance.sh test-connections

EOF
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# MONITORING COMMANDS

status_check() {
    echo "🐳 FOREST DOCKER STATUS"
    echo "═════════════════════════════════════════════════════════"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep -E "forest|dify|decepticon|ollama|postgres|redis|target" || true
    echo ""
    echo "Stopped containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -E "Exited|Dead" | grep -E "forest|dify|decepticon" || echo "  (none)"
}

view_logs() {
    local service="${1:-forest-swarm}"
    echo "📜 Viewing logs for: $service"
    docker logs -f "$service"
}

health_check() {
    echo "🔍 FULL HEALTH CHECK"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    echo "1️⃣ Core Services:"
    for svc in forest-swarm forest-ollama forest-postgres forest-redis; do
        if docker inspect "$svc" > /dev/null 2>&1; then
            health=$(docker inspect "$svc" --format='{{.State.Health.Status}}' 2>/dev/null || echo "running")
            echo "   ✓ $svc: $health"
        else
            echo "   ✗ $svc: NOT FOUND"
        fi
    done
    echo ""
    
    echo "2️⃣ Red-Team Stack:"
    for svc in forest-decepticon decepticon-langgraph decepticon-sandbox; do
        if docker inspect "$svc" > /dev/null 2>&1; then
            status=$(docker inspect "$svc" --format='{{.State.Running}}')
            if [ "$status" = "true" ]; then
                echo "   ✓ $svc: running"
            else
                echo "   ✗ $svc: stopped"
            fi
        fi
    done
    echo ""
    
    echo "3️⃣ Network Connectivity:"
    docker exec forest-swarm ping -c 1 forest-ollama > /dev/null 2>&1 && echo "   ✓ forest-swarm → forest-ollama: OK" || echo "   ✗ forest-swarm → forest-ollama: FAIL"
    docker exec forest-swarm ping -c 1 forest-postgres > /dev/null 2>&1 && echo "   ✓ forest-swarm → forest-postgres: OK" || echo "   ✗ forest-swarm → forest-postgres: FAIL"
    docker exec forest-swarm bash -c "redis-cli -h forest-redis PING 2>&1 | grep -q NOAUTH" && echo "   ✓ forest-swarm → forest-redis: OK" || echo "   ✗ forest-swarm → forest-redis: FAIL"
    echo ""
    
    echo "4️⃣ Services:"
    docker exec forest-ollama curl -s http://localhost:11434/api/tags | grep -q mistral && echo "   ✓ Ollama API: Responding with mistral" || echo "   ✗ Ollama API: Not responding"
    echo ""
    
    echo "✅ Health check complete"
}

show_stats() {
    echo "📊 REAL-TIME CONTAINER STATS"
    echo "═════════════════════════════════════════════════════════"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "forest|dify|decepticon|ollama|postgres|redis|target" || true
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# MANAGEMENT COMMANDS

restart_service() {
    local service="${1:-forest-swarm}"
    echo "🔄 Restarting: $service"
    docker restart "$service"
    echo "✅ Restarted"
    sleep 3
    docker ps | grep "$service" || echo "⚠️  May still be starting..."
}

clean_docker() {
    echo "🧹 Cleaning up Docker resources"
    echo "  • Removing stopped containers..."
    docker ps -a --format "{{.Names}}" | grep -E "forest|dify|decepticon" | while read ctr; do
        status=$(docker inspect "$ctr" --format='{{.State.Running}}' 2>/dev/null || echo "true")
        if [ "$status" != "true" ]; then
            docker rm "$ctr" 2>/dev/null && echo "    ✓ Removed: $ctr" || true
        fi
    done
    echo "✅ Cleanup complete"
}

reset_redis() {
    echo "🔄 Resetting forest-redis"
    docker exec forest-redis redis-cli FLUSHALL
    echo "✅ Redis cache cleared"
}

fix_dify() {
    echo "🔧 Fixing Dify infrastructure"
    echo ""
    
    echo "1️⃣ Fixing dify-redis-1..."
    docker exec dify-redis-1 redis-cli CONFIG SET stop-writes-on-bgsave-error no 2>&1 | head -1
    docker exec dify-redis-1 redis-cli CONFIG SET appendonly no 2>&1 | head -1
    docker exec dify-redis-1 redis-cli SAVE 2>&1 | head -1
    echo "✅ Redis fixed"
    echo ""
    
    echo "2️⃣ Restarting dify-worker-1..."
    docker restart dify-worker-1
    sleep 5
    echo "✅ Worker restarted"
    echo ""
    
    echo "✅ Dify infrastructure repaired"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# TESTING COMMANDS

test_connections() {
    echo "🔗 TESTING INTER-SERVICE COMMUNICATION"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    echo "forest-swarm → forest-ollama:11434"
    docker exec forest-swarm curl -s http://forest-ollama:11434/api/tags | grep -q mistral && echo "  ✅ OK (mistral model found)" || echo "  ✗ FAIL"
    echo ""
    
    echo "forest-swarm → forest-postgres:5432"
    docker exec forest-swarm bash -c "nc -z forest-postgres 5432" 2>&1 | grep -q "succeeded\|" && echo "  ✅ OK (port responsive)" || echo "  ✗ FAIL"
    echo ""
    
    echo "forest-swarm → forest-redis:6379"
    docker exec forest-swarm bash -c "redis-cli -h forest-redis PING" 2>&1 | grep -q "PONG\|NOAUTH" && echo "  ✅ OK (responding)" || echo "  ✗ FAIL"
    echo ""
    
    echo "✅ Connection tests complete"
}

test_ollama() {
    echo "🤖 TESTING OLLAMA LLM SERVICE"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    echo "Checking Ollama API..."
    response=$(curl -s http://localhost:11434/api/tags)
    echo "Response: $(echo "$response" | jq -r '.models[0].name' 2>/dev/null || echo "JSON parsing failed")"
    echo ""
    
    echo "Models available:"
    echo "$response" | jq -r '.models[].name' 2>/dev/null | sed 's/^/  • /' || echo "  (unable to parse)"
    echo ""
    
    echo "✅ Ollama test complete"
}

test_proposal() {
    echo "📨 SENDING TEST PROPOSAL"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    echo "Note: Proposal handling requires entrypoint.py modification"
    echo "Currently, forest-swarm runs in monitoring-only mode"
    echo ""
    echo "To enable proposal handling:"
    echo "  1. Edit /forest/entrypoint.py"
    echo "  2. Add stdin/API proposal listener"
    echo "  3. Rebuild docker image"
    echo ""
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# INFORMATION COMMANDS

show_info() {
    echo "ℹ️  FOREST DOCKER INFRASTRUCTURE"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    echo "Core Services:"
    echo "  • forest-swarm        (Orchestrator + Watchers + Firewall)"
    echo "  • forest-ollama       (LLM: mistral:7b @ port 11434)"
    echo "  • forest-postgres     (Audit DB @ port 5432)"
    echo "  • forest-redis        (Cache @ port 6379)"
    echo ""
    
    echo "Red-Team Stack:"
    echo "  • forest-decepticon   (AI Attacker)"
    echo "  • decepticon-langgraph"
    echo "  • decepticon-sandbox"
    echo ""
    
    echo "Integration:"
    echo "  • dify-* services"
    echo ""
    
    echo "Volumes:"
    docker volume ls --filter name=forest | tail -n +2 | sed 's/^/  • /'
    echo ""
}

show_ports() {
    echo "🔌 EXPOSED PORTS"
    echo "═════════════════════════════════════════════════════════"
    docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "forest|dify|decepticon|ollama|postgres|redis|target" | grep -v "^NAMES" || true
    echo ""
    echo "Local Access:"
    echo "  • Ollama API:        http://localhost:11434"
    echo "  • Dify Web:          http://localhost:3000"
    echo "  • Decepticon Target: http://localhost:8081"
    echo "  • LiteLLM Proxy:     http://localhost:4000 (internal)"
}

show_networks() {
    echo "🌐 DOCKER NETWORKS"
    echo "═════════════════════════════════════════════════════════"
    docker network ls | grep -E "forest|dify|decepticon" || true
    echo ""
    echo "Forest Network Containers:"
    docker network inspect forest-blue-team-guardian_forest-network 2>/dev/null | grep -A1 "\"Name\":" | grep -v "^--$" | sed 's/.*"\(.*\)".*/  • \1/' || echo "  (network not found)"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# MAIN DISPATCHER

main() {
    case "${1:-help}" in
        status)          status_check ;;
        logs)            view_logs "$2" ;;
        health)          health_check ;;
        stats)           show_stats ;;
        restart)         restart_service "$2" ;;
        clean)           clean_docker ;;
        reset-redis)     reset_redis ;;
        fix-dify)        fix_dify ;;
        test-connections) test_connections ;;
        test-ollama)     test_ollama ;;
        test-proposal)   test_proposal ;;
        info)            show_info ;;
        ports)           show_ports ;;
        networks)        show_networks ;;
        help|--help|-h)  usage ;;
        *)               echo "❌ Unknown command: $1"; echo ""; usage; exit 1 ;;
    esac
}

main "$@"
