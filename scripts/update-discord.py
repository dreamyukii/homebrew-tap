#!/usr/bin/env python3

import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

DISCORD_API = (
    "https://discord.com/api/updates/stable?platform=linux"
)

ROOT = Path(__file__).resolve().parent.parent
CASK = ROOT / "Casks" / "discord-linux.rb"


def download_sha256(url):
    print()
    print("Downloading package for SHA256 calculation...")
    print(url)

    with tempfile.NamedTemporaryFile() as tmp:
        subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "-A",
                "Mozilla/5.0 (X11; Linux x86_64)",
                "-o",
                tmp.name,
                url,
            ],
            check=True,
        )

        sha = hashlib.sha256()

        with open(tmp.name, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)

                if not chunk:
                    break

                sha.update(chunk)

    return sha.hexdigest()


def latest_release():
    print()
    print("=" * 80)
    print("FETCHING DISCORD")
    print("=" * 80)

    print(f"API: {DISCORD_API}")

    request = urllib.request.Request(
        DISCORD_API,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())

    version = data["name"]

    url = (
        f"https://dl.discordapp.net/apps/linux/"
        f"{version}/discord-{version}.tar.gz"
    )

    print(f"Latest Version : {version}")
    print(f"Latest URL     : {url}")

    sha256 = download_sha256(url)

    print(f"SHA256         : {sha256}")

    return {
        "version": version,
        "url": url,
        "sha256": sha256,
    }


def update_cask(release):
    if not CASK.exists():
        raise FileNotFoundError(
            f"Cask file not found: {CASK}"
        )

    content = CASK.read_text(
        encoding="utf-8"
    )

    original_content = content

    old_version = re.search(
        r'version\s+"([^"]*)"',
        content,
    )

    if old_version:
        print(f"Current Version: {old_version.group(1)}")

    content = re.sub(
        r'version\s+"[^"]*"',
        f'version "{release["version"]}"',
        content,
        count=1,
    )

    content = re.sub(
        r'sha256\s+"[^"]*"',
        f'sha256 "{release["sha256"]}"',
        content,
        count=1,
    )

    content = re.sub(
        r'url\s+"[^"]*"',
        f'url "{release["url"]}"',
        content,
        count=1,
    )

    if content == original_content:
        print()
        print("No changes needed.")
        return

    CASK.write_text(
        content,
        encoding="utf-8",
    )

    print()
    print("Updated successfully:")
    print(f"File    : {CASK}")
    print(f"Version : {release['version']}")
    print(f"SHA256  : {release['sha256']}")


def main():
    release = latest_release()
    update_cask(release)


if __name__ == "__main__":
    main()