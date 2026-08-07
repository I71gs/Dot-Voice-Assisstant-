"""
modules/clipboard.py — DOT Clipboard Module

Get, set, and clear the system clipboard using pyperclip.
"""

from __future__ import annotations

from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger

log = get_logger("clipboard")


def _get_pyperclip():
    try:
        import pyperclip
        return pyperclip
    except ImportError:
        return None


def get_clipboard(**_) -> str:
    pc = _get_pyperclip()
    if pc is None:
        return "✗ pyperclip not installed. Run: pip install pyperclip"
    try:
        text = pc.paste()
        if not text:
            return "ℹ  Clipboard is empty."
        preview = text[:500]
        suffix = f"\n[... {len(text) - 500} more characters]" if len(text) > 500 else ""
        return f"📋 Clipboard contents:\n{preview}{suffix}"
    except Exception as e:
        return f"✗ Could not read clipboard: {e}"


def set_clipboard(text: str, **_) -> str:
    pc = _get_pyperclip()
    if pc is None:
        return "✗ pyperclip not installed. Run: pip install pyperclip"
    try:
        pc.copy(text)
        preview = text[:80] + ("..." if len(text) > 80 else "")
        return f"✓ Copied to clipboard: {preview}"
    except Exception as e:
        return f"✗ Could not set clipboard: {e}"


def clear_clipboard(**_) -> str:
    pc = _get_pyperclip()
    if pc is None:
        return "✗ pyperclip not installed."
    try:
        pc.copy("")
        return "✓ Clipboard cleared."
    except Exception as e:
        return f"✗ Could not clear clipboard: {e}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("get_clipboard", get_clipboard, "Show clipboard contents",
                     aliases=["get clipboard", "show clipboard", "clipboard", "paste"],
                     category="Clipboard"),
        make_command("set_clipboard", set_clipboard, "Copy text to clipboard",
                     aliases=["copy", "set clipboard"],
                     args_help="<text>", category="Clipboard"),
        make_command("clear_clipboard", clear_clipboard, "Clear clipboard",
                     aliases=["clear clipboard"],
                     category="Clipboard"),
    ])
