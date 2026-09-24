"""Verify that the refactored analyzer matches the messy original exactly.

Runs both `messy/analyzer.py` and `src/analyzer.py` on every fixture with
every CLI combination, and asserts that stdout, stderr, and exit code are
identical. Any mismatch is reported and the process exits non-zero.

Usage:
    python scripts/verify.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESSY = ROOT / "messy" / "analyzer.py"
CLEAN = ROOT / "src" / "analyzer.py"
FIXTURES = ROOT / "fixtures"


def run(script: Path, *args: str) -> tuple[str, str, int]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


CASES: list[tuple[str, ...]] = [
    ("sample1.txt",),
    ("sample2.txt",),
    ("empty.txt",),
    ("only_blank.txt",),
    ("sample1.txt", "--format", "html"),
    ("sample2.txt", "--format", "html"),
    ("sample1.txt", "--format", "csv"),
    ("sample1.txt", "--summary"),
    ("sample1.txt", "--min-length", "5"),
    ("does-not-exist.txt",),
    (),
]


def main() -> int:
    if not CLEAN.exists():
        print(f"SKIP: {CLEAN} does not exist yet — nothing to compare.")
        return 0

    failures = 0
    for case in CASES:
        args = tuple(
            str(FIXTURES / a) if a.endswith(".txt") or a == "does-not-exist.txt" else a
            for a in case
        )
        messy_out, messy_err, messy_code = run(MESSY, *args)
        clean_out, clean_err, clean_code = run(CLEAN, *args)

        if (messy_out, messy_err, messy_code) != (clean_out, clean_err, clean_code):
            failures += 1
            print(f"MISMATCH: {' '.join(args) or '<no args>'}")
            if messy_out != clean_out:
                print("  stdout differs")
            if messy_err != clean_err:
                print("  stderr differs")
            if messy_code != clean_code:
                print(f"  exit code differs: messy={messy_code} clean={clean_code}")
        else:
            print(f"OK: {' '.join(case) or '<no args>'}")

    if failures:
        print(f"\n{failures} mismatches found.")
        return 1
    print("\nAll outputs match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())