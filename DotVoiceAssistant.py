import pyttsx3  # pip install pyttsx3
import speech_recognition as sr  # pip install speechRecognition
import datetime
import os
import subprocess
import webbrowser
import psutil  # pip install psutil
import random
import json
from pathlib import Path
import requests  # pip install requests
import smtplib  # for email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from PIL import ImageGrab  # pip install pillow
import socket

# Check for optional audio backends
try:
    import pyaudio  # pip install pyaudio or use pipwin on Windows to get prebuilt wheels
    HAVE_PYAUDIO = True
except Exception:
    HAVE_PYAUDIO = False

try:
    import sounddevice as sd
    import numpy as np
    HAVE_SOUNDDEVICE = True
except Exception:
    HAVE_SOUNDDEVICE = False

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)

# Configuration files
HISTORY_FILE = "command_history.json"
TODO_FILE = "todos.json"
REMINDERS_FILE = "reminders.json"
CONFIG_FILE = "dot_config.json"

# Default configuration
DEFAULT_CONFIG = {
    'language': 'en-in',
    'wake_word': 'dot',
    'music_dir': 'D:\\Shubham\\Music',
    'weather_api_key': '',
    'email_address': '',
    'email_password': '',
    'timezone': 'UTC',
}

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def speak(audio):
    """Speak the given audio text"""
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        print_error(f"Speech error: {e}")

def wish_me():
    """Greet user based on time"""
    hour = int(datetime.datetime.now().hour)
    
    if 0 <= hour < 12:
        greeting = "Good Morning! "
    elif 12 <= hour < 18:
        greeting = "Good Afternoon! "
    else:
        greeting = "Good Evening! "
    
    greeting += "I'm Dot, your voice assistant. How can I help?"
    speak(greeting)
    print_info(greeting)

def record_audio_with_sounddevice(duration=5, fs=16000):
    """Record audio with sounddevice if PyAudio is unavailable"""
    if not HAVE_SOUNDDEVICE:
        raise RuntimeError("sounddevice is not available")

    print(f"{Colors.YELLOW}🎤 Listening with sounddevice...{Colors.ENDC}")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    audio_bytes = audio.tobytes()
    return sr.AudioData(audio_bytes, sample_rate=fs, sample_width=2)


def take_command():
    """Take voice command from microphone"""
    r = sr.Recognizer()

    # If PyAudio is not available, try sounddevice first, otherwise fall back to typed input
    if not HAVE_PYAUDIO:
        if HAVE_SOUNDDEVICE:
            try:
                audio = record_audio_with_sounddevice(duration=5)
                print(f"{Colors.YELLOW}🔄 Recognizing...{Colors.ENDC}")
                query = r.recognize_google(audio, language='en-in')
                print_success(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                print_error("Could not understand. Please speak again...")
                return "none"
            except sr.RequestError:
                print_error("Network issue. Please check internet connection...")
                return "none"
            except Exception as e:
                print_error(f"Sounddevice error: {e}")
                print_warning("Falling back to text input.")
        else:
            print_warning("PyAudio not installed and sounddevice unavailable — using text input.")

        try:
            typed = input("Type your command: ")
            return typed
        except Exception:
            return "none"

    try:
        with sr.Microphone() as source:
            print(f"{Colors.YELLOW}🎤 Listening...{Colors.ENDC}")
            r.pause_threshold = 1
            r.energy_threshold = 4000
            # timeout waits for phrase to start; phrase_time_limit limits length
            audio = r.listen(source, timeout=5, phrase_time_limit=10)

        print(f"{Colors.YELLOW}🔄 Recognizing...{Colors.ENDC}")
        query = r.recognize_google(audio, language='en-in')
        print_success(f"You said: {query}")
        return query

    except sr.UnknownValueError:
        print_error("Could not understand. Please speak again...")
        return "none"
    except sr.RequestError:
        print_error("Network issue. Please check internet connection...")
        return "none"
    except sr.WaitTimeoutError:
        # speech_recognition raises WaitTimeoutError when no phrase is detected in timeout
        print_error("No input detected. Please try again...")
        return "none"
    except Exception as e:
        print_error(f"Error: {e}")
        return "none"

# ==================== TIME & REMINDERS ====================

def get_time():
    """Get current time"""
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
    message = f"Sir, the time is {time_str} on {date_str}"
    speak(message)
    print_info(f"📅 {message}")

def set_reminder(hours=1, minutes=0):
    """Set a reminder"""
    try:
        reminder_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)
        message = f"Reminder for later"
        
        reminders = []
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r') as f:
                reminders = json.load(f)
        
        reminders.append({
            'message': message,
            'time': reminder_time.isoformat(),
            'created': datetime.datetime.now().isoformat()
        })
        
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(reminders, f, indent=2)
        
        time_display = reminder_time.strftime("%H:%M")
        print_success(f"Reminder set for {time_display}")
        speak(f"Reminder set for {hours} hour from now")
    except Exception as e:
        print_error(f"Reminder error: {e}")

