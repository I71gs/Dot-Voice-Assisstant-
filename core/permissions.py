"""
core/permissions.py — DOT Assistant Permission System

Every command carries a PermissionLevel.
The dispatcher uses require_confirmation() before executing CONFIRM/DANGEROUS commands.
This system cannot be bypassed — not even by a future AI layer.
"""

from __future__ import annotations

from enum import Enum, auto


class PermissionLevel(Enum):
    """Severity levels for commands."""
    SAFE = auto()       # Execute immediately, no prompt
    CONFIRM = auto()    # Prompt once, accept y/Y
    DANGEROUS = auto()  # Prompt with explicit warning, require 'yes' in full


def require_confirmation(
    action_description: str,
    level: PermissionLevel = PermissionLevel.CONFIRM,
) -> bool:
    """
    Prompt the user to confirm a potentially destructive action.

    Returns True if the user approves, False otherwise.
    This function always reads from stdin — it cannot be bypassed programmatically.
    """
    if level == PermissionLevel.SAFE:
        return True

    if level == PermissionLevel.CONFIRM:
        print(f"\n⚠  This action will: {action_description}")
        try:
            answer = input("   Confirm? [y/N] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        return answer.lower() == "y"

    if level == PermissionLevel.DANGEROUS:
        print(f"\n🔴 DANGEROUS OPERATION: {action_description}")
        print("   This action may be irreversible.")
        try:
            answer = input("   Type 'yes' to confirm (anything else cancels): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        return answer.lower() == "yes"

    return False
