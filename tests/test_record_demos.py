from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = PROJECT_ROOT / "scripts" / "record-demos.sh"
EXPECTED_KEYS = {
    "rs-nim",
    "rs-tic-tac-toe",
    "rs-connect-four",
    "rs-gomoku",
}


class RecordDemosIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(dir=PROJECT_ROOT)
        self.root = Path(self.temp_dir.name)
        (self.root / "scripts").mkdir()
        (self.root / "demos").mkdir()
        if not SOURCE_SCRIPT.exists():
            self.fail("scripts/record-demos.sh must exist")
        shutil.copy2(SOURCE_SCRIPT, self.root / "scripts" / "record-demos.sh")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_script(
        self, *args: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["/bin/bash", "scripts/record-demos.sh", *args],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_rejects_invalid_key(self) -> None:
        result = self.run_script("Nim")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid key", result.stderr)

    def test_rejects_key_without_tape(self) -> None:
        result = self.run_script("rs-missing")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tape", result.stderr.lower())

    def test_reports_missing_vhs(self) -> None:
        (self.root / "demos" / "rs-x.tape").write_text(
            "Output docs/assets/games/rs-x.gif\n", encoding="utf-8"
        )
        empty_path = self.root / "empty-path"
        empty_path.mkdir()
        env = os.environ.copy()
        env["PATH"] = str(empty_path)

        result = self.run_script("rs-x", env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("vhs", result.stderr.lower())


class DemoTapeContractTests(unittest.TestCase):
    def test_each_tape_replays_its_game_and_stays_on_the_final_position(self) -> None:
        tapes = sorted((PROJECT_ROOT / "demos").glob("*.tape"))
        self.assertEqual({tape.stem for tape in tapes}, EXPECTED_KEYS)
        for tape in tapes:
            with self.subTest(tape=tape.name):
                key = tape.stem
                contents = tape.read_text(encoding="utf-8")
                self.assertIn(
                    f"Output docs/assets/games/{key}.gif",
                    contents.splitlines(),
                )
                self.assertNotIn("Output /", contents)
                self.assertIn(f"games/{key}/examples/records/", contents)
                self.assertIn(f"games/{key}/target/release/{key} --lang en replay ", contents)
                # The GIF must end on the final position, not on an empty shell after the game quits.
                self.assertNotIn("--exit-on-end", contents)


if __name__ == "__main__":
    unittest.main()
