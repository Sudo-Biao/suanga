#!/usr/bin/env bash
# =============================================================================
# start.sh — 八卦推演 One-click launcher
# =============================================================================
# Usage:
#   ./start.sh          — start both backend + frontend (dev mode)
#   ./start.sh backend  — backend only
#   ./start.sh frontend — frontend only
#   ./start.sh stop     — kill all launched processes
#   ./start.sh install  — install / update all dependencies only
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_PORT=8888
FRONTEND_PORT=5173

BACKEND_PID_FILE="/tmp/bagua_backend.pid"
FRONTEND_PID_FILE="/tmp/bagua_frontend.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

banner() {
  echo -e "${CYAN}"
  echo "  ╔══════════════════════════════════════════════╗"
  echo "  ║          八 卦 推 演  BaGua System           ║"
  echo "  ║  八字 · 六爻 · 奇门遁甲 · 风水 · 择日       ║"
  echo "  ╚══════════════════════════════════════════════╝"
  echo -e "${NC}"
}

log()     { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*"; exit 1; }
info()    { echo -e "${CYAN}[→]${NC} $*"; }

# ─────────────────────────────────────────────
# Dependency check
# ─────────────────────────────────────────────
check_python() {
  if ! command -v python3 &>/dev/null; then
    error "Python 3.10+ is required. Install from https://www.python.org"
  fi
  PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  info "Python $PY_VER detected"
}

check_node() {
  if ! command -v node &>/dev/null; then
    error "Node.js 18+ is required. Install from https://nodejs.org"
  fi
  NODE_VER=$(node --version)
  info "Node $NODE_VER detected"
}

check_npm() {
  if ! command -v npm &>/dev/null; then
    error "npm is required (bundled with Node.js)"
  fi
}

# ─────────────────────────────────────────────
# Install dependencies
# ─────────────────────────────────────────────
install_backend() {
  info "Installing Python dependencies..."
  cd "$BACKEND_DIR"

  # Prefer venv when not already active
  if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    if [[ ! -d ".venv" ]]; then
      python3 -m venv .venv
      log "Created virtual environment at .venv"
    fi
    # shellcheck disable=SC1091
    source .venv/bin/activate
    log "Activated virtual environment"
  else
    log "Using existing virtual environment: $VIRTUAL_ENV"
  fi

  pip install -r requirements.txt -q
  log "Backend dependencies installed"
}

install_frontend() {
  info "Installing Node dependencies..."
  cd "$FRONTEND_DIR"
  npm install --silent
  log "Frontend dependencies installed"
}

install_all() {
  check_python
  check_node
  check_npm
  install_backend
  install_frontend
  log "All dependencies ready"
}

# ─────────────────────────────────────────────
# Environment setup
# ─────────────────────────────────────────────
setup_env() {
  ENV_FILE="$BACKEND_DIR/.env"
  if [[ ! -f "$ENV_FILE" ]]; then
    if [[ -f "$BACKEND_DIR/.env.example" ]]; then
      cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
      warn ".env not found — created from .env.example. Edit $ENV_FILE as needed."
    fi
  fi
}

# ─────────────────────────────────────────────
# Wait for port to open
# ─────────────────────────────────────────────
wait_for_port() {
  local port=$1 label=$2 retries=20
  info "Waiting for $label on :$port ..."
  for ((i=0; i<retries; i++)); do
    if curl -s "http://localhost:$port/health" &>/dev/null || \
       curl -s "http://localhost:$port"        &>/dev/null; then
      log "$label is up → http://localhost:$port"
      return 0
    fi
    sleep 1
  done
  warn "$label did not respond in ${retries}s — check logs"
  return 1
}

# ─────────────────────────────────────────────
# Start backend
# ─────────────────────────────────────────────
start_backend() {
  cd "$BACKEND_DIR"

  # Activate venv if present
  if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi

  # Kill stale process
  if [[ -f "$BACKEND_PID_FILE" ]]; then
    OLD_PID=$(cat "$BACKEND_PID_FILE")
    kill "$OLD_PID" 2>/dev/null && warn "Stopped stale backend (PID $OLD_PID)"
    rm -f "$BACKEND_PID_FILE"
  fi

  info "Starting FastAPI backend on :$BACKEND_PORT ..."
  nohup python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
    --reload \
    --log-level info \
    > /tmp/bagua_backend.log 2>&1 &

  echo $! > "$BACKEND_PID_FILE"
  log "Backend PID: $(cat "$BACKEND_PID_FILE")  |  Logs: /tmp/bagua_backend.log"

  wait_for_port "$BACKEND_PORT" "Backend"
}

# ─────────────────────────────────────────────
# Start frontend
# ─────────────────────────────────────────────
start_frontend() {
  cd "$FRONTEND_DIR"

  if [[ ! -d "node_modules" ]]; then
    warn "node_modules not found — running npm install first..."
    npm install --silent
  fi

  # Kill stale process
  if [[ -f "$FRONTEND_PID_FILE" ]]; then
    OLD_PID=$(cat "$FRONTEND_PID_FILE")
    kill "$OLD_PID" 2>/dev/null && warn "Stopped stale frontend (PID $OLD_PID)"
    rm -f "$FRONTEND_PID_FILE"
  fi

  info "Starting Vite frontend on :$FRONTEND_PORT ..."
  nohup npm run dev -- --host 0.0.0.0 \
    > /tmp/bagua_frontend.log 2>&1 &

  echo $! > "$FRONTEND_PID_FILE"
  log "Frontend PID: $(cat "$FRONTEND_PID_FILE")  |  Logs: /tmp/bagua_frontend.log"

  wait_for_port "$FRONTEND_PORT" "Frontend"
}

# ─────────────────────────────────────────────
# Stop all
# ─────────────────────────────────────────────
stop_all() {
  info "Stopping all bagua processes..."
  for PID_FILE in "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"; do
    if [[ -f "$PID_FILE" ]]; then
      PID=$(cat "$PID_FILE")
      if kill "$PID" 2>/dev/null; then
        log "Killed PID $PID"
      else
        warn "PID $PID not running"
      fi
      rm -f "$PID_FILE"
    fi
  done
  log "Done"
}

# ─────────────────────────────────────────────
# Print status summary
# ─────────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}  Services Running${NC}"
  echo -e "  ${GREEN}●${NC} Backend API  →  http://localhost:${BACKEND_PORT}"
  echo -e "  ${GREEN}●${NC} API Docs     →  http://localhost:${BACKEND_PORT}/docs"
  echo -e "  ${GREEN}●${NC} Frontend     →  http://localhost:${FRONTEND_PORT}"
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "  Press ${YELLOW}Ctrl+C${NC} or run ${CYAN}./start.sh stop${NC} to quit"
  echo ""
}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
banner
MODE="${1:-all}"

case "$MODE" in
  install)
    install_all
    ;;
  backend)
    check_python
    setup_env
    start_backend
    print_summary
    ;;
  frontend)
    check_node
    check_npm
    start_frontend
    print_summary
    ;;
  stop)
    stop_all
    ;;
  all | *)
    check_python
    check_node
    check_npm
    setup_env

    # Install only if missing
    if [[ ! -f ".venv/bin/activate" ]] && [[ -z "${VIRTUAL_ENV:-}" ]]; then
      install_backend
    fi
    if [[ ! -d "frontend/node_modules" ]]; then
      install_frontend
    fi

    start_backend
    start_frontend
    print_summary

    # Keep script alive so Ctrl+C cleans up
    trap stop_all EXIT INT TERM
    info "Running. Logs: /tmp/bagua_backend.log  /tmp/bagua_frontend.log"
    tail -f /tmp/bagua_backend.log /tmp/bagua_frontend.log 2>/dev/null
    ;;
esac
