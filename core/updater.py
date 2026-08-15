from __future__ import annotations

import json
import re
import urllib.request

from app.version import APP_VERSION, GITHUB_REPO


def _parse_version(tag: str) -> tuple:
    nums = re.findall(r"\d+", tag)
    return tuple(int(x) for x in nums[:3]) if nums else (0, 0, 0)


def check_update(timeout: int = 8) -> dict | None:
    if not GITHUB_REPO:
        return None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WillpoVoice",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    tag = data.get("tag_name", "")
    if _parse_version(tag) <= _parse_version(APP_VERSION):
        return None
    assets = data.get("assets", [])
    exe = next(
        (a for a in assets if a.get("name", "").lower().endswith(".exe")),
        None,
    )
    return {
        "version": tag,
        "notes": data.get("body", "") or "Sin notas de version.",
        "url": exe.get("browser_download_url") if exe else data.get("html_url", ""),
        "size": exe.get("size", 0) if exe else 0,
    }
