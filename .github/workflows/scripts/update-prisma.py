#!/usr/bin/env python3

import importlib.util
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


# The shared helpers live in update-all.py. Load that file as a module without
# invoking its updater orchestration entry point.
_spec = importlib.util.spec_from_file_location(
    "update_all_helpers",
    Path(__file__).with_name("update-all.py"),
)
if _spec is None or _spec.loader is None:
    raise ImportError("Unable to load shared helpers from update-all.py")
_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_helpers)
download_sha256 = _helpers.download_sha256
get_cask_path = _helpers.get_cask_path
update_cask = _helpers.update_cask

APPCAST = (
    "https://releases.talon-sec.com/api/v1/appcast.xml"
    "?appid=%7Bdfef2477-4f0e-454b-bc0d-03ce61074e4c%7D"
    "&platform=linux_rpm"
    "&architecture=x64"
    "&channel=stable"
)
SPARKLE_NS = "http://www.andymatuschak.org/xml-namespaces/sparkle"
CASK = get_cask_path("prisma-access-browser-linux.rb")


def latest_release():
    print("\n" + "=" * 80)
    print("FETCHING PRISMA")
    print("=" * 80)

    request = urllib.request.Request(
        APPCAST,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            xml_data = response.read()
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch Prisma appcast: {exc}") from exc

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as exc:
        raise RuntimeError(f"Failed to parse Prisma appcast XML: {exc}") from exc

    items = root.findall("./channel/item") or root.findall(".//item")
    if not items:
        raise ValueError("No appcast items found in Prisma XML response")

    def published_at(item):
        raw = item.findtext("pubDate", "").strip()
        if not raw:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            date = parsedate_to_datetime(raw)
        except (TypeError, ValueError, IndexError):
            return datetime.min.replace(tzinfo=timezone.utc)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return date

    latest_item = max(items, key=published_at)
    enclosure = latest_item.find("enclosure")
    if enclosure is None:
        raise ValueError("Latest Prisma appcast item has no enclosure")

    version = (
        enclosure.attrib.get(f"{{{SPARKLE_NS}}}shortVersionString")
        or enclosure.attrib.get("shortVersionString")
        or latest_item.findtext(f"{{{SPARKLE_NS}}}shortVersionString", "")
        or latest_item.findtext("version", "")
    ).strip()
    url = enclosure.attrib.get("url", "").strip()
    if not version or not url:
        raise ValueError(
            f"Prisma appcast enclosure is missing version or URL: {enclosure.attrib!r}"
        )

    sha256 = download_sha256(url)
    print(f"Latest Version : {version}")
    print(f"Latest URL     : {url}")
    print(f"SHA256         : {sha256}")
    return {"version": version, "url": url, "sha256": sha256}


def main():
    update_cask(CASK, latest_release())


if __name__ == "__main__":
    main()
