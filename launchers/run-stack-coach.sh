#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${repo_root}"
if [[ "${1:-}" == "--browser" ]]; then
  shift
  PYTHONPATH="${repo_root}/src" exec python3 -m stack_review_coach --browser "$@"
fi

PYTHONPATH="${repo_root}/src" exec python3 -m stack_review_coach "$@"
