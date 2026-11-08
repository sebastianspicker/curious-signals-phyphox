#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 not found." >&2
    exit 2
  fi
}

require_command git
require_command rg

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "secret-scan.sh must run from a Git worktree." >&2
  exit 2
fi

echo "== Secret scan (tracked and untracked files) =="
secret_patterns=(
  "BEGIN ([A-Z]+ )?PRIVATE KEY"
  "AKIA[0-9A-Z]{16}"
  "ASIA[0-9A-Z]{16}"
  "xox[baprs]-[0-9A-Za-z-]{10,}"
  "gh[pousr]_[0-9A-Za-z]{36}"
  "github_pat_[0-9A-Za-z_]{20,}"
  "glpat-[0-9A-Za-z-]{20,}"
  "sk-ant-[0-9A-Za-z_-]{20,}"
  "sk-(proj-)?[0-9A-Za-z_-]{32,}"
  "AIza[0-9A-Za-z_-]{35}"
  "[rs]k_live_[0-9A-Za-z]{20,}"
  "xapp-[0-9A-Za-z-]{10,}"
  "hooks\\.slack\\.com/services/"
)

matches="$(mktemp "${TMPDIR:-/tmp}/secret-scan.XXXXXX")"
files="$(mktemp "${TMPDIR:-/tmp}/secret-scan.XXXXXX")"
trap 'rm -f "$matches" "$files"' EXIT

git ls-files -z --cached --others --exclude-standard -- . >"$files"
# --text: a match inside a binary file is still reported with its file name.
scan_arguments=(--null --line-number --with-filename --text)
for pattern in "${secret_patterns[@]}"; do
  scan_arguments+=(--regexp "$pattern")
done
scan_batch() {
  local status=0
  rg "${scan_arguments[@]}" -- "$@" >>"$matches" || status=$?
  if ((status > 1)); then
    echo "Secret scanner failed (exit ${status}); scan is incomplete." >&2
    exit 2
  fi
}

batch=()
while IFS= read -r -d '' file; do
  [[ -f "$file" ]] || continue
  batch+=("$file")
  if ((${#batch[@]} >= 128)); then
    scan_batch "${batch[@]}"
    batch=()
  fi
done <"$files"
if ((${#batch[@]})); then
  scan_batch "${batch[@]}"
fi

if [[ -s "$matches" ]]; then
  while IFS= read -r -d '' file && IFS= read -r line; do
    echo "Potential secret match: ${file}:${line%%:*}"
  done <"$matches"
  echo "Secret scan failed. Remove secrets before proceeding." >&2
  exit 1
fi

echo "OK"
