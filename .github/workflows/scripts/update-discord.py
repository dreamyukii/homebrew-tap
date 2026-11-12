#!/usr/bin/env python3

import importlib.util
import json
import urllib.request
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

API = "https://discord.com/api/updates/stable?platform=linux"
CASK = get_cask_path("discord-linux.rb")


def latest_release():
    print("\n" + "=" * 80)
    print("FETCHING DISCORD")
    print("=" * 80)

    request = urllib.request.Request(
        API,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch Discord release metadata: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected Discord API response: {data!r}")

    version = data.get("name") or data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"Discord API response did not include a version: {data!r}")
    version = version.strip()

    url = f"https://dl.discordapp.net/apps/linux/{version}/discord-{version}.tar.gz"
    print(f"Latest Version : {version}")
    print(f"Latest URL     : {url}")

    sha256 = download_sha256(url)
    print(f"SHA256         : {sha256}")

    return {"version": version, "url": url, "sha256": sha256}


def main():
    update_cask(CASK, latest_release())


if __name__ == "__main__":
    main()
