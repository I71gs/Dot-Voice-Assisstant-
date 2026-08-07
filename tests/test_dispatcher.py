"""
tests/test_dispatcher.py — Unit tests for Dispatcher & Command Registry
"""

from __future__ import annotations

import pytest
from core.command_registry import CommandRegistry, make_command
from core.context import Context
from core.dispatcher import Dispatcher
from core.parser import ParsedCommand
from core.permissions import PermissionLevel


def test_dispatcher_success():
    registry = CommandRegistry()
    context = Context()

    def dummy_handler(val: str) -> str:
        return f"value was {val}"

    registry.register(make_command("dummy", dummy_handler, "Dummy command", aliases=["dum"]))
    dispatcher = Dispatcher(registry, context)

    res = dispatcher.dispatch(ParsedCommand(intent="dummy", arguments={"val": "test"}))
    assert res == "value was test"

    res = dispatcher.dispatch(ParsedCommand(intent="unknown"))
    assert "not recognized" in res


def test_dispatcher_error_handling():
    registry = CommandRegistry()
    context = Context()

    def buggy_handler() -> str:
        raise ValueError("buggy code")

    registry.register(make_command("buggy", buggy_handler, "Buggy command"))
    dispatcher = Dispatcher(registry, context)

    res = dispatcher.dispatch(ParsedCommand(intent="buggy"))
    assert res.startswith("✗ Error:")
    assert "buggy code" in res
