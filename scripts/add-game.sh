#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
  echo "usage: scripts/add-game.sh <key> [url]" >&2
  exit 2
fi

key=$1
if [[ ! $key =~ ^rs-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "invalid key: $key (expected rs-prefixed kebab-case)" >&2
  exit 2
fi

url=${2:-"https://github.com/akitenkrad/${key}.git"}
script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root_dir=$(dirname -- "$script_dir")
cd -- "$root_dir"

game_path="games/$key"
if [[ -e $game_path || -L $game_path ]]; then
  printf '%s already exists; skipping git submodule add.\n' "$game_path"
else
  git submodule add "$url" "$game_path"
fi

python3 - "$key" <<'PY'
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

key = sys.argv[1]
path = Path("games.toml")
with path.open("rb") as handle:
    document = tomllib.load(handle)

games = document.get("games", [])
if not any(isinstance(game, dict) and game.get("key") == key for game in games):
    needs_separator = path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        if needs_separator:
            handle.write("\n")
        handle.write(
            "[[games]]\n"
            f'key = "{key}"\n'
            'title = "TODO"\n'
            'title_ja = "TODO"\n'
            'summary = "TODO"\n'
            'summary_ja = "TODO"\n'
            "tags = []\n"
        )
PY

python3 scripts/gen_catalog.py
printf 'Fill in the TODO fields in games.toml, re-run python3 scripts/gen_catalog.py, then commit.\n'
