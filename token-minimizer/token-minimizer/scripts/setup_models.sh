#!/usr/bin/env bash
# Pulls the Qwen models used by Token Minimizer.
# Run this after `docker compose up -d` (or after starting `ollama serve` locally).
#
# Usage:
#   ./scripts/setup_models.sh            # pulls the small default (0.5B)
#   ./scripts/setup_models.sh all         # pulls 0.5B, 1.5B and 3B
#   ./scripts/setup_models.sh 1.5b        # pulls just one size

set -e

OLLAMA_CMD="ollama"
if docker ps --format '{{.Names}}' | grep -q token-minimizer-ollama; then
  OLLAMA_CMD="docker exec token-minimizer-ollama ollama"
fi

pull () {
  echo "Pulling $1 ..."
  $OLLAMA_CMD pull "$1"
}

case "$1" in
  all)
    pull qwen2.5:0.5b
    pull qwen2.5:1.5b
    pull qwen2.5:3b
    ;;
  0.5b|"")
    pull qwen2.5:0.5b
    ;;
  1.5b)
    pull qwen2.5:1.5b
    ;;
  3b)
    pull qwen2.5:3b
    ;;
  *)
    echo "Unknown option: $1"
    echo "Usage: $0 [all|0.5b|1.5b|3b]"
    exit 1
    ;;
esac

echo "Done. Models available: $($OLLAMA_CMD list)"
