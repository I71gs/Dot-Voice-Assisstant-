"""
modules/browser.py — DOT Browser Module

Web search, URL opening, and common website shortcuts.
"""

from __future__ import annotations

import webbrowser

from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger

log = get_logger("browser")

SHORTCUTS: dict[str, str] = {
    "google": "https://google.com",
    "github": "https://github.com",
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://wikipedia.org",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "amazon": "https://amazon.com",
}


def google_search(query: str, **_) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    log.info("Google search: %s", query)
    return f"✓ Searching Google for: {query}"


def youtube_search(query: str, **_) -> str:
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"✓ Searching YouTube for: {query}"


def open_website(url: str, **_) -> str:
    url_lower = url.lower().strip().rstrip("/")
    if url_lower in SHORTCUTS:
        target = SHORTCUTS[url_lower]
    else:
        target = url if url.startswith("http") else f"https://{url}"
    webbrowser.open(target)
    log.info("Opened URL: %s", target)
    return f"✓ Opening: {target}"


def open_url(url: str, **_) -> str:
    return open_website(url)


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("google_search", google_search, "Search Google",
                     aliases=["search", "google", "look up", "find"],
                     args_help="<query>", category="Browser"),
        make_command("youtube_search", youtube_search, "Search YouTube",
                     aliases=["youtube search"],
                     args_help="<query>", category="Browser"),
        make_command("open_website", open_website, "Open a website or URL",
                     aliases=["open website", "open site", "visit", "go to"],
                     args_help="<url>", category="Browser"),
        make_command("open_url", open_url, "Open a URL directly",
                     aliases=["open url", "url"],
                     args_help="<url>", category="Browser"),
    ])
