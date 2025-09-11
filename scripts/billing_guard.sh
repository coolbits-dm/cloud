#!/usr/bin/env bash
set -euo pipefail
MODE="${CB_BILLING_MODE:-dev}"
if [ "$MODE" != "prod" ]; then
  echo "[BILLING-GUARD] mode=$MODE → SKIP cloud steps (soft guard)."
  printf "skip\n" > .billing_guard || true
  exit 0   # nu 42
fi
rm -f .billing_guard || true
exit 0
