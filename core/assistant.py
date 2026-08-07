"""
core/assistant.py — DOT Assistant Orchestrator
"""

from __future__ import annotations

import datetime
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

import config as cfg
from core.command_registry import CommandRegistry
from core.context import Context
from core.dispatcher import Dispatcher
from core.logger import get_logger
from core.parser import Parser
from core.scheduler import Scheduler

log = get_logger("assistant")
console = Console()


class Assistant:
    def __init__(self) -> None:
        self.settings = cfg.load_settings()
        self.name: str = self.settings.get("assistant_name", "DOT")
        self.registry = CommandRegistry()
        self.context = Context()
        self.parser = Parser()
        self.scheduler = Scheduler()
        self.dispatcher: Optional[Dispatcher] = None
        self._tts_engine = None
        self._tts_enabled = False

    def initialize(self) -> None:
        self.settings = cfg.load_settings()
        self._tts_enabled = self.settings.get("tts_enabled", False)

        if self._tts_enabled:
            self._init_tts()

        self._register_all_commands()
        self.dispatcher = Dispatcher(self.registry, self.context)
        log.info("DOT initialized — %d commands registered", len(self.registry))

    def _init_tts(self) -> None:
        try:
            import pyttsx3
            self._tts_engine = pyttsx3.init("sapi5")
            voices = self._tts_engine.getProperty("voices")
            if voices:
                self._tts_engine.setProperty("voice", voices[0].id)
            self._tts_engine.setProperty("rate", 150)
            log.info("TTS engine initialized")
        except Exception as exc:
            log.warning("TTS init failed (%s) — TTS disabled", exc)
            self._tts_engine = None
            self._tts_enabled = False

    def _register_all_commands(self) -> None:
        from modules import (
            apps, automation, browser, clipboard,
            files, information, media, productivity,
            reminders, screenshots, system,
        )

        modules = [
            files, apps, system, media, browser,
            clipboard, screenshots, reminders,
            productivity, information, automation,
        ]

        for mod in modules:
            if hasattr(mod, "register_commands"):
                mod.register_commands(self.registry, self.scheduler)
            else:
                log.warning("Module %s has no register_commands()", mod.__name__)

        self._register_builtins()

    def _register_builtins(self) -> None:
        from core.command_registry import make_command
        from core.permissions import PermissionLevel

        self.registry.register_all([
            make_command("help", self._cmd_help, "Show all available commands", category="System",
                         aliases=["?", "commands", "what can you do"]),
            make_command("help_category", self._cmd_help_category, "Show commands in a category",
                         category="System", args_help="<category>"),
            make_command("exit", self._cmd_exit, "Exit DOT assistant", category="System",
                         aliases=["quit", "bye", "goodbye"]),
            make_command("get_time", self._cmd_time, "Show current time",
                         category="Time", aliases=["time", "current time"]),
            make_command("get_date", self._cmd_date, "Show current date",
                         category="Time", aliases=["date", "today"]),
            make_command("show_settings", self._cmd_settings, "Show current settings",
                         category="Settings", aliases=["settings", "config"]),
            make_command("settings_menu", self._cmd_settings_menu, "Interactive settings editor",
                         category="Settings"),
            make_command("toggle_tts", self._cmd_toggle_tts, "Toggle text-to-speech on/off",
                         category="Settings"),
            make_command("toggle_genz", self._cmd_toggle_genz, "Toggle Gen Z slang responses",
                         category="Settings"),
            make_command("toggle_dark_jokes", self._cmd_toggle_dark_jokes, "Toggle dark jokes",
                         category="Settings"),
            make_command("greet", self._cmd_greet, "Say hello", category="Conversation",
                         aliases=["hello", "hi", "hey"]),
            make_command("how_are_you", self._cmd_how_are_you, "Ask how DOT is doing",
                         category="Conversation"),
            make_command("who_are_you", self._cmd_who_are_you, "Learn about DOT",
                         category="Conversation"),
            make_command("thank_you", self._cmd_thank_you, "Express gratitude",
                         category="Conversation"),
            make_command("capabilities", self._cmd_capabilities, "What can DOT do?",
                         category="Conversation"),
        ])

    def run(self) -> None:
        self._print_banner()
        self._greet_by_time()

        while True:
            try:
                raw = self._prompt()
            except (EOFError, KeyboardInterrupt):
                console.print("\n")
                console.print("[bold green]Goodbye! Thanks for using DOT.[/]")
                break

            if not raw.strip():
                continue

            result = self.handle_input(raw)

            if result == "__EXIT__":
                console.print("[bold green]Goodbye! Thanks for using DOT.[/]")
                break

            if result:
                self._print_result(result)
                self._speak(result)

    def handle_input(self, text: str) -> str:
        from modules.productivity import save_command_history
        save_command_history(text)

        log.info("input: %s", text)
        parsed = self.parser.parse(text)
        log.info("parsed: intent=%s args=%s", parsed.intent, parsed.arguments)
        return self.dispatcher.dispatch(parsed)

    def _print_banner(self) -> None:
        settings = cfg.load_settings()
        tts_status = "ON" if settings.get("tts_enabled", False) else "OFF"

        panel = Panel(
            f"[bold cyan]System Status:[/] [green]ONLINE[/]\n"
            f"[bold cyan]Mode:[/]          [yellow]TEXT[/]\n"
            f"[bold cyan]TTS:[/]           [{'green' if tts_status == 'ON' else 'red'}]{tts_status}[/]\n\n"
            f"[dim]Type [bold]help[/bold] to see available commands.[/dim]",
            title=f"[bold magenta]  {self.name} ASSISTANT  [/]",
            border_style="bright_blue",
            expand=False,
            padding=(1, 4),
        )
        console.print()
        console.print(panel)
        console.print()

    def _greet_by_time(self) -> None:
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        msg = f"{greeting}! I'm {self.name}, your desktop assistant. How can I help?"
        console.print(f"[dim]{msg}[/dim]\n")
        self._speak(msg)

    def _prompt(self) -> str:
        console.print(f"[bold bright_blue]{self.name}[/] [bold white]>[/] ", end="")
        return input()

    def _print_result(self, result: str) -> None:
        if result.startswith("✓"):
            console.print(f"[bold green]{result}[/]")
        elif result.startswith("✗"):
            console.print(f"[bold red]{result}[/]")
        elif result.startswith("⚠") or result.startswith("!"):
            console.print(f"[bold yellow]{result}[/]")
        else:
            console.print(result)

    def _speak(self, text: str) -> None:
        if not self._tts_enabled or not self._tts_engine:
            return
        plain = text
        for tag in ["[bold green]", "[bold red]", "[bold yellow]", "[/]"]:
            plain = plain.replace(tag, "")
        try:
            self._tts_engine.say(plain[:300])
            self._tts_engine.runAndWait()
        except Exception as exc:
            log.debug("TTS speak error: %s", exc)

    def _cmd_help(self, **_) -> str:
        categories = self.registry.commands_by_category()
        table = Table(title="Available Commands", box=box.SIMPLE, show_header=True)
        table.add_column("Command / Aliases", style="cyan", no_wrap=False)
        table.add_column("Description", style="white")
        table.add_column("Category", style="dim")

        for cat, cmds in sorted(categories.items()):
            for c in sorted(cmds, key=lambda x: x.name):
                aliases = ", ".join(c.aliases[:2]) if c.aliases else ""
                cmd_display = c.name
                if c.args_help:
                    cmd_display += f"  {c.args_help}"
                if aliases:
                    cmd_display += f"\n[dim]({aliases})[/dim]"
                table.add_row(cmd_display, c.description, cat)

        console.print(table)
        return ""

    def _cmd_help_category(self, category: str = "", **_) -> str:
        all_cats = self.registry.commands_by_category()
        match = next(
            (k for k in all_cats if k.lower() == category.lower()), None
        )
        if not match:
            available = ", ".join(sorted(all_cats.keys()))
            return f"✗ Unknown category '{category}'. Available: {available}"
        cmds = all_cats[match]
        table = Table(title=f"Commands — {match}", box=box.SIMPLE)
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        for c in sorted(cmds, key=lambda x: x.name):
            table.add_row(c.name + (f"  {c.args_help}" if c.args_help else ""), c.description)
        console.print(table)
        return ""

    def _cmd_exit(self, **_) -> str:
        return "__EXIT__"

    def _cmd_time(self, **_) -> str:
        now = datetime.datetime.now()
        return f"🕐 {now.strftime('%H:%M:%S')}  —  {now.strftime('%A, %B %d, %Y')}"

    def _cmd_date(self, **_) -> str:
        return f"📅 {datetime.datetime.now().strftime('%A, %B %d, %Y')}"

    def _cmd_settings(self, **_) -> str:
        s = cfg.load_settings()
        table = Table(title="Current Settings", box=box.SIMPLE)
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        for k, v in s.items():
            if isinstance(v, dict):
                continue
            display = "••••••••" if ("password" in k or "key" in k.lower()) and v else str(v)
            table.add_row(k, display)
        console.print(table)
        return ""

    def _cmd_settings_menu(self, **_) -> str:
        s = cfg.load_settings()
        editable = [
            ("tts_enabled", "TTS (text-to-speech)"),
            ("genz_slangs", "Gen Z slang responses"),
            ("dark_jokes", "Dark jokes"),
            ("assistant_name", "Assistant name"),
            ("music_dir", "Music directory"),
            ("weather_api_key", "Weather API key"),
            ("email_address", "Email address"),
        ]
        while True:
            console.print("\n[bold cyan]SETTINGS MENU[/]")
            for i, (key, label) in enumerate(editable, 1):
                val = s.get(key, "")
                display = "••••••••" if ("password" in key or "key" in key.lower()) and val else val
                console.print(f"  [cyan]{i}.[/] {label:<30} : {display}")
            console.print("  [dim]0. Back[/dim]")
            try:
                choice = input("\nSelect number to edit (0 to exit): ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if choice == "0":
                break
            try:
                idx = int(choice) - 1
                key, label = editable[idx]
            except (ValueError, IndexError):
                console.print("[red]Invalid selection.[/]")
                continue
            try:
                current = s.get(key, "")
                if isinstance(current, bool):
                    s[key] = not current
                    console.print(f"[green]✓ {label} set to {s[key]}[/]")
                else:
                    new_val = input(f"New value for {label}: ").strip()
                    if new_val:
                        s[key] = new_val
                        console.print(f"[green]✓ {label} updated.[/]")
            except (EOFError, KeyboardInterrupt):
                break
            cfg.save_settings(s)
            self.settings = s
        return ""

    def _cmd_toggle_tts(self, **_) -> str:
        s = cfg.load_settings()
        s["tts_enabled"] = not s.get("tts_enabled", False)
        cfg.save_settings(s)
        self._tts_enabled = s["tts_enabled"]
        if self._tts_enabled and not self._tts_engine:
            self._init_tts()
        status = "enabled" if s["tts_enabled"] else "disabled"
        return f"✓ TTS {status}."

    def _cmd_toggle_genz(self, **_) -> str:
        s = cfg.load_settings()
        s["genz_slangs"] = not s.get("genz_slangs", True)
        cfg.save_settings(s)
        return f"✓ Gen Z slangs {'enabled' if s['genz_slangs'] else 'disabled'}."

    def _cmd_toggle_dark_jokes(self, **_) -> str:
        s = cfg.load_settings()
        s["dark_jokes"] = not s.get("dark_jokes", True)
        cfg.save_settings(s)
        return f"✓ Dark jokes {'enabled' if s['dark_jokes'] else 'disabled'}."

    def _cmd_greet(self, **_) -> str:
        return f"Hello! I'm {self.name}. How can I help you today?"

    def _cmd_how_are_you(self, **_) -> str:
        return "I'm running smoothly. All systems nominal. Ready to help!"

    def _cmd_who_are_you(self, **_) -> str:
        return (
            f"I'm {self.name}, your text-based desktop assistant. "
            "I can help with files, apps, system info, productivity, browsing, and more."
        )

    def _cmd_thank_you(self, **_) -> str:
        return "You're welcome. Always happy to help!"

    def _cmd_capabilities(self, **_) -> str:
        return self._cmd_help()
