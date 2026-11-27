#!/usr/bin/env python3

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Mapping


API = (
    "https://discord.com/api/updates/stable"
    "?platform=linux"
)


def get_cask_path(name: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        casks_dir = parent / "Casks"

        if casks_dir.is_dir():
            path = casks_dir / name

            if not path.is_file():
                raise FileNotFoundError(
                    f"Cask file not found: {path}"
                )

            return path

    raise RuntimeError(
        "Unable to locate repository root containing Casks directory"
    )


CASK = get_cask_path(
    "discord-linux.rb"
)


def download_sha256(
    url: str,
    timeout: int = 300,
) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(X11; Linux x86_64)"
            )
        },
    )

    digest = hashlib.sha256()

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        content_length = response.headers.get(
            "Content-Length"
        )

        total_size = (
            int(content_length)
            if content_length
            and content_length.isdecimal()
            else 0
        )

        downloaded = 0

        while chunk := response.read(
            1024 * 1024
        ):
            digest.update(chunk)

            downloaded += len(chunk)

            if total_size:
                percent = min(
                    downloaded * 100 // total_size,
                    100,
                )

                progress = (
                    f"Downloading: "
                    f"{percent:3d}% "
                    f"({downloaded / 1024**2:.1f}/"
                    f"{total_size / 1024**2:.1f} MiB)"
                )
            else:
                progress = (
                    f"Downloaded: "
                    f"{downloaded / 1024**2:.1f} MiB"
                )

            sys.stdout.write(
                f"\r{progress}"
            )

            sys.stdout.flush()

    print()

    return digest.hexdigest()


def update_cask(
    path: str | Path,
    release: Mapping[str, str],
) -> None:
    cask_path = Path(path)

    text = cask_path.read_text(
        encoding="utf-8"
    )

    old_version = re.search(
        r'version\s+"([^"]*)"',
        text,
    )

    if old_version:
        print(
            f"Current Version: "
            f"{old_version.group(1)}"
        )

    original_text = text

    for key in (
        "version",
        "sha256",
        "url",
    ):
        value = release[key]

        pattern = (
            rf'(?m)^(\s*{key}\s+)'
            r'"[^"]*"'
        )

        text, count = re.subn(
            pattern,
            lambda m: (
                f'{m.group(1)}"{value}"'
            ),
            text,
            count=1,
        )

        if count != 1:
            raise RuntimeError(
                f"Unable to update {key}"
            )

    if text == original_text:
        print()
        print("No changes required.")
        return

    cask_path.write_text(
        text,
        encoding="utf-8",
    )

    print()
    print("Updated successfully")
    print(
        f"File    : {cask_path.name}"
    )
    print(
        f"Version : {release['version']}"
    )
    print(
        f"SHA256  : {release['sha256']}"
    )


def latest_release():
    print()
    print("=" * 80)
    print("FETCHING DISCORD")
    print("=" * 80)

    request = urllib.request.Request(
        API,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(X11; Linux x86_64)"
            )
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        data = json.loads(
            response.read()
        )

    version = data["name"]

    url = (
        f"https://dl.discordapp.net/apps/linux/"
        f"{version}/discord-{version}.tar.gz"
    )

    print(
        f"Latest Version : {version}"
    )

    print(
        f"Latest URL     : {url}"
    )

    print()
    print(
        "Downloading package for SHA256 calculation..."
    )

    sha256 = download_sha256(url)

    print(
        f"SHA256         : {sha256}"
    )

    return {
        "version": version,
        "url": url,
        "sha256": sha256,
    }


def main():
    release = latest_release()

    update_cask(
        CASK,
        release,
    )


if __name__ == "__main__":
    main()