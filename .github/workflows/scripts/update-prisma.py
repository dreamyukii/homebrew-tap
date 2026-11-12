#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET

from email.utils import parsedate_to_datetime

from common import (
    download_sha256,
    get_cask_path,
    update_cask,
)

APPCAST = (
    "https://releases.talon-sec.com/api/v1/appcast.xml"
    "?appid=%7Bdfef2477-4f0e-454b-bc0d-03ce61074e4c%7D"
    "&platform=linux_rpm"
    "&architecture=x64"
    "&channel=stable"
)

SPARKLE_NS = (
    "http://www.andymatuschak.org/xml-namespaces/sparkle"
)

CASK = get_cask_path(
    "prisma-access-browser-linux.rb"
)


def latest_release():
    print()
    print("=" * 80)
    print("FETCHING PRISMA")
    print("=" * 80)

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

    latest_item = max(
        items,
        key=lambda item:
        parsedate_to_datetime(
            item.findtext("pubDate", "")
        ),
    )

    enclosure = latest_item.find(
        "enclosure"
    )

    version = enclosure.attrib[
        f"{{{SPARKLE_NS}}}shortVersionString"
    ]

    url = enclosure.attrib["url"]

    sha256 = download_sha256(url)

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