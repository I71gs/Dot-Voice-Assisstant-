"""
modules/reminders.py — DOT Reminder Module

Supports creating, listing, deleting reminders.
Schedules reminders in background using core/scheduler.py.
Persists reminders to data/reminders.json.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Optional

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from services.notifications import notify

log = get_logger("reminders")

REMINDERS_FILE = cfg.DATA_DIR / "reminders.json"


def _load_reminders() -> list[dict[str, Any]]:
    if REMINDERS_FILE.exists():
        try:
            with REMINDERS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_reminders(reminders: list[dict[str, Any]]) -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with REMINDERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2)


_scheduler = None


def trigger_reminder(message: str, time_str: str) -> None:
    notify("DOT Reminder", message)
    log.info("Reminder triggered: %s", message)

    reminders = _load_reminders()
    for r in reminders:
        if r.get("message") == message and r.get("time") == time_str:
            r["completed"] = True
    _save_reminders(reminders)


def add_reminder(message: str, delay: str, unit: str, **_) -> str:
    global _scheduler
    try:
        val = int(delay)
    except ValueError:
        return f"✗ Invalid delay: {delay}"

    unit_clean = unit.lower().strip()
    seconds = val
    if "minute" in unit_clean:
        seconds = val * 60
    elif "hour" in unit_clean:
        seconds = val * 3600

    target_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    time_str = target_time.isoformat()

    reminders = _load_reminders()
    reminders.append({
        "message": message,
        "time": time_str,
        "completed": False,
        "created": datetime.datetime.now().isoformat()
    })
    _save_reminders(reminders)

    if _scheduler:
        _scheduler.schedule_once(seconds, trigger_reminder, message, time_str)
        log.info("Scheduled reminder background: %s in %ds", message, seconds)

    return f"✓ Reminder set in {delay} {unit}: {message}"


def add_reminder_simple(delay: str, unit: str, **_) -> str:
    try:
        print("Enter reminder message:")
        msg = input().strip()
        if not msg:
            return "✗ Reminder cancelled: message empty."
        return add_reminder(msg, delay, unit)
    except (EOFError, KeyboardInterrupt):
        return "✗ Reminder cancelled."


def list_reminders(**_) -> str:
    reminders = _load_reminders()
    if not reminders:
        return "No reminders configured."

    pending = [r for r in reminders if not r.get("completed")]
    completed = [r for r in reminders if r.get("completed")]

    lines = []
    if pending:
        lines.append("⏳ PENDING REMINDERS:")
        for idx, r in enumerate(pending, 1):
            t = datetime.datetime.fromisoformat(r["time"]).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"  {idx}. [ {t} ] {r['message']}")

    if completed:
        if lines:
            lines.append("")
        lines.append("✓ COMPLETED REMINDERS:")
        for idx, r in enumerate(completed, 1):
            lines.append(f"  - {r['message']}")

    return "\n".join(lines)


def delete_reminder(index: str, **_) -> str:
    try:
        idx = int(index) - 1
    except ValueError:
        return f"✗ Invalid index: {index}"

    reminders = _load_reminders()
    pending = [r for r in reminders if not r.get("completed")]

    if idx < 0 or idx >= len(pending):
        return f"✗ Index out of range: {index}"

    target = pending[idx]
    reminders = [r for r in reminders if not (r["time"] == target["time"] and r["message"] == target["message"])]
    _save_reminders(reminders)

    return f"✓ Deleted reminder: {target['message']}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    global _scheduler
    _scheduler = scheduler

    if _scheduler:
        now_iso = datetime.datetime.now().isoformat()
        reminders = _load_reminders()
        count = 0
        for r in reminders:
            if not r.get("completed"):
                r_time = r.get("time", "")
                if r_time > now_iso:
                    diff = (datetime.datetime.fromisoformat(r_time) - datetime.datetime.now()).total_seconds()
                    _scheduler.schedule_once(diff, trigger_reminder, r["message"], r_time)
                    count += 1
                else:
                    _scheduler.schedule_once(1.0, trigger_reminder, r["message"], r_time)
                    count += 1
        if count > 0:
            log.info("Re-scheduled %d pending reminders from disk", count)

    registry.register_all([
        make_command("add_reminder", add_reminder, "Add a reminder",
                     aliases=["remind me in", "set reminder"],
                     args_help="<message> in <delay> <unit>", category="Reminders"),
        make_command("add_reminder_simple", add_reminder_simple, "Add a reminder (prompts for message)",
                     args_help="in <delay> <unit>", category="Reminders"),
        make_command("list_reminders", list_reminders, "List all reminders",
                     aliases=["list reminders", "show reminders", "my reminders"], category="Reminders"),
        make_command("delete_reminder", delete_reminder, "Delete a pending reminder",
                     aliases=["delete reminder"], args_help="<index>", category="Reminders"),
    ])