def set_alarm(hours=0, minutes=5):
    """Set an alarm"""
    try:
        alarm_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)
        print_header(f"ALARM SET FOR {alarm_time.strftime('%H:%M:%S')}")
        speak(f"Alarm set for {alarm_time.strftime('%H:%M')}")
        
        def alarm_thread():
            while True:
                current_time = datetime.datetime.now()
                if current_time >= alarm_time:
                    print_error("⏰ ALARM! ALARM! ALARM!")
                    for _ in range(5):
                        speak("Alarm!")
                    break
                time.sleep(1)
        
        thread = threading.Thread(target=alarm_thread, daemon=True)
        thread.start()
    except Exception as e:
        print_error(f"Alarm error: {e}")

# ==================== SYSTEM MANAGEMENT ====================

def get_system_info():
    """Display system information"""
    print_header("SYSTEM INFORMATION")
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print_info(f"CPU Usage: {cpu_percent}%")
        print_info(f"Memory: {memory.percent}% ({memory.used // (1024**3)}/{memory.total // (1024**3)} GB)")
        print_info(f"Disk: {disk.percent}% ({disk.used // (1024**3)}/{disk.total // (1024**3)} GB)")
        
        message = f"CPU at {cpu_percent} percent, Memory at {memory.percent} percent"
        speak(message)
    except Exception as e:
        print_error(f"System info error: {e}")

def get_network_info():
    """Display network information"""
    print_header("NETWORK INFORMATION")
    
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        print_info(f"Hostname: {hostname}")
        print_info(f"IP Address: {ip_address}")
        
        try:
            requests.get('http://google.com', timeout=2)
            print_success("Internet: Connected")
            speak("Internet is connected")
        except:
            print_error("Internet: Not connected")
            speak("Internet is not connected")
            
    except Exception as e:
        print_error(f"Network error: {e}")

def list_running_processes():
    """List top running processes"""
    print_header("TOP RUNNING PROCESSES")
    
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append((proc.info['name'], proc.info['memory_percent']))
            except:
                pass
        
        processes.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, mem) in enumerate(processes[:10], 1):
            print(f"  {i}. {name:<30} - {mem:.2f}% RAM")
        
        speak(f"Found {len(processes)} running processes")
    except Exception as e:
        print_error(f"Process error: {e}")

