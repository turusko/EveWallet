#!/usr/bin/env bash
set -euo pipefail

# Raspberry Pi auto-deploy script for EveWallet Docker app.
# Default published port: 8080 -> container port 8000.

REPO_DIR="${REPO_DIR:-$HOME/EveWallet}"
CONTAINER_NAME="${CONTAINER_NAME:-evewallet-app}"
IMAGE_NAME="${IMAGE_NAME:-evewallet:latest}"
HOST_PORT="${HOST_PORT:-8080}"
CONTAINER_PORT="${CONTAINER_PORT:-8000}"
ENV_FILE="${ENV_FILE:-.env}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "ERROR: Required command '$1' is not installed."
    exit 1
  fi
}

require_cmd git
require_cmd docker

if [ ! -d "$REPO_DIR/.git" ]; then
  log "ERROR: '$REPO_DIR' is not a git repository."
  exit 1
fi

cd "$REPO_DIR"

log "Updating current branch with latest remote changes (no branch switch)..."
current_branch="$(git rev-parse --abbrev-ref HEAD)"
git fetch origin "$current_branch"
git pull --ff-only origin "$current_branch"

log "Building Docker image '$IMAGE_NAME'..."
docker build -t "$IMAGE_NAME" .

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  log "Stopping existing container '$CONTAINER_NAME'..."
  docker stop "$CONTAINER_NAME" || true
  log "Removing existing container '$CONTAINER_NAME'..."
  docker rm "$CONTAINER_NAME" || true
fi

DOCKER_RUN_ARGS=(
  -d
  --name "$CONTAINER_NAME"
  --restart unless-stopped
  -p "$HOST_PORT:$CONTAINER_PORT"
)

if [ -f "$ENV_FILE" ]; then
  DOCKER_RUN_ARGS+=(--env-file "$ENV_FILE")
fi

log "Starting container '$CONTAINER_NAME' on port $HOST_PORT..."
docker run "${DOCKER_RUN_ARGS[@]}" "$IMAGE_NAME"

log "Deployment complete. UI should be available at http://<raspberry-pi-ip>:$HOST_PORT and API docs at /docs"
