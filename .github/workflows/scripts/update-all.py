#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def find_repo_root():
    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "Casks").is_dir():
            return parent

    raise RuntimeError(
        "Unable to locate repository root containing Casks directory"
    )


def print_header(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main():
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
        print()
        print_header(f"Running {script.name}")

        result = subprocess.run(
            [sys.executable, str(script)]
        )

        if result.returncode == 0:
            print(f"SUCCESS: {script.name}")
        else:
            print(f"FAILED : {script.name}")
            failed.append(script.name)

    print()
    print_header("Summary")

    print(f"Total     : {len(updater_scripts)}")
    print(
        f"Succeeded : {len(updater_scripts) - len(failed)}"
    )
    print(f"Failed    : {len(failed)}")

    if failed:
        print()
        print("Failed scripts:")

        for script in failed:
            print(f" - {script}")

        sys.exit(1)

    print()
    print("All updater scripts completed successfully.")


if __name__ == "__main__":
    main()