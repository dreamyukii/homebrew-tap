#!/usr/bin/env python3

import hashlib
import re
import sys
import urllib.request
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse


def get_cask_path(name: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        casks_dir = parent / "Casks"
        if casks_dir.is_dir():
            path = casks_dir / name
            if not path.is_file():
                raise FileNotFoundError(f"Cask file not found: {path}")
            return path

    raise RuntimeError("Unable to locate repository root containing Casks directory")


def download_sha256(url: str, timeout: int = 60) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    digest = hashlib.sha256()

    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_length = response.headers.get("Content-Length")
        total_size = (
            int(content_length)
            if content_length and content_length.isdecimal()
            else 0
        )
        downloaded = 0

        while chunk := response.read(65536):
            digest.update(chunk)
            downloaded += len(chunk)

            if total_size:
                percent = min(downloaded * 100 // total_size, 100)
                progress = (
                    f"Downloading: {percent:3d}% "
                    f"({downloaded / 1024**2:.1f}/"
                    f"{total_size / 1024**2:.1f} MiB)"
                )
            else:
                progress = (
                    f"Downloaded: {downloaded / 1024**2:.1f} MiB"
                )

            sys.stdout.write(f"\r{progress}")
            sys.stdout.flush()

        sys.stdout.write("\n")

    return digest.hexdigest()


def update_cask(path: str | Path, release: Mapping[str, str]) -> None:
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

API = (
    "https://discord.com/api/downloads/distributions/app/installers/latest"
    "?channel=stable&platform=linux&arch=x64&format=rpm"
)

CASK = get_cask_path(
    "discord-linux.rb"
)


def latest_release():
    print()
    print("=" * 80)
    print("FETCHING DISCORD")
    print("=" * 80)

    request = urllib.request.Request(
        API,
        headers={"User-Agent": "Mozilla/5.0"},
        method="HEAD",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        url = response.geturl()

    match = re.search(
        r"/linux/x64/([^/]+)/Discord\.rpm$",
        urlparse(url).path,
    )
    if match is None:
        raise RuntimeError(f"Unexpected Discord RPM download URL: {url}")
    version = match.group(1)

    print(
        f"Latest Version : {version}"
    )

    print(
        f"Latest URL     : {url}"
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
    update_cask(
        CASK,
        latest_release(),
    )


if __name__ == "__main__":
    main()