def take_screenshot():
    """Take a screenshot"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        print_success(f"Screenshot saved: {filename}")
        speak("Screenshot taken")
    except Exception as e:
        print_error(f"Screenshot error: {e}")

def shutdown_pc():
    """Shutdown the computer"""
    try:
        print_warning("Shutting down computer in 10 seconds...")
        speak("Computer will shutdown in 10 seconds")
        os.system("shutdown /s /t 10")
    except Exception as e:
        print_error(f"Shutdown error: {e}")

def restart_pc():
    """Restart the computer"""
    try:
        print_warning("Restarting computer in 10 seconds...")
        speak("Computer will restart in 10 seconds")
        os.system("shutdown /r /t 10")
    except Exception as e:
        print_error(f"Restart error: {e}")

def lock_computer():
    """Lock the computer"""
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        print_success("Computer locked")
        speak("Computer locked")
    except Exception as e:
        print_error(f"Lock error: {e}")

def cancel_shutdown():
    """Cancel shutdown"""
    try:
        os.system("shutdown /a")
        print_success("Shutdown cancelled")
        speak("Shutdown cancelled")
    except Exception as e:
        print_warning("No shutdown scheduled")

# ==================== FILE MANAGEMENT ====================

def list_files(path="."):
    """List files in directory"""
    try:
        print_header(f"FILES IN: {os.path.abspath(path)}")
        files = os.listdir(path)
        
        for i, file in enumerate(files[:20], 1):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                print(f"  📁 {file}")
            else:
                print(f"  📄 {file}")
        
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more files")
        
        speak(f"Found {len(files)} items in directory")
    except Exception as e:
        print_error(f"Error listing files: {e}")

def get_recent_files(directory=".", count=10):
    """Get recently modified files"""
    print_header(f"RECENT FILES - {os.path.abspath(directory)}")
    
    try:
        files = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isfile(path):
                mod_time = os.path.getmtime(path)
                files.append((item, mod_time))
        
        files.sort(key=lambda x: x[1], reverse=True)
        
        for i, (filename, mod_time) in enumerate(files[:count], 1):
            time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
            print(f"  {i}. {filename:<40} - {time_str}")
        
        speak(f"Found {len(files)} recent files")
    except Exception as e:
        print_error(f"Recent files error: {e}")

def create_file(filename, content=""):
    """Create a new file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f"File created: {filename}")
        speak(f"File {filename} created")
    except Exception as e:
        print_error(f"Create file error: {e}")

