"""
modules/screenshots.py — DOT Screenshot Module

Captures screenshots and saves them to a configured directory.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from PIL import ImageGrab

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger

log = get_logger("screenshots")


def _get_screenshot_dir() -> Path:
    settings = cfg.load_settings()
    d = Path(settings.get("screenshot_dir", str(cfg.ROOT_DIR / "screenshots")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def take_screenshot(open_after: bool = False, **_) -> str:
    try:
        folder = _get_screenshot_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{ts}.png"
        path = folder / filename

        im = ImageGrab.grab()
        im.save(path)
        log.info("Screenshot saved: %s", path)

        msg = f"✓ Screenshot saved: {filename}"
        if open_after:
            import os
            os.startfile(str(path))
            msg += " (opened)"
        return msg
    except Exception as e:
        log.error("take_screenshot: %s", e)
        return f"✗ Screenshot error: {e}"


def open_latest_screenshot(**_) -> str:
    try:
        import os
        folder = _get_screenshot_dir()
        files = list(folder.glob("screenshot_*.png"))
        if not files:
            return "✗ No screenshots found."
        files.sort(key=lambda x: x.stat().st_mtime)
        latest = files[-1]
        os.startfile(str(latest))
        return f"✓ Opening latest screenshot: {latest.name}"
    except Exception as e:
        return f"✗ Error opening latest screenshot: {e}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("take_screenshot", take_screenshot, "Take a screenshot",
                     aliases=["screenshot", "take screenshot", "capture screen", "snap"],
                     category="Screenshots"),
        make_command("open_latest_screenshot", open_latest_screenshot, "Open the latest screenshot",
                     aliases=["open latest screenshot", "open last screenshot"],
                     category="Screenshots"),
    ])
