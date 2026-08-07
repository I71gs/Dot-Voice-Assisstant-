"""
core/context.py — DOT Assistant Runtime Context

Lightweight, in-memory session state. Not a memory or AI system.
One Context instance lives for the lifetime of a session.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Context:
    """Holds transient runtime information for a single DOT session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    cwd: Path = field(default_factory=Path.cwd)
    last_command: str = ""
    last_result: str = ""
    pending_confirmation: Optional[str] = None  # description of pending action
    extra: dict[str, Any] = field(default_factory=dict)

    def update_cwd(self, path: Path) -> None:
        self.cwd = path.resolve()

    def record(self, command: str, result: str) -> None:
        self.last_command = command
        self.last_result = result

    def set_pending(self, description: str) -> None:
        self.pending_confirmation = description

    def clear_pending(self) -> None:
        self.pending_confirmation = None

    def has_pending(self) -> bool:
        return self.pending_confirmation is not None