def delete_file(filename):
    """Delete a file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print_success(f"File deleted: {filename}")
            speak(f"File {filename} deleted")
        else:
            print_error("File not found")
    except Exception as e:
        print_error(f"Delete error: {e}")

def navigate_directory(path):
    """Navigate to a directory"""
    try:
        if os.path.isdir(path):
            os.chdir(path)
            print_success(f"Navigated to: {os.getcwd()}")
            speak(f"Navigated to {path}")
        else:
            print_error(f"Directory not found: {path}")
    except Exception as e:
        print_error(f"Navigation error: {e}")

# ==================== MUSIC & MEDIA ====================

def play_music():
    """Play music from Music directory"""
    try:
        music_dir = 'D:\\Shubham\\Music'
        if not os.path.exists(music_dir):
            print_error(f"Music directory not found: {music_dir}")
            return
        
        songs = [s for s in os.listdir(music_dir) if s.endswith(('.mp3', '.wav', '.flac'))]
        
        if not songs:
            print_error("No music files found")
            return
        
        print_header("MUSIC PLAYER")
        for i, song in enumerate(songs[:10], 1):
            print(f"  {i}. {song}")
        
        song = random.choice(songs)
        print_success(f"Now playing: {song}")
        speak(f"Playing {song}")
        os.startfile(os.path.join(music_dir, song))
    except Exception as e:
        print_error(f"Music error: {e}")

def play_video(video_path=None):
    """Play a video file"""
    try:
        if not video_path:
            video_dir = 'D:\\Videos'
            if os.path.exists(video_dir):
                videos = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
                if videos:
                    video_path = os.path.join(video_dir, random.choice(videos))
        
        if video_path and os.path.exists(video_path):
            os.startfile(video_path)
            print_success(f"Playing video: {os.path.basename(video_path)}")
            speak("Playing video")
        else:
            print_error("No video found")
    except Exception as e:
        print_error(f"Video error: {e}")

def display_images(image_dir='D:\\Pictures'):
    """Display images from a folder"""
    try:
        print_header(f"IMAGE VIEWER - {image_dir}")
        
        images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not images:
            print_error("No images found")
            return
        
        for i, img in enumerate(images[:10], 1):
            print(f"  {i}. {img}")
        
        print_success(f"Found {len(images)} images")
        speak(f"Found {len(images)} images in the folder")
    except Exception as e:
        print_error(f"Image error: {e}")

def search_youtube(query):
    """Search YouTube"""
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        print_success(f"Searching YouTube for: {query}")
        speak(f"Searching YouTube for {query}")
    except Exception as e:
        print_error(f"YouTube search error: {e}")

def read_file_aloud(filepath):
    """Read a text file aloud"""
    try:
        if not os.path.exists(filepath):
            print_error(f"File not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print_header(f"READING: {os.path.basename(filepath)}")
        print(content[:200] + "..." if len(content) > 200 else content)
        
        speak(content)
    except Exception as e:
        print_error(f"Read file error: {e}")

def play_radio():
    """Play online radio"""
    print_header("RADIO PLAYER")
    
    try:
        station_url = "http://stream.antena3.ro:8000"
        print_info(f"Opening radio stream...")
        speak("Opening radio stream")
        os.startfile(station_url)
    except Exception as e:
        print_error(f"Radio error: {e}")

# ==================== WEB & SEARCH ====================

def search_web(query):
    """Search on Google"""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        print_success(f"Searching for: {query}")
        speak(f"Searching for {query} on Google")
    except Exception as e:
        print_error(f"Search error: {e}")

def open_website(url):
    """Open website in browser"""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        print_success(f"Opening {url}")
        speak(f"Opening {url}")
    except Exception as e:
        print_error(f"Could not open website: {e}")

def open_application(app_name):
    """Open an application"""
    try:
        app_paths = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'firefox': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
        }
        
        if app_name.lower() in app_paths:
            os.startfile(app_paths[app_name.lower()])
            print_success(f"Opening {app_name}")
            speak(f"Opening {app_name}")
        else:
            print_error(f"Application '{app_name}' not found in shortcuts")
    except Exception as e:
        print_error(f"Could not open application: {e}")

# ==================== INFORMATION ====================

def get_weather(city="London"):
    """Get weather information"""
    print_header(f"WEATHER - {city}")
    
    try:
        config = load_config()
        api_key = config.get('weather_api_key', '')
        
        if not api_key:
            print_warning("Weather API key not configured. Get one from openweathermap.org")
            return
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            
            print_info(f"Temperature: {temp}°C")
            print_info(f"Humidity: {humidity}%")
            print_info(f"Condition: {description.title()}")
            
            message = f"Weather in {city}: {temp} degrees, {description}"
            speak(message)
        else:
            print_error("City not found")
    except requests.exceptions.Timeout:
        print_error("Weather API timeout")
    except Exception as e:
        print_error(f"Weather error: {e}")

def get_dictionary_definition(word):
    """Get word definition"""
    print_header(f"DEFINITION - {word}")
    
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()[0]
            meanings = data.get('meanings', [])
            
            if meanings:
                meaning = meanings[0]
                part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                definitions = meaning.get('definitions', [])
                
                print_info(f"Part of Speech: {part_of_speech}")
                
                if definitions:
                    definition = definitions[0].get('definition', 'No definition found')
                    print_info(f"Definition: {definition}")
                    speak(f"{word} means {definition}")
            else:
                print_error("No definitions found")
        else:
            print_error(f"Word not found: {word}")
    except Exception as e:
        print_error(f"Dictionary error: {e}")

def tell_trivia():
    """Tell a random trivia fact"""
    trivia_facts = [
        "Did you know? Honey never spoils. Archaeologists have found 3000-year-old honey that was still edible!",
        "Did you know? A group of flamingos is called a flamboyance!",
        "Did you know? Octopuses have three hearts!",
        "Did you know? Bananas are berries but strawberries aren't!",
        "Did you know? The Great Wall of China is not visible from space!",
        "Did you know? A day on Venus is longer than its year!",
        "Did you know? Cleopatra lived closer to the invention of pizza than to the building of the Great Pyramid!",
        "Did you know? Sloths only defecate once a week!",
        "Did you know? A group of pugs is called a grumble!",
        "Did you know? Carrots were originally purple, not orange!",
    ]
    
    fact = random.choice(trivia_facts)
    print_success(fact)
    speak(fact)

def convert_units(value, from_unit, to_unit):
    """Convert between units"""
    print_header("UNIT CONVERTER")
    
    try:
        conversions = {
            ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
            ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
            ('km', 'miles'): lambda x: x * 0.621371,
            ('miles', 'km'): lambda x: x * 1.60934,
            ('kg', 'pounds'): lambda x: x * 2.20462,
            ('pounds', 'kg'): lambda x: x * 0.453592,
        }
        
        key = (from_unit.lower(), to_unit.lower())
        
        if key in conversions:
            result = conversions[key](value)
            message = f"{value} {from_unit} equals {result:.2f} {to_unit}"
            print_info(message)
            speak(message)
        else:
            print_error(f"Conversion not supported: {from_unit} to {to_unit}")
    except Exception as e:
        print_error(f"Conversion error: {e}")

def solve_math(expression):
    """Solve math expressions"""
    print_header("CALCULATOR")
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        message = f"{expression} equals {result}"
        print_info(message)
        speak(message)
    except Exception as e:
        print_error(f"Math error: {e}")

# ==================== PRODUCTIVITY ====================

def add_todo(task):
    """Add a task to TODO list"""
    try:
        todos = []
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r') as f:
                todos = json.load(f)
        
        todos.append({
            'task': task,
            'completed': False,
            'created': datetime.datetime.now().isoformat()
        })
        
        with open(TODO_FILE, 'w') as f:
            json.dump(todos, f, indent=2)
        
        print_success(f"Task added: {task}")
        speak(f"Task {task} added to your TODO list")
    except Exception as e:
        print_error(f"TODO error: {e}")

def list_todos():
    """List all TODO items"""
    print_header("TODO LIST")
    
    try:
        if not os.path.exists(TODO_FILE):
            print_warning("No tasks yet")
            return
        
        with open(TODO_FILE, 'r') as f:
            todos = json.load(f)
        
        pending = [t for t in todos if not t['completed']]
        completed = [t for t in todos if t['completed']]
        
        if pending:
            print(f"\n{Colors.YELLOW}PENDING ({len(pending)}):{Colors.ENDC}")
            for i, todo in enumerate(pending, 1):
                print(f"  {i}. ☐ {todo['task']}")
        
        if completed:
            print(f"\n{Colors.GREEN}COMPLETED ({len(completed)}):{Colors.ENDC}")
            for i, todo in enumerate(completed, 1):
                print(f"  {i}. ☑ {todo['task']}")
        
        speak(f"You have {len(pending)} pending tasks")
    except Exception as e:
        print_error(f"TODO error: {e}")

def take_note():
    """Take a voice note"""
    try:
        print_header("VOICE NOTE")
        print_info("Say your note (you will have 10 seconds)...")
        speak("Say your note now")
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=10)
        
        note = r.recognize_google(audio, language='en-in')
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note_file = "notes.txt"
        
        with open(note_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {note}\n")
        
        print_success(f"Note saved: {note}")
        speak("Note saved successfully")
    except Exception as e:
        print_error(f"Note error: {e}")

def send_email(to_email, subject, body):
    """Send an email"""
    print_header("SENDING EMAIL")
    
    try:
        config = load_config()
        sender_email = config.get('email_address', '')
        sender_password = config.get('email_password', '')
        
        if not sender_email or not sender_password:
            print_warning("Email not configured. Set email_address and email_password in config")
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print_success(f"Email sent to {to_email}")
        speak("Email sent successfully")
    except Exception as e:
        print_error(f"Email error: {e}")

# ==================== ENTERTAINMENT ====================

def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the Python go to the gym? To get more Python muscle!",
        "What do you call a programmer from Finland? Nerdic!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    ]
    
    joke = random.choice(jokes)
    print_success(joke)
    speak(joke)

# ==================== CONFIGURATION ====================

def load_config():
    """Load configuration file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print_success("Configuration saved")
    except Exception as e:
        print_error(f"Config save error: {e}")

