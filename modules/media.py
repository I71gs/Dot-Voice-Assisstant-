"""
modules/media.py — DOT Media Module

Volume control, music/video playback, Spotify, YouTube, radio.
"""

from __future__ import annotations

import os
import random
import webbrowser
from pathlib import Path
from typing import Optional

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger

log = get_logger("media")


def _try_pycaw_set(level: int) -> bool:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level / 100.0)), None)
        return True
    except Exception:
        return False


def _try_pycaw_get() -> Optional[int]:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return None


def _try_pycaw_mute(mute: bool) -> bool:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1 if mute else 0, None)
        return True
    except Exception:
        return False


def set_volume(level: str, **_) -> str:
    try:
        lvl = int(level)
        if not (0 <= lvl <= 100):
            return "✗ Volume must be between 0 and 100."
        if _try_pycaw_set(lvl):
            return f"✓ Volume set to {lvl}%"
        os.system(f"nircmd setsysvolume {int(lvl * 655.35)}")
        return f"✓ Volume set to {lvl}% (via fallback)"
    except Exception as e:
        return f"✗ Volume error: {e}"


def volume_up(step: Optional[str] = None, **_) -> str:
    s = int(step) if step and str(step).isdigit() else 10
    current = _try_pycaw_get()
    if current is not None:
        return set_volume(str(min(100, current + s)))
    try:
        os.system(f"nircmd changesysvolume {int(s * 655.35)}")
        return f"✓ Volume increased by {s}%"
    except Exception as e:
        return f"✗ Volume error: {e}"


def volume_down(step: Optional[str] = None, **_) -> str:
    s = int(step) if step and str(step).isdigit() else 10
    current = _try_pycaw_get()
    if current is not None:
        return set_volume(str(max(0, current - s)))
    try:
        os.system(f"nircmd changesysvolume -{int(s * 655.35)}")
        return f"✓ Volume decreased by {s}%"
    except Exception as e:
        return f"✗ Volume error: {e}"


def mute(**_) -> str:
    if _try_pycaw_mute(True):
        return "✓ Muted."
    try:
        os.system("nircmd mutesysvolume 1")
        return "✓ Muted."
    except Exception as e:
        return f"✗ Mute error: {e}"


def unmute(**_) -> str:
    if _try_pycaw_mute(False):
        return "✓ Unmuted."
    try:
        os.system("nircmd mutesysvolume 0")
        return "✓ Unmuted."
    except Exception as e:
        return f"✗ Unmute error: {e}"


def play_music(path: Optional[str] = None, **_) -> str:
    settings = cfg.load_settings()
    music_dir = path or settings.get("music_dir", "")
    if not music_dir:
        return "✗ Music directory not configured. Use 'settings menu' to set it."
    p = Path(music_dir)
    if not p.exists():
        return f"✗ Music directory not found: {music_dir}"
    songs = [f for f in p.iterdir() if f.suffix.lower() in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}]
    if not songs:
        return f"✗ No music files found in: {music_dir}"
    song = random.choice(songs)
    try:
        os.startfile(str(song))
        log.info("Playing music: %s", song.name)
        return f"✓ Now playing: {song.name}"
    except OSError as e:
        return f"✗ Could not play music: {e}"


def play_video(path: Optional[str] = None, **_) -> str:
    settings = cfg.load_settings()
    if path:
        p = Path(path)
        if not p.exists():
            return f"✗ File not found: {path}"
        try:
            os.startfile(str(p))
            return f"✓ Playing: {p.name}"
        except OSError as e:
            return f"✗ Could not play: {e}"

    video_dir = Path(settings.get("video_dir", ""))
    if not video_dir.exists():
        return f"✗ Video directory not found: {video_dir}"
    videos = [f for f in video_dir.iterdir() if f.suffix.lower() in {".mp4", ".avi", ".mkv", ".mov", ".wmv"}]
    if not videos:
        return f"✗ No video files found in: {video_dir}"
    vid = random.choice(videos)
    try:
        os.startfile(str(vid))
        return f"✓ Playing: {vid.name}"
    except OSError as e:
        return f"✗ Could not play video: {e}"


def open_spotify(**_) -> str:
    try:
        os.startfile("spotify:")
        return "✓ Opening Spotify..."
    except OSError:
        webbrowser.open("https://open.spotify.com")
        return "✓ Opening Spotify Web Player..."


def youtube_search(query: str, **_) -> str:
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"✓ Searching YouTube for: {query}"


def play_radio(**_) -> str:
    webbrowser.open("https://www.radio.net")
    return "✓ Opening radio in browser..."


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("set_volume", set_volume, "Set system volume (0-100)",
                     aliases=["set volume", "volume"],
                     args_help="<level>", category="Media"),
        make_command("volume_up", volume_up, "Increase volume",
                     aliases=["volume up", "vol up"],
                     args_help="[step]", category="Media"),
        make_command("volume_down", volume_down, "Decrease volume",
                     aliases=["volume down", "vol down"],
                     args_help="[step]", category="Media"),
        make_command("mute", mute, "Mute system audio",
                     aliases=["silence"], category="Media"),
        make_command("unmute", unmute, "Unmute system audio",
                     aliases=["restore volume"], category="Media"),
        make_command("play_music", play_music, "Play random music from music directory",
                     aliases=["play music", "music"],
                     args_help="[path]", category="Media"),
        make_command("play_video", play_video, "Play a video file",
                     aliases=["play video", "video"],
                     args_help="[path]", category="Media"),
        make_command("open_spotify", open_spotify, "Open Spotify",
                     aliases=["spotify", "play spotify"],
                     category="Media"),
        make_command("youtube_search", youtube_search, "Search YouTube",
                     aliases=["youtube", "yt"],
                     args_help="<query>", category="Media"),
        make_command("play_radio", play_radio, "Open online radio",
                     aliases=["radio", "online radio"],
                     category="Media"),
    ])
