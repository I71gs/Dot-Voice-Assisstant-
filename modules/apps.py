"""
modules/apps.py — DOT Application Management Module

Open, close, and manage Windows applications.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional

import psutil

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from core.permissions import PermissionLevel

log = get_logger("apps")


def _get_app_paths() -> dict[str, str]:
    return cfg.load_settings().get("app_paths", {})


def _launch(path: str) -> bool:
    try:
        if path.endswith(":"):
            os.startfile(path)
        else:
            os.startfile(path)
        return True
    except OSError:
        try:
            subprocess.Popen(path, shell=True)
            return True
        except Exception:
            return False


def open_app(app: str, **_) -> str:
    app_lower = app.lower().strip()
    paths = _get_app_paths()

    if app_lower in paths:
        path = paths[app_lower]
        if _launch(path):
            log.info("Opened app: %s -> %s", app_lower, path)
            return f"✓ Opening {app.title()}"
        return f"✗ Could not launch {app}: path may be incorrect ({path})"

    matches = [k for k in paths if app_lower in k]
    if len(matches) == 1:
        path = paths[matches[0]]
        if _launch(path):
            log.info("Opened app (partial match): %s -> %s", matches[0], path)
            return f"✓ Opening {matches[0].title()}"

    if matches:
        options = ", ".join(matches)
        return f"✗ Multiple matches for '{app}': {options}"

    if _launch(app_lower):
        return f"✓ Launched: {app}"

    available = ", ".join(sorted(paths.keys()))
    return f"✗ App '{app}' not found. Configured apps: {available}"


def close_app(app: Optional[str] = None, **_) -> str:
    if app:
        return terminate_app(app)
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd:
            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
            return "✓ Close signal sent to active window."
        return "✗ No active window found."
    except Exception as e:
        return f"✗ Could not close window: {e}"


def minimize_windows(**_) -> str:
    try:
        import ctypes
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
        return "✓ All windows minimized."
    except Exception as e:
        try:
            subprocess.run(
                'powershell -command "(New-Object -ComObject Shell.Application).MinimizeAll()"',
                shell=True, capture_output=True
            )
            return "✓ All windows minimized."
        except Exception:
            return f"✗ Could not minimize: {e}"


def show_desktop(**_) -> str:
    return minimize_windows()


def list_running_apps(**_) -> str:
    try:
        seen = set()
        rows = []
        for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                name = proc.info["name"]
                if name and name not in seen:
                    seen.add(name)
                    rows.append((name, proc.info["memory_percent"] or 0.0))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        rows.sort(key=lambda x: x[1], reverse=True)
        lines = [f"🖥  Running Applications ({len(rows)} processes)\n"]
        for name, mem in rows[:20]:
            lines.append(f"  {name:<40} {mem:.1f}% RAM")
        return "\n".join(lines)
    except Exception as e:
        return f"✗ Could not list apps: {e}"


def terminate_app(app: str, **_) -> str:
    try:
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if app.lower() in proc.info["name"].lower():
                    proc.terminate()
                    killed.append(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed:
            return f"✓ Terminated: {', '.join(set(killed))}"
        return f"✗ No process found matching '{app}'"
    except Exception as e:
        return f"✗ Terminate error: {e}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("open_app", open_app, "Open an application",
                     aliases=["open", "launch", "start"],
                     args_help="<app>", category="Applications"),
        make_command("close_app", close_app, "Close the active window or a named app",
                     aliases=["close app", "close window"],
                     args_help="[app]", category="Applications"),
        make_command("minimize_windows", minimize_windows, "Minimize all windows",
                     aliases=["minimize", "show desktop"],
                     category="Applications"),
        make_command("show_desktop", show_desktop, "Show the desktop",
                     aliases=["desktop"],
                     category="Applications"),
        make_command("list_running_apps", list_running_apps, "List all running processes",
                     aliases=["list apps", "running apps", "processes list"],
                     category="Applications"),
        make_command("terminate_app", terminate_app, "Force-terminate a named process",
                     aliases=["terminate", "force close", "kill app"],
                     args_help="<app>", category="Applications",
                     permission=PermissionLevel.CONFIRM),
    ])
