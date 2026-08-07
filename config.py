"""
config.py — DOT Assistant Configuration

Central loader/saver for data/settings.json.
All modules must import settings from here, not hard-code paths.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Project root is the directory that contains this file.
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Default configuration
DEFAULT_SETTINGS: dict[str, Any] = {
    "assistant_name": "DOT",
    "tts_enabled": False,
    "music_dir": str(Path.home() / "Music"),
    "video_dir": str(Path.home() / "Videos"),
    "pictures_dir": str(Path.home() / "Pictures"),
    "downloads_dir": str(Path.home() / "Downloads"),
    "screenshot_dir": str(ROOT_DIR / "screenshots"),
    "notes_file": str(DATA_DIR / "notes.txt"),
    "app_paths": {
        "notepad":    "notepad.exe",
        "calculator": "calc.exe",
        "paint":      "mspaint.exe",
        "explorer":   "explorer.exe",
        "chrome":     "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "firefox":    "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "edge":       "C:\\Program Files\\x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "word":       "winword.exe",
        "excel":      "excel.exe",
        "powershell": "powershell.exe",
        "cmd":        "cmd.exe",
        "spotify":    "spotify:",
    },
    "weather_api_key": "",
    "email_address": "",
    "email_password": "",
    "language": "en-in",
    "timezone": "UTC",
    "genz_slangs": True,
    "dark_jokes": True,
    "max_history": 200,
}


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict[str, Any]:
    _ensure_data_dir()
    if SETTINGS_FILE.exists():
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                on_disk = json.load(f)
            merged = {**DEFAULT_SETTINGS, **on_disk}
            merged["app_paths"] = {
                **DEFAULT_SETTINGS.get("app_paths", {}),
                **on_disk.get("app_paths", {}),
            }
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    save_settings(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict[str, Any]) -> None:
    _ensure_data_dir()
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get(key: str, default: Any = None) -> Any:
    return load_settings().get(key, default)


def set_key(key: str, value: Any) -> None:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
