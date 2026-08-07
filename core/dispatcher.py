"""
core/dispatcher.py — DOT Assistant Dispatcher

Receives a ParsedCommand, checks permissions, and calls the correct handler.
Returns a string result. Never prints directly.
"""

from __future__ import annotations

from core.command_registry import CommandRegistry
from core.context import Context
from core.logger import get_logger
from core.parser import ParsedCommand
from core.permissions import PermissionLevel, require_confirmation

log = get_logger("dispatcher")


class Dispatcher:
    def __init__(self, registry: CommandRegistry, context: Context) -> None:
        self._registry = registry
        self._context = context

    def dispatch(self, cmd: ParsedCommand) -> str:
        log.info("dispatch | intent=%s args=%s", cmd.intent, cmd.arguments)

        if cmd.intent == "unknown":
            return (
                "Command not recognized. Type 'help' to see available commands."
            )

        command_def = self._registry.lookup(cmd.intent)
        if command_def is None:
            log.warning("No handler registered for intent: %s", cmd.intent)
            return f"No handler registered for: {cmd.intent!r}"

        if command_def.permission != PermissionLevel.SAFE:
            action_desc = (
                f"{command_def.description}"
                + (f" — args: {cmd.arguments}" if cmd.arguments else "")
            )
            approved = require_confirmation(action_desc, command_def.permission)
            if not approved:
                log.info("User cancelled: %s", cmd.intent)
                return "✗ Cancelled."

        try:
            result = command_def.handler(
                **cmd.arguments,
                _context=self._context,
            ) or ""
        except TypeError:
            try:
                result = command_def.handler(**cmd.arguments) or ""
            except Exception as exc:
                log.exception("Handler error for intent=%s", cmd.intent)
                return f"✗ Error: {exc}"
        except Exception as exc:
            log.exception("Handler error for intent=%s", cmd.intent)
            return f"✗ Error: {exc}"

        self._context.record(cmd.raw, result)
        log.info("result | intent=%s result=%.100s", cmd.intent, result)
        return result
