# 🤖 Dot Assistant

An interactive, feature-packed desktop Python Assistant named **Dot**. It features full speech recognition, text-to-speech output, fallback console text-input, system control capabilities, media player features, web integrations, and task productivity utilities.

---

## 🌟 Key Features

### 🗣 Voice & Conversational AI
- **Text-to-Speech (TTS):** Powered by `pyttsx3` (SAPI5 engine on Windows / espeak on Linux).
- **Speech Recognition:** Flexible audio capture via `sounddevice` or `speech_recognition` with Google Speech API integration.
- **Console Fallback:** Smooth fallback to text input when microphone input is not present or configured.
- **Voice Customization:** Switch voice profiles (male/female) and adjust speech rate dynamically.
- **Custom Wake Word:** Wake word set to `dot` by default.

### 💻 System Control & Diagnostics
- **PC Management:** Lock workstation, shutdown, restart, or cancel scheduled shutdowns.
- **System Diagnostics:** Monitor CPU load, RAM memory usage, battery percentage, and running processes (`psutil`).
- **Network Stats:** Check IP configuration and connection status.
- **Screen Capture:** Instant desktop screenshot capture saved locally.

### 🎵 Media & Entertainment
- Local music player integration (scans configured music directory).
- YouTube video search & automated browser play.
- Online radio stream launcher.
- Jokes & trivia generator.

### 🛠 Productivity & Utilities
- **To-Do Manager:** Add, view, and persist daily tasks (`todos.json`).
- **Reminders & Alarms:** Set countdown timers and background reminder notifications.
- **Note Taking & File Search:** Quick note creation, directory navigation, and file reading aloud.
- **Web & Information:** Weather lookup via OpenWeatherMap API, Google web search, dictionary definitions, and unit conversion.

---

## 🏗 Project Architecture & Structure

```
VoiceAssistant/
├── DotAssistant.py                # Main assistant script
├── requirements.txt               # Python dependencies manifest
├── dot_config.example.json        # Configuration template (rename to dot_config.json)
├── .gitignore                     # Git ignore rules for cached, runtime, and secret files
└── README.md                      # Complete project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system.
- Microphone (optional, required for voice mode; falls back to text mode otherwise).

### 1. Clone the Repository

```bash
git clone https://github.com/I71gs/Dot-Voice-Assisstant-.git
cd Dot-Voice-Assisstant-
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙ Configuration

Create your local configuration file by copying `dot_config.example.json`:

```bash
# Windows PowerShell
copy dot_config.example.json dot_config.json

# Linux / macOS
cp dot_config.example.json dot_config.json
```

Edit `dot_config.json` with your credentials/preferences:

```json
{
  "language": "en-in",
  "wake_word": "dot",
  "music_dir": "C:\\Users\\YourUsername\\Music",
  "weather_api_key": "YOUR_OPENWEATHERMAP_API_KEY",
  "email_address": "your_email@gmail.com",
  "email_password": "your_app_password",
  "timezone": "UTC",
  "ai_enabled": false,
  "ai_model": "gemma3:4b",
  "ai_timeout": 15
}
```

Add these optional settings to enable local AI command translation via Ollama:

- `ai_enabled`: `false` to keep the existing deterministic command engine only; `true` to enable Gemma fallback.
- `ai_model`: the local Ollama model name, e.g. `gemma3:4b`.
- `ai_timeout`: timeout in seconds for the Ollama model call.

---

## 🖥 Usage

Run the main Dot Voice Assistant:

```bash
python DotAssistant.py
```

### Available Command Categories

| Category | Example Commands |
|---|---|
| **System Info** | `system info`, `network info`, `processes`, `screenshot` |
| **System Control** | `lock computer`, `shutdown`, `restart`, `cancel shutdown` |
| **Media** | `play music`, `play video`, `youtube python tutorial`, `radio` |
| **Productivity** | `add task`, `show tasks`, `take note`, `reminder`, `set alarm` |
| **Web & Info** | `weather`, `search python`, `define algorithm`, `open google.com` |
| **Settings** | `settings`, `voices`, `set wake word dot` |
| **Exit** | `exit`, `quit`, `bye` |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git checkout -b feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
