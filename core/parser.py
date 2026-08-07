"""
core/parser.py — DOT Assistant Command Parser

Converts raw user text into a structured ParsedCommand.
This is the ONLY place where text → intent mapping lives.
No business logic here — pure text analysis.

The ParsedCommand format is the Phase 2 contract:
    A future Gemma AI layer must produce the same ParsedCommand objects.
    The dispatcher is agnostic to source (human text OR AI output).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedCommand:
    """Structured representation of a user command."""
    intent: str                         # canonical intent, e.g. "create_file"
    arguments: dict = field(default_factory=dict)  # extracted args
    raw: str = ""                       # original text, preserved for logging

    def to_dict(self) -> dict:
        return {"intent": self.intent, "arguments": self.arguments, "raw": self.raw}


@dataclass
class _Rule:
    """A single regex rule that maps to an intent."""
    pattern: re.Pattern
    intent: str
    arg_groups: list[str] = field(default_factory=list)  # named capture groups


class Parser:
    def __init__(self) -> None:
        self._rules: list[_Rule] = _build_rules()

    def parse(self, text: str) -> ParsedCommand:
        text = text.strip()
        lower = text.lower()

        for rule in self._rules:
            m = rule.pattern.match(lower)
            if m:
                args = {}
                for group in rule.arg_groups:
                    val = m.group(group)
                    if val is not None:
                        args[group] = val.strip()
                return ParsedCommand(intent=rule.intent, arguments=args, raw=text)

        return ParsedCommand(intent="unknown", arguments={}, raw=text)


def _r(pattern: str, intent: str, groups: Optional[list[str]] = None) -> _Rule:
    return _Rule(
        pattern=re.compile(pattern, re.IGNORECASE),
        intent=intent,
        arg_groups=groups or [],
    )


def _build_rules() -> list[_Rule]:
    return [
        _r(r"^(exit|quit|bye|goodbye)$", "exit"),
        _r(r"^help\s+(?P<category>\w+)$", "help_category", ["category"]),
        _r(r"^help$", "help"),
        _r(r"^(what('s| is) the time|time|current time|show time)$", "get_time"),
        _r(r"^(what('s| is) the date|date|today|current date)$", "get_date"),
        _r(
            r"^(remind me|set reminder|add reminder)\s+(?P<message>.+)\s+in\s+(?P<delay>\d+)\s+(?P<unit>minute|minutes|hour|hours|second|seconds)$",
            "add_reminder",
            ["message", "delay", "unit"],
        ),
        _r(
            r"^(remind me|set reminder|add reminder)\s+in\s+(?P<delay>\d+)\s+(?P<unit>minute|minutes|hour|hours|second|seconds)\s+(?P<message>.+)$",
            "add_reminder",
            ["message", "delay", "unit"],
        ),
        _r(
            r"^(remind me|set reminder|add reminder)\s+in\s+(?P<delay>\d+)\s+(?P<unit>minute|minutes|hour|hours|second|seconds)$",
            "add_reminder_simple",
            ["delay", "unit"],
        ),
        _r(r"^(list reminders|show reminders|my reminders)$", "list_reminders"),
        _r(r"^delete reminder\s+(?P<index>\d+)$", "delete_reminder", ["index"]),
        _r(r"^(create|make|new) (file|document)\s+(?P<filename>\S+)$", "create_file", ["filename"]),
        _r(r"^(create|make|new) (file|document)$", "create_file_prompt"),
        _r(r"^(read|open|show|view|print) file\s+(?P<filename>.+)$", "read_file", ["filename"]),
        _r(r"^(update|write|edit) file\s+(?P<filename>\S+)$", "update_file", ["filename"]),
        _r(r"^(append|add to) file\s+(?P<filename>\S+)\s+(?P<content>.+)$", "append_file", ["filename", "content"]),
        _r(
            r"^(rename|move) file\s+(?P<source>\S+)\s+(to|as)\s+(?P<destination>\S+)$",
            "rename_file",
            ["source", "destination"],
        ),
        _r(
            r"^(delete|remove) file\s+(?P<filename>.+)$",
            "delete_file",
            ["filename"],
        ),
        _r(r"^(copy) file\s+(?P<source>\S+)\s+(to)\s+(?P<destination>\S+)$", "copy_file", ["source", "destination"]),
        _r(r"^(create|make|new) (folder|directory|dir)\s+(?P<path>.+)$", "create_folder", ["path"]),
        _r(r"^(delete|remove) (folder|directory|dir)\s+(?P<path>.+)$", "delete_folder", ["path"]),
        _r(r"^(move) file\s+(?P<source>\S+)\s+(to)\s+(?P<destination>.+)$", "move_file", ["source", "destination"]),
        _r(r"^(list|ls|dir|show) files?(\s+(?P<path>.+))?$", "list_files", ["path"]),
        _r(r"^(recent files?|recently (modified|changed))(\s+(?P<path>.+))?$", "recent_files", ["path"]),
        _r(r"^(search|find) (files?|for)\s+(?P<pattern>.+)$", "search_files", ["pattern"]),
        _r(r"^(open folder|open dir(ectory)?)\s+(?P<path>.+)$", "open_folder", ["path"]),
        _r(r"^(go to|cd|navigate to?)\s+(?P<path>.+)$", "navigate_to", ["path"]),
        _r(r"^(file info|info(rmation)? (of|for|about)?)\s+(?P<path>.+)$", "file_info", ["path"]),
        _r(r"^(system info(rmation)?|sysinfo|sys info)$", "system_info"),
        _r(r"^(cpu|cpu usage|cpu load)$", "cpu_usage"),
        _r(r"^(ram|ram usage|memory|memory usage)$", "ram_usage"),
        _r(r"^(disk|disk usage|disk space|storage)(\s+(?P<path>.+))?$", "disk_usage", ["path"]),
        _r(r"^(battery|battery status|battery level)$", "battery_status"),
        _r(r"^(network info(rmation)?|net info|netinfo)$", "network_info"),
        _r(r"^(processes|running processes|list processes|ps)$", "running_processes"),
        _r(r"^(shutdown|power off|poweroff|turn off)(\s+in\s+(?P<delay>\d+))?$", "shutdown", ["delay"]),
        _r(r"^(restart|reboot)(\s+in\s+(?P<delay>\d+))?$", "restart", ["delay"]),
        _r(r"^cancel (shutdown|restart|reboot)$", "cancel_shutdown"),
        _r(r"^(lock|lock computer|lock screen|lock pc)$", "lock_computer"),
        _r(r"^(sleep|hibernate|suspend)$", "sleep"),
        _r(r"^(brightness)\s+(?P<level>\d+)$", "set_brightness", ["level"]),
        _r(r"^(open|launch|start)\s+(?P<app>.+)$", "open_app", ["app"]),
        _r(r"^(close|kill) (app|application|window)(\s+(?P<app>.+))?$", "close_app", ["app"]),
        _r(r"^(minimize|minimise)( (all|windows))?$", "minimize_windows"),
        _r(r"^(show desktop|desktop)$", "show_desktop"),
        _r(r"^(list (apps|applications)|running apps)$", "list_running_apps"),
        _r(r"^(terminate|force (close|kill))\s+(?P<app>.+)$", "terminate_app", ["app"]),
        _r(r"^(set volume|volume)\s+(?P<level>\d+)$", "set_volume", ["level"]),
        _r(r"^(volume up|vol up|increase volume)(\s+(?P<step>\d+))?$", "volume_up", ["step"]),
        _r(r"^(volume down|vol down|decrease volume)(\s+(?P<step>\d+))?$", "volume_down", ["step"]),
        _r(r"^(mute|silence)$", "mute"),
        _r(r"^(unmute|restore volume|unsilence)$", "unmute"),
        _r(r"^(play music|music)(\s+(?P<path>.+))?$", "play_music", ["path"]),
        _r(r"^(play video|video)(\s+(?P<path>.+))?$", "play_video", ["path"]),
        _r(r"^(spotify|open spotify|play spotify)$", "open_spotify"),
        _r(r"^(youtube|yt)\s+(?P<query>.+)$", "youtube_search", ["query"]),
        _r(r"^(radio|play radio|online radio)$", "play_radio"),
        _r(r"^(search|google|look up|find)\s+(?P<query>.+)$", "google_search", ["query"]),
        _r(r"^(open website|open site|go to|visit)\s+(?P<url>.+)$", "open_website", ["url"]),
        _r(r"^(open url|url|navigate to)\s+(?P<url>https?://.+)$", "open_url", ["url"]),
        _r(r"^(get clipboard|show clipboard|clipboard|paste)$", "get_clipboard"),
        _r(r"^(copy|set clipboard)\s+(?P<text>.+)$", "set_clipboard", ["text"]),
        _r(r"^(clear clipboard)$", "clear_clipboard"),
        _r(r"^(screenshot|take screenshot|capture screen|snap)$", "take_screenshot"),
        _r(r"^(open (last|latest) screenshot)$", "open_latest_screenshot"),
        _r(r"^(add task|add todo|new task)\s+(?P<task>.+)$", "add_todo", ["task"]),
        _r(r"^(add task|add todo|new task)$", "add_todo_prompt"),
        _r(r"^(list tasks|show tasks|my tasks|todos?|list todos?)$", "list_todos"),
        _r(r"^(complete|done|finish) (task|todo)\s+(?P<index>\d+)$", "complete_todo", ["index"]),
        _r(r"^(remove|delete) (task|todo)\s+(?P<index>\d+)$", "remove_todo", ["index"]),
        _r(r"^(note|take note|add note)\s+(?P<text>.+)$", "create_note", ["text"]),
        _r(r"^(note|take note|add note)$", "create_note_prompt"),
        _r(r"^(read notes?|show notes?|my notes?)(\s+(?P<count>\d+))?$", "read_notes", ["count"]),
        _r(r"^(history|command history|show history)(\s+(?P<count>\d+))?$", "show_history", ["count"]),
        _r(r"^(weather)(\s+(?P<city>.+))?$", "get_weather", ["city"]),
        _r(r"^(define|definition|meaning of?|what (is|does))\s+(?P<word>\S+)$", "define_word", ["word"]),
        _r(r"^(trivia|fun fact|fact)$", "tell_trivia"),
        _r(
            r"^(convert)\s+(?P<value>[\d.]+)\s+(?P<from_unit>\w+)\s+(to|in)\s+(?P<to_unit>\w+)$",
            "convert_units",
            ["value", "from_unit", "to_unit"],
        ),
        _r(r"^(calculate|calc|math|compute|=)\s+(?P<expression>.+)$", "calculate", ["expression"]),
        _r(r"^(joke|tell (me )?(a )?joke)$", "tell_joke"),
        _r(r"^(settings|config|configuration|show settings?)$", "show_settings"),
        _r(r"^(settings? menu|configure|interactive settings?)$", "settings_menu"),
        _r(r"^(toggle tts|toggle (voice|speech) output|tts)$", "toggle_tts"),
        _r(r"^(toggle genz|toggle gen z|genz slangs?)$", "toggle_genz"),
        _r(r"^(toggle dark jokes?|dark jokes?)$", "toggle_dark_jokes"),
        _r(r"^(set (weather )?api key)\s+(?P<key>.+)$", "set_api_key", ["key"]),
        _r(r"^(run command|cmd|exec)\s+(?P<command>.+)$", "run_command", ["command"]),
        _r(r"^(hello|hi|hey|good morning|good afternoon|good evening)$", "greet"),
        _r(r"^(how are you|how('s| is) it going|what('s| is) up)$", "how_are_you"),
        _r(r"^(who are you|what is your name|your name)$", "who_are_you"),
        _r(r"^(what can you do|capabilities|commands)$", "capabilities"),
        _r(r"^(thank(s| you)|cheers)$", "thank_you"),
    ]
