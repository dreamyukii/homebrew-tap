#!/usr/bin/env python3

import json
import urllib.request

from common import (
    download_sha256,
    get_cask_path,
    update_cask,
)

API = (
    "https://discord.com/api/updates/stable"
    "?platform=linux"
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
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(request) as response:
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