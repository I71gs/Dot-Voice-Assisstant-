# DOT - Desktop Operations Terminal

> A modular, deterministic, text-based Windows desktop assistant.
> **Phase 1** - No AI. Pure regex-based command parsing.

---

## Overview

DOT is a lightweight, fully offline Windows desktop assistant you run in your terminal.
It understands plain-English commands for system control, file management, media, productivity, browsing, and more - without any AI or cloud dependency.

```
DOT > time
22:31:04  -  Thursday, August 07, 2026

DOT > system info
SYSTEM INFORMATION
----------------------------------------
  CPU Usage   : 12.3%
  RAM Usage   : 58.1%  (9.3 / 16.0 GB)
  Disk Usage  : 74.2%  (371.0 / 500.0 GB)
  Battery     : 88%  Plugged in

DOT > remind me take a break in 30 minutes
Reminder set: "take a break" in 30 minutes
```

---

## Project Structure

```
VoiceAssistant/
├── main.py                     # Entry point - starts the REPL
├── config.py                   # Central settings loader/saver
├── dot_config.example.json     # User config template
├── requirements.txt
├── README.md
│
├── core/                       # Framework (no business logic)
│   ├── assistant.py            # Orchestrator: REPL, banner, TTS
│   ├── parser.py               # Text -> ParsedCommand (regex rules)
│   ├── dispatcher.py           # ParsedCommand -> handler dispatch
│   ├── command_registry.py     # Command registration & category index
│   ├── context.py              # Per-session state (cwd, confirmation)
│   ├── permissions.py          # SAFE / CONFIRM / DANGEROUS levels
│   ├── scheduler.py            # Background thread for reminders
│   └── logger.py               # Rotating file logger -> logs/dot.log
│
├── modules/                    # Feature modules
│   ├── system.py               # CPU, RAM, disk, battery, power, lock
│   ├── files.py                # Create, read, update, copy, move, delete
│   ├── apps.py                 # Open, close, list, terminate apps
│   ├── media.py                # Volume, music, video, Spotify, YouTube
│   ├── browser.py              # Google search, open URL
│   ├── clipboard.py            # Get, set, clear clipboard
│   ├── screenshots.py          # Capture and open screenshots
│   └── reminders.py            # Timed reminders with background scheduler
│
├── services/                   # Shared singleton services
│   ├── notifications.py        # Windows toast notifications (plyer)
│   └── scheduler_service.py    # Global scheduler singleton
│
├── data/                       # Runtime data (auto-created, gitignored)
│   ├── settings.json           # Your personal settings
│   ├── reminders.json          # Saved reminders
│   └── notes.txt               # Personal notes
│
├── logs/
│   └── dot.log
│
└── tests/
    ├── test_parser.py
    └── test_dispatcher.py
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/I71gs/Dot-Assisstant.git
cd Dot-Assisstant
```

### 2. Virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure

```bash
copy dot_config.example.json data\settings.json
# Edit data\settings.json with your music_dir, weather_api_key, etc.
```

DOT auto-creates `data/settings.json` with defaults on first run.

### 5. Run

```bash
python main.py
```

---

## Command Reference

### Time & Date
| Command | Aliases |
|---|---|
| `time` | `what is the time`, `current time` |
| `date` | `today`, `what is the date` |

### System
| Command | Example / Aliases |
|---|---|
| `system info` | `sysinfo`, `sys info` |
| `cpu` | `cpu usage`, `cpu load` |
| `ram` | `memory`, `ram usage` |
| `disk [path]` | `disk C:\`, `storage` |
| `battery` | `battery status` |
| `network info` | `net info`, `netinfo` |
| `processes` | `ps`, `running processes` |
| `lock` | `lock screen`, `lock computer` |
| `sleep` | `hibernate` |
| `brightness <0-100>` | `brightness 70` |
| `shutdown [in N]` | `shutdown in 60` |
| `restart [in N]` | `reboot` |
| `cancel shutdown` | - |

### Files
| Command | Example |
|---|---|
| `create file <name>` | `new file notes.txt` |
| `read file <name>` | `open file report.md` |
| `update file <name>` | `edit file todo.txt` |
| `append file <name> <text>` | `append file log.txt done` |
| `rename file <src> to <dst>` | `rename file a.txt to b.txt` |
| `copy file <src> to <dst>` | - |
| `move file <src> to <dst>` | - |
| `delete file <name>` | - |
| `list files [path]` | `ls`, `dir` |
| `recent files` | - |
| `search files <pattern>` | `find files *.py` |
| `file info <path>` | - |
| `create folder <path>` | `new directory backup` |
| `delete folder <path>` | - |
| `open folder <path>` | - |

### Applications
| Command | Example |
|---|---|
| `open <app>` | `open chrome` |
| `close app [name]` | `close app notepad` |
| `terminate <app>` | `force kill chrome` |
| `minimize all` | - |
| `show desktop` | - |
| `running apps` | `list applications` |

Configurable app paths via `app_paths` in `data/settings.json`.

### Media
| Command | Example |
|---|---|
| `volume <0-100>` | `set volume 50` |
| `volume up [step]` | `vol up 20` |
| `volume down [step]` | `vol down` |
| `mute` / `unmute` | - |
| `play music [path]` | `music` |
| `play video [path]` | `video` |
| `spotify` | `open spotify` |
| `youtube <query>` | `yt lo-fi beats` |
| `radio` | `play radio` |

Volume control uses `pycaw` (Windows native), with `nircmd` fallback.

### Browser
| Command | Example |
|---|---|
| `search <query>` | `google Python tutorials` |
| `open website <url>` | `visit github.com` |
| `open url <https://...>` | - |

