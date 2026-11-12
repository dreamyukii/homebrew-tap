#!/usr/bin/env python3

import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping
from urllib import request

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CASKS_DIR = _REPO_ROOT / "Casks"


def get_cask_path(name: str) -> Path:
    """Return the path to a cask in this repository."""
    path = _CASKS_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Cask file not found: {path}")
    return path


def download_sha256(url: str, timeout: int = 60) -> str:
    """Download a release artifact and return its SHA-256 digest."""
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    digest = hashlib.sha256()

    with request.urlopen(req, timeout=timeout) as response:
        while chunk := response.read(65536):
            digest.update(chunk)

    return digest.hexdigest()


def update_cask(path: str | Path, release: Mapping[str, str]) -> None:
    """Update the version, SHA-256, and URL fields in a cask file."""
    cask_path = Path(path)
    text = cask_path.read_text(encoding="utf-8")

    for key in ("version", "sha256", "url"):
        value = release[key]
        if '"' in value or "\n" in value:
            raise ValueError(f"Invalid value for cask field {key!r}")

        pattern = rf'(?m)^(\s*{key}\s+)"[^"]*"'
        text, count = re.subn(
            pattern,
            lambda match: f'{match.group(1)}"{value}"',
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not update {key!r} in {cask_path}")

    cask_path.write_text(text, encoding="utf-8")


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "Casks").is_dir():
            return parent
    raise RuntimeError("Unable to locate repository root containing Casks directory")


def print_header(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    root = find_repo_root()
    print_header("Homebrew Tap Updater")
    print(f"Repository Root : {root}")

    scripts_dir = Path(__file__).resolve().parent
    updater_scripts = sorted(
        script
        for script in scripts_dir.glob("update-*.py")
        if script.name != "update-all.py"
    )

    if not updater_scripts:
        print("No updater scripts found.")
        sys.exit(1)

    failed = []
    for script in updater_scripts:
        print_header(f"Running {script.name}")
        result = subprocess.run([sys.executable, str(script)], check=False)
        if result.returncode == 0:
            print(f"SUCCESS: {script.name}")
        else:
            print(f"FAILED : {script.name} (exit code {result.returncode})")
            failed.append(script.name)

    print_header("Summary")
    print(f"Total     : {len(updater_scripts)}")
    print(f"Succeeded : {len(updater_scripts) - len(failed)}")
    print(f"Failed    : {len(failed)}")

    if failed:
        print("\nFailed scripts:")
        for script in failed:
            print(f" - {script}")
        sys.exit(1)

    print("\nAll updater scripts completed successfully.")


if __name__ == "__main__":
    main()