def show_settings():
    """Show current settings"""
    print_header("SETTINGS")
    
    config = load_config()
    for key, value in config.items():
        if 'password' not in key and 'key' not in key.lower():
            print_info(f"{key}: {value}")
        else:
            print_info(f"{key}: ••••••••••")

def set_language(language='en-in'):
    """Change language for speech recognition"""
    config = load_config()
    config['language'] = language
    save_config(config)
    print_success(f"Language set to: {language}")
    speak("Language updated")

def set_wake_word(word='dot'):
    """Set custom wake word"""
    config = load_config()
    config['wake_word'] = word.lower()
    save_config(config)
    print_success(f"Wake word set to: {word}")
    speak(f"Wake word set to {word}")

def voice_profiles():
    """Show available voice profiles"""
    print_header("VOICE PROFILES")
    
    for i, voice in enumerate(voices, 1):
        print(f"  {i}. {voice.name} - {voice.id}")

def run_system_command(command):
    """Run a Windows system command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print_info(result.stdout)
            speak("Command executed")
        if result.stderr:
            print_error(result.stderr)
    except Exception as e:
        print_error(f"Command error: {e}")

def save_command_history(command):
    """Save command to history"""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        
        history.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'command': command
        })
        
        history = history[-100:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        pass

def show_help():
    """Display help menu"""
    print_header("AVAILABLE COMMANDS")
    
    commands = {
        "⏰ TIME": {
            'time': 'Tell current time and date',
            'set reminder': 'Set reminder (say: set reminder)',
            'set alarm': 'Set alarm (say: set alarm)',
        },
        "🎵 MEDIA": {
            'play music': 'Play random music',
            'play video': 'Play random video',
            'youtube [search]': 'Search YouTube',
            'radio': 'Play online radio',
            'read file': 'Read text file aloud',
        },
        "📁 FILES": {
            'list files': 'List files in directory',
            'recent files': 'Show recently modified files',
            'create file': 'Create new file',
            'delete file': 'Delete a file',
            'navigate': 'Change directory',
        },
        "🌐 INFORMATION": {
            'weather': 'Get weather (needs API key)',
            'define [word]': 'Get word definition',
            'trivia': 'Tell a fun fact',
            'convert': 'Convert units',
            'calculate [math]': 'Solve math',
        },
        "✅ PRODUCTIVITY": {
            'add task': 'Add to TODO list',
            'my tasks': 'Show TODO list',
            'send email': 'Send email',
            'note': 'Take voice note',
        },
        "💻 SYSTEM": {
            'system info': 'Display system resources',
            'network info': 'Show network details',
            'processes': 'List running processes',
            'screenshot': 'Take screenshot',
            'lock': 'Lock computer',
            'shutdown': 'Shutdown PC',
            'restart': 'Restart PC',
            'cancel': 'Cancel shutdown',
        },
        "⚙️ SETTINGS": {
            'settings': 'Show current settings',
            'voices': 'Show available voices',
            'set language': 'Change recognition language',
            'set wake word': 'Set custom wake word',
        },
        "🎭 FUN": {
            'joke': 'Tell a joke',
            'images': 'Show images',
        },
    }
    
    for category, cmds in commands.items():
        print(f"\n{Colors.CYAN}{Colors.BOLD}{category}{Colors.ENDC}")
        for cmd, desc in cmds.items():
            print(f"  {Colors.BLUE}{cmd:<25}{Colors.ENDC}→ {desc}")
    
    print()

# ==================== MAIN PROGRAM ====================

if __name__ == "__main__":
    print_header("DOT VOICE ASSISTANT")
    print_info("Say 'help' for available commands or 'exit' to quit.\n")
    
    wish_me()
    
    while True:
        try:
            print(f"\n{Colors.BOLD}{Colors.BLUE}[DOT]${Colors.ENDC} ", end="", flush=True)
            
            query = take_command().lower()
            
            if query == "none":
                continue
            
            save_command_history(query)
            
            # TIME & REMINDERS
            if 'time' in query:
                get_time()
            elif 'reminder' in query and 'set' in query:
                set_reminder(hours=1)
            elif 'alarm' in query and 'set' in query:
                set_alarm(minutes=5)
            
            # MUSIC & MEDIA
            elif 'play music' in query:
                play_music()
            elif 'play video' in query:
                play_video()
            elif 'youtube' in query:
                search_query = query.replace('youtube', '').strip()
                search_youtube(search_query if search_query else 'music')
            elif 'radio' in query:
                play_radio()
            elif 'read file' in query:
                read_file_aloud('notes.txt')
            
            # FILES
            elif 'list files' in query or 'show files' in query:
                list_files()
            elif 'recent files' in query:
                get_recent_files()
            elif 'create file' in query:
                create_file('new_file.txt', 'Created by Dot')
            elif 'delete file' in query:
                print_warning("Which file to delete?")
            elif 'navigate' in query:
                navigate_directory('.')
            
            # INFORMATION
            elif 'weather' in query:
                get_weather('London')
            elif 'define' in query:
                word = query.replace('define', '').strip()
                if word:
                    get_dictionary_definition(word)
            elif 'trivia' in query:
                tell_trivia()
            elif 'convert' in query:
                convert_units(100, 'km', 'miles')
            elif 'calculate' in query or 'math' in query:
                solve_math('2+2')
            
            # PRODUCTIVITY
            elif 'add task' in query or 'add todo' in query:
                add_todo('New task')
            elif 'my tasks' in query or 'show tasks' in query:
                list_todos()
            elif 'note' in query or 'take note' in query:
                take_note()
            elif 'send email' in query:
                print_warning("Email sending requires config setup")
            
            # SYSTEM
            elif 'system info' in query or 'system status' in query:
                get_system_info()
            elif 'network info' in query:
                get_network_info()
            elif 'processes' in query:
                list_running_processes()
            elif 'screenshot' in query:
                take_screenshot()
            elif 'lock' in query and 'computer' in query:
                lock_computer()
            elif 'shutdown' in query:
                shutdown_pc()
            elif 'restart' in query:
                restart_pc()
            elif 'cancel' in query and 'shutdown' in query:
                cancel_shutdown()
            
            # WEB & SEARCH
            elif 'search' in query:
                search_query = query.replace('search', '').strip()
                search_web(search_query if search_query else 'Python')
            elif 'open' in query and ('website' in query or 'web' in query):
                website = query.replace('open', '').replace('website', '').strip()
                open_website(website if website else 'google.com')
            elif 'open' in query and 'app' in query:
                app = query.replace('open', '').replace('app', '').strip()
                open_application(app if app else 'notepad')
            
            # SETTINGS
            elif 'settings' in query:
                show_settings()
            elif 'voices' in query:
                voice_profiles()
            elif 'set language' in query:
                set_language('en-in')
            elif 'set wake word' in query:
                set_wake_word('dot')
            
            # ENTERTAINMENT
            elif 'joke' in query:
                tell_joke()
            elif 'images' in query or 'image' in query:
                display_images()
            
            # HELP & EXIT
            elif 'help' in query:
                show_help()
            elif 'bye' in query or 'exit' in query or 'quit' in query:
                print_success("Goodbye! Thanks for using Dot.")
                speak("Goodbye")
                break
            else:
                print_warning("Command not recognized. Say 'help' for available commands.")
                speak("I didn't understand that. Please try again or say help for available commands.")
    
    except KeyboardInterrupt:
        print_header("DOT VOICE ASSISTANT SHUTTING DOWN")
        print_success("Goodbye!")
        speak("Goodbye")
