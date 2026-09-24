"""Capture the messy analyzer's output as golden files.

Run this ONCE, before any refactoring. The golden files become the
contract: the refactored version must reproduce them byte-for-byte.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESSY = ROOT / "messy" / "analyzer.py"
FIXTURES = ROOT / "fixtures"


def run(script: Path, *args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )
    return result.stdout


CASES = [
    ("sample1.txt",),
    ("sample2.txt",),
    ("empty.txt",),
    ("only_blank.txt",),
    ("sample1.txt", "--format", "html"),
    ("sample2.txt", "--format", "html"),
    ("sample1.txt", "--format", "csv"),
    ("sample1.txt", "--summary"),
    ("sample1.txt", "--min-length", "5"),
]


def main() -> None:
    for case in CASES:
        args = [str(FIXTURES / a) if a.endswith(".txt") else a for a in case]
        output = run(MESSY, *args)
        if "html" in case:
            suffix = ".golden.html"
        elif "csv" in case:
            suffix = ".golden.csv"
        elif "summary" in case:
            suffix = ".golden.summary.txt"
        elif "min-length" in case:
            suffix = ".golden.min5.txt"
        else:
            suffix = ".golden.txt"
        name = case[0].replace(".txt", "") + suffix
        target = FIXTURES / name
        target.write_text(output, encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()