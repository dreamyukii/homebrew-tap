#!/usr/bin/env python3

import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

SPARKLE_NS = "http://www.andymatuschak.org/xml-namespaces/sparkle"

APPCAST = (
    "https://releases.talon-sec.com/api/v1/appcast.xml"
    "?appid=%7Bdfef2477-4f0e-454b-bc0d-03ce61074e4c%7D"
    "&platform=linux_rpm"
    "&architecture=x64"
    "&channel=stable"
)

ROOT = Path(__file__).resolve().parent.parent
CASK = ROOT / "Casks" / "prisma-access-browser-linux.rb"


def download_sha256(url):
    print()
    print("Downloading package for SHA256 calculation...")
    print(url)

    sha = hashlib.sha256()

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(request) as response:
        length = response.headers.get("Content-Length")

        if length:
            length = int(length)
            print(
                f"Size: {length / 1024 / 1024:.2f} MB"
            )

        downloaded = 0

        while True:
            chunk = response.read(1024 * 1024)

            if not chunk:
                break

            downloaded += len(chunk)

            sha.update(chunk)

            if length:
                print(
                    f"\rDownloaded: "
                    f"{downloaded / 1024 / 1024:.2f} MB / "
                    f"{length / 1024 / 1024:.2f} MB",
                    end="",
                    flush=True,
                )

    print()
    return sha.hexdigest()


def latest_release():
    print()
    print("=" * 80)
    print("FETCHING PRISMA ACCESS BROWSER")
    print("=" * 80)

    print(f"AppCast: {APPCAST}")

    request = urllib.request.Request(
        APPCAST,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(request) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    items = root.findall("./channel/item")

    if not items:
        raise RuntimeError(
            "No releases found in AppCast"
        )

    print(f"Releases Found: {len(items)}")

    latest_item = max(
        items,
        key=lambda item: parsedate_to_datetime(
            item.findtext("pubDate", "")
        ),
    )

    enclosure = latest_item.find("enclosure")

    if enclosure is None:
        raise RuntimeError(
            "No enclosure found"
        )

    version = enclosure.attrib[
        f"{{{SPARKLE_NS}}}shortVersionString"
    ]

    url = enclosure.attrib["url"]

    pubdate = latest_item.findtext(
        "pubDate",
        "",
    )

    print(f"Latest Version : {version}")
    print(f"Published      : {pubdate}")
    print(f"RPM URL        : {url}")

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

    print()
    print("=" * 80)
    print("UPDATING CASK")
    print("=" * 80)

    content = CASK.read_text(
        encoding="utf-8"
    )

    original_content = content

    current_version = re.search(
        r'version\s+"([^"]*)"',
        content,
    )

    current_sha = re.search(
        r'sha256\s+"([^"]*)"',
        content,
    )

    current_url = re.search(
        r'url\s+"([^"]*)"',
        content,
    )

    print(
        "Current Version:",
        current_version.group(1)
        if current_version
        else "unknown",
    )

    print(
        "Current SHA256:",
        current_sha.group(1)
        if current_sha
        else "unknown",
    )

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
        print(
            "No updates required."
        )
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