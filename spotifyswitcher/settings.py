from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "StreamFastInput"
STATE_FILE = CONFIG_DIR / "state.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": None,           # None means "follow Windows"
    "live_device": None,     # None means "use the built-in default"
    "normal_device": None,   # None means "use the built-in default"
    "manage_voicemeeter": True,
    "target_process": None,    # None means "use the built-in default" (Spotify.exe)
    "voicemeeter_path": None,  # None means "use the built-in default" install path
}


def load_mode() -> str:
    try:
        return json.loads(STATE_FILE.read_text()).get("mode", "NORMAL")
    except Exception:
        return "NORMAL"


def save_mode(mode: str) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"mode": mode}))
    except OSError:
        pass


def load_settings() -> dict:
    merged = dict(DEFAULT_SETTINGS)
    if not SETTINGS_FILE.exists():
        return merged
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            merged.update(data)
    except Exception:
        pass
    return merged


def save_settings(data: dict) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def get_theme() -> str | None:
    """Explicitly chosen theme, or None to follow Windows."""
    name = load_settings().get("theme")
    return name if name in ("light", "dark") else None