### Clipboard
| Command | Example |
|---|---|
| `clipboard` | `get clipboard` |
| `copy <text>` | `set clipboard hello` |
| `clear clipboard` | - |

### Screenshots
| Command | Example |
|---|---|
| `screenshot` | `snap`, `capture screen` |
| `open last screenshot` | - |

### Reminders
| Command | Example |
|---|---|
| `remind me <msg> in <N> minutes` | `remind me drink water in 20 minutes` |
| `remind me in <N> hours <msg>` | `remind me in 1 hour take meds` |
| `list reminders` | `my reminders` |
| `delete reminder <index>` | - |

### Settings
| Command | Description |
|---|---|
| `settings` | Show current settings table |
| `settings menu` | Interactive settings editor |
| `toggle tts` | Enable/disable text-to-speech |
| `toggle genz` | Toggle Gen Z slang responses |
| `toggle dark jokes` | Toggle dark jokes |

### Conversation
| Command | Aliases |
|---|---|
| `hello` | `hi`, `hey` |
| `how are you` | - |
| `who are you` | - |
| `help` | `commands`, `?` |
| `help <category>` | `help Media`, `help System` |
| `exit` | `quit`, `bye`, `goodbye` |

---

## Configuration

Settings live in `data/settings.json` (auto-created on first run).

| Key | Default | Description |
|---|---|---|
| `assistant_name` | `"DOT"` | Display name |
| `tts_enabled` | `false` | Text-to-speech (pyttsx3 / SAPI5) |
| `music_dir` | `~/Music` | Music directory |
| `video_dir` | `~/Videos` | Video directory |
| `screenshot_dir` | `<project>/screenshots` | Screenshot save path |
| `notes_file` | `data/notes.txt` | Notes storage |
| `weather_api_key` | `""` | OpenWeatherMap API key |
| `genz_slangs` | `true` | Gen Z style responses |
| `dark_jokes` | `true` | Dark joke toggle |
| `max_history` | `200` | Command history limit |
| `app_paths` | `{...}` | Custom app executable paths |

---

## Architecture

```
User Input (text)
      |
      v
  core/parser.py       <- regex rules -> ParsedCommand { intent, args, raw }
      |
      v
  core/dispatcher.py   <- looks up intent in CommandRegistry -> calls handler
      |
      v
  modules/*.py         <- handler function returns str result
      |
      v
  core/assistant.py    <- prints result (rich-coloured), optionally speaks it
```

**Key design decisions:**
- `parser.py` is the **only** place where `text -> intent` mapping lives
- `dispatcher.py` is **source-agnostic** - Phase 2 AI plugs in here by producing the same `ParsedCommand` objects
- Permission levels gate all destructive operations before execution

---

## Permission System

| Level | Behaviour | Used for |
|---|---|---|
| `SAFE` | Executes immediately | All info/read ops |
| `CONFIRM` | Prompts `Are you sure? (y/n)` | Sleep, file delete |
| `DANGEROUS` | Red warning prompt | Shutdown, restart, shell exec |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `rich` | Terminal UI, tables, panels |
| `psutil` | CPU, RAM, disk, battery, processes |
| `requests` | Network info, weather API |
| `Pillow` | Screenshots |
| `pyperclip` | Clipboard access |
| `plyer` | Windows toast notifications |
| `pywin32` | Windows API integration |
| `pycaw` | Windows audio volume control |
| `pyttsx3` | Optional TTS (disabled by default) |
| `pytest` | Unit testing |

---

## Roadmap

- [x] Phase 1 - Modular text-based deterministic assistant
- [ ] Phase 2 - AI integration (local LLM via Ollama / Gemma)
- [ ] Phase 3 - GUI / system tray mode
- [ ] Phase 4 - Plugin system

---

## License

MIT - see [LICENSE](LICENSE).
