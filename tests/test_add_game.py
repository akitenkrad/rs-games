from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ADD_GAME = PROJECT_ROOT / "scripts" / "add-game.sh"
SOURCE_GENERATOR = PROJECT_ROOT / "scripts" / "gen_catalog.py"


class AddGameIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(dir=PROJECT_ROOT)
        self.root = Path(self.temp_dir.name)
        (self.root / "scripts").mkdir()
        if not SOURCE_ADD_GAME.exists() or not SOURCE_GENERATOR.exists():
            self.fail("scripts/add-game.sh and scripts/gen_catalog.py must exist")
        shutil.copy2(SOURCE_ADD_GAME, self.root / "scripts" / "add-game.sh")
        shutil.copy2(SOURCE_GENERATOR, self.root / "scripts" / "gen_catalog.py")
        (self.root / "games.toml").write_text(
            '''
[[games]]
key = "rs-nim"
title = "Nim"
title_ja = "ニム"
summary = "Nim."
summary_ja = "ニム．"
tags = ["strategy"]
'''.lstrip(),
            encoding="utf-8",
        )
        marker = "<!-- BEGIN:games -->\nold\n<!-- END:games -->\n"
        (self.root / "README.md").write_text(marker, encoding="utf-8")
        (self.root / "README.ja.md").write_text(marker, encoding="utf-8")
        (self.root / ".gitmodules").write_text(
            '[submodule "games/rs-nim"]\n'
            "\tpath = games/rs-nim\n"
            "\turl = https://github.com/akitenkrad/rs-nim.git\n",
            encoding="utf-8",
        )
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        fake_git = fake_bin / "git"
        fake_git.write_text(
            '''#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$FAKE_ROOT/git.log"
url=$3
path=$4
mkdir -p "$path"
printf '\\n[submodule "%s"]\\n\\tpath = %s\\n\\turl = %s\\n' "$path" "$path" "$url" >> .gitmodules
''',
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{fake_bin}{os.pathsep}{self.env['PATH']}"
        self.env["FAKE_ROOT"] = str(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_add(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.root / "scripts" / "add-game.sh"), *args],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_adds_default_submodule_and_todo_entry_then_repeats_safely(self) -> None:
        first = self.run_add("rs-tetris")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn(
            "submodule add https://github.com/akitenkrad/rs-tetris.git games/rs-tetris",
            (self.root / "git.log").read_text(encoding="utf-8"),
        )
        catalog = (self.root / "games.toml").read_text(encoding="utf-8")
        self.assertEqual(catalog.count('key = "rs-tetris"'), 1)
        self.assertIn('title = "TODO"', catalog)
        self.assertIn("Fill in the TODO fields", first.stdout)
        self.assertIn("[TODO](https://github.com/akitenkrad/rs-tetris)", (self.root / "README.md").read_text(encoding="utf-8"))

        second = self.run_add("rs-tetris")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual((self.root / "git.log").read_text(encoding="utf-8").count("submodule add"), 1)
        catalog = (self.root / "games.toml").read_text(encoding="utf-8")
        self.assertEqual(catalog.count('key = "rs-tetris"'), 1)

    def test_rejects_invalid_key_before_invoking_git(self) -> None:
        result = self.run_add("Tetris")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid key", result.stderr)
        self.assertFalse((self.root / "git.log").exists())


if __name__ == "__main__":
    unittest.main()
