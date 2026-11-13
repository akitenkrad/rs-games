#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: scripts/record-demos.sh [key ...]" >&2
}

script_path=${BASH_SOURCE[0]}
script_parent=${script_path%/*}
script_dir=$(CDPATH= cd -- "$script_parent" && pwd)
root_dir=${script_dir%/*}
cd -- "$root_dir"

keys=()
if (( $# == 0 )); then
  shopt -s nullglob
  tapes=(demos/*.tape)
  shopt -u nullglob
  for tape in "${tapes[@]}"; do
    key=${tape##*/}
    keys+=("${key%.tape}")
  done
else
  keys=("$@")
fi

for key in "${keys[@]}"; do
  if [[ ! $key =~ ^rs-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    usage
    echo "invalid key: $key (expected rs-prefixed kebab-case)" >&2
    exit 2
  fi
  if [[ ! -f demos/$key.tape ]]; then
    echo "demo tape not found: demos/$key.tape" >&2
    exit 1
  fi
done

if ! command -v vhs >/dev/null 2>&1; then
  echo "vhs is required but was not found on PATH" >&2
  exit 1
fi

mkdir -p docs/assets/games
for key in "${keys[@]}"; do
  printf 'Building %s in release mode...\n' "$key"
  cargo build --release --locked --manifest-path "games/$key/Cargo.toml"
  printf 'Recording demos/%s.tape...\n' "$key"
  vhs "demos/$key.tape"
done

python3 scripts/gen_catalog.py
