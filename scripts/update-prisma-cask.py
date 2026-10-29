#!/usr/bin/env python3

import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

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
    sha = hashlib.sha256()

    with urllib.request.urlopen(url) as response:
        while True:
            chunk = response.read(1024 * 1024)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()


def latest_release():
    with urllib.request.urlopen(APPCAST) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    enclosure = root.find("./channel/item/enclosure")

    return {
        "version": enclosure.attrib[
            "{http://www.andymatuschak.org/xml-namespaces/sparkle}shortVersionString"
        ],
        "url": enclosure.attrib["url"],
    }


def update_cask():
    if not CASK.exists():
        raise FileNotFoundError(
            f"Cask file not found: {CASK}"
        )

    release = latest_release()

    print(f"Latest Version : {release['version']}")
    print(f"Latest URL     : {release['url']}")
    print("Calculating SHA256...")

    sha256 = download_sha256(release["url"])

    print(f"SHA256         : {sha256}")

    content = CASK.read_text(encoding="utf-8")

    original_content = content

    content = re.sub(
        r'version\s+"[^"]*"',
        f'version "{release["version"]}"',
        content,
        count=1,
    )

    content = re.sub(
        r'sha256\s+"[^"]*"',
        f'sha256 "{sha256}"',
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
        print("No changes needed.")
        return

    CASK.write_text(content, encoding="utf-8")

    print()
    print("Updated successfully:")
    print(f"File    : {CASK}")
    print(f"Version : {release['version']}")
    print(f"SHA256  : {sha256}")


if __name__ == "__main__":
    update_cask()