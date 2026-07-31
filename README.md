# 🤖 JARVIS Voice Assistant V2

An interactive, feature-packed desktop Python Voice Assistant inspired by JARVIS. It features full speech recognition, text-to-speech output, fallback console text-input, system control capabilities, media player features, web integrations, and task productivity utilities.

---

## 🌟 Key Features

### 🗣 Voice & Conversational AI
- **Text-to-Speech (TTS):** Powered by `pyttsx3` (SAPI5 engine on Windows / espeak on Linux).
- **Speech Recognition:** Flexible audio capture via `sounddevice` or `speech_recognition` with Google Speech API integration.
- **Console Fallback:** Smooth fallback to text input when microphone input is not present or configured.
- **Voice Customization:** Switch voice profiles (male/female) and adjust speech rate dynamically.

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
├── JarvisV2_Complete.py      # Main complete voice assistant script (Recommended entry point)
├── JarvisV2.py               # Legacy / PyAudio version script
├── requirements.txt          # Python dependencies manifest
├── jarvis_config.example.json# Configuration template (rename to jarvis_config.json)
├── .gitignore                # Git ignore rules for cached, runtime, and secret files
└── README.md                 # Complete project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system.
- Microphone (optional, required for voice mode; falls back to text mode otherwise).

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/VoiceAssistant.git
cd VoiceAssistant
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

> **Note for Windows users:** Audio recording relies on `sounddevice` and `numpy`, eliminating the complex build errors associated with PyAudio on Windows.

---

## ⚙ Configuration

Create your local configuration file by copying `jarvis_config.example.json`:

```bash
# Windows PowerShell
copy jarvis_config.example.json jarvis_config.json

# Linux / macOS
cp jarvis_config.example.json jarvis_config.json
```

Edit `jarvis_config.json` with your credentials/preferences:

```json
{
  "language": "en-in",
  "wake_word": "jarvis",
  "music_dir": "C:\\Users\\YourUsername\\Music",
  "weather_api_key": "YOUR_OPENWEATHERMAP_API_KEY",
  "email_address": "your_email@gmail.com",
  "email_password": "your_app_password",
  "timezone": "UTC"
}
```

---

## 🖥 Usage

Run the main complete voice assistant:

```bash
python JarvisV2_Complete.py
```

### Available Command Categories

| Category | Example Commands |
|---|---|
| **System Info** | `system info`, `network info`, `processes`, `screenshot` |
| **System Control** | `lock computer`, `shutdown`, `restart`, `cancel shutdown` |
| **Media** | `play music`, `play video`, `youtube python tutorial`, `radio` |
| **Productivity** | `add task`, `show tasks`, `take note`, `reminder`, `set alarm` |
| **Web & Info** | `weather`, `search python`, `define algorithm`, `open google.com` |
| **Settings** | `settings`, `voices`, `set wake word jarvis` |
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
