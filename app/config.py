from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path.home() / "WillpoVoice"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULTS = {
    "dark_mode": True,
    "history": [],
    "last_voice": "",
}


def load_settings() -> Dict[str, Any]:
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            merged = dict(DEFAULTS)
            merged.update(data)
            return merged
    except Exception:
        pass

    return dict(DEFAULTS)


def save_settings(settings: Dict[str, Any]) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass
