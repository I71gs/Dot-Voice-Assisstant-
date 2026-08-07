"""
tests/test_parser.py — Unit tests for Parser
"""

from __future__ import annotations

import pytest
from core.parser import Parser


def test_basic_intents():
    parser = Parser()

    p = parser.parse("what is the time")
    assert p.intent == "get_time"

    p = parser.parse("date")
    assert p.intent == "get_date"

    p = parser.parse("exit")
    assert p.intent == "exit"


def test_command_with_arguments():
    parser = Parser()

    p = parser.parse("create file note.txt")
    assert p.intent == "create_file"
    assert p.arguments == {"filename": "note.txt"}

    p = parser.parse("rename file old.txt to new.txt")
    assert p.intent == "rename_file"
    assert p.arguments == {"source": "old.txt", "destination": "new.txt"}

    p = parser.parse("open chrome")
    assert p.intent == "open_app"
    assert p.arguments == {"app": "chrome"}


def test_reminders_parsing():
    parser = Parser()

    p = parser.parse("remind me buy groceries in 10 minutes")
    assert p.intent == "add_reminder"
    assert p.arguments == {"message": "buy groceries", "delay": "10", "unit": "minutes"}


def test_unknown_commands():
    parser = Parser()

    p = parser.parse("random gibberish that does not match rules")
    assert p.intent == "unknown"
    assert p.arguments == {}
