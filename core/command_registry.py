"""
core/command_registry.py — DOT Assistant Command Registry

All commands are registered here. Modules register their handlers at startup.
The registry drives both dispatch and help generation.
New commands require NO modification to main.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from core.permissions import PermissionLevel


@dataclass
class CommandDef:
    """Definition of a single DOT command."""
    name: str                           # canonical intent name, e.g. "create_file"
    handler: Callable[..., str]         # function that executes the command
    description: str                    # one-line human-readable description
    permission: PermissionLevel = PermissionLevel.SAFE
    category: str = "General"           # group for help display
    aliases: list[str] = field(default_factory=list)   # alternative trigger phrases
    args_help: str = ""                 # e.g. "<filename>" for help display


class CommandRegistry:
    """Central registry of all DOT commands."""

    def __init__(self) -> None:
        self._by_name: dict[str, CommandDef] = {}
        self._alias_map: dict[str, str] = {}  # alias -> canonical name

    def register(self, cmd: CommandDef) -> None:
        """Register a CommandDef. Raises ValueError on duplicate names."""
        if cmd.name in self._by_name:
            raise ValueError(f"Command already registered: {cmd.name!r}")
        self._by_name[cmd.name] = cmd
        for alias in cmd.aliases:
            a = alias.lower().strip()
            self._alias_map[a] = cmd.name

    def register_all(self, commands: list[CommandDef]) -> None:
        for cmd in commands:
            self.register(cmd)

    def lookup(self, intent: str) -> Optional[CommandDef]:
        """Return CommandDef for a given intent name or None."""
        return self._by_name.get(intent)

    def lookup_alias(self, alias: str) -> Optional[CommandDef]:
        """Return CommandDef for a raw alias string or None."""
        name = self._alias_map.get(alias.lower().strip())
        if name:
            return self._by_name.get(name)
        return None

    def all_commands(self) -> list[CommandDef]:
        return list(self._by_name.values())

    def commands_by_category(self) -> dict[str, list[CommandDef]]:
        result: dict[str, list[CommandDef]] = {}
        for cmd in self._by_name.values():
            result.setdefault(cmd.category, []).append(cmd)
        return dict(sorted(result.items()))

    def __len__(self) -> int:
        return len(self._by_name)


def make_command(
    name: str,
    handler: Callable[..., str],
    description: str,
    aliases: Optional[list[str]] = None,
    permission: PermissionLevel = PermissionLevel.SAFE,
    category: str = "General",
    args_help: str = "",
) -> CommandDef:
    """Convenience factory for CommandDef."""
    return CommandDef(
        name=name,
        handler=handler,
        description=description,
        permission=permission,
        category=category,
        aliases=aliases or [],
        args_help=args_help,
    )
