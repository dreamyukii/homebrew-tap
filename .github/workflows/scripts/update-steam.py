#!/usr/bin/env python3

import json
import re
import urllib.request
from pathlib import Path
from typing import Mapping


def get_cask_path(name: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        casks_dir = parent / "Casks"
        if casks_dir.is_dir():
            path = casks_dir / name
            if not path.is_file():
                raise FileNotFoundError(f"Cask file not found: {path}")
            return path

    raise RuntimeError("Unable to locate repository root containing Casks directory")


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


API = "https://api.github.com/repos/ivan-hc/Steam-appimage/releases/latest"
CASK = get_cask_path("steam-linux-appimage.rb")
RELEASE_TAG_PATTERN = re.compile(
    r"(?P<app_version>\d+(?:\.\d+)+-\d+)"
    r"@(?P<date>\d{4}-\d{2}-\d{2})_(?P<build>\d+)\Z"
)


def latest_release() -> dict[str, str]:
    request = urllib.request.Request(
        API,
        headers={"Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)

    tag = release.get("tag_name", "")
    tag_match = RELEASE_TAG_PATTERN.fullmatch(tag)
    if tag_match is None:
        raise RuntimeError(f"Unexpected Steam AppImage release tag: {tag!r}")

    expected_name = (
        f"Steam-{tag_match['app_version']}-anylinux-x86_64.AppImage"
    )
    assets = [
        asset
        for asset in release.get("assets", [])
        if asset.get("name") == expected_name
    ]
    if len(assets) != 1:
        raise RuntimeError(
            f"Expected one {expected_name!r} asset, found {len(assets)}"
        )

    asset = assets[0]
    digest = asset.get("digest", "")
    digest_match = re.fullmatch(r"sha256:([0-9a-fA-F]{64})", digest)
    if digest_match is None:
        raise RuntimeError(
            f"Missing or invalid SHA-256 digest for {expected_name!r}"
        )

    version = (
        f"{tag_match['app_version']}-{tag_match['date']}-{tag_match['build']}"
    )
    url = asset.get("browser_download_url", "")
    if not url.startswith("https://github.com/ivan-hc/Steam-appimage/"):
        raise RuntimeError(f"Unexpected Steam AppImage download URL: {url!r}")

    return {
        "version": version,
        "sha256": digest_match[1].lower(),
        "url": url,
    }


def main() -> None:
    update_cask(CASK, latest_release())


if __name__ == "__main__":
    main()
