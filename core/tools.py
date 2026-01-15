import subprocess
import psutil # pip install psutil
import webbrowser
import pyautogui # pip install pyautogui
import datetime
import requests
import os
import pyperclip # pip install pyperclip
import time
from langchain_core.tools import tool
from core.app_launcher import AppLauncher

# Initialize Dynamic Launcher
launcher = AppLauncher()

# --- TOOL 1: OPEN APPLICATIONS ---

@tool
def open_application(app_name: str):
    """
    Call this tool when the user asks to open, launch, or start an application.
    Input 'app_name' should be the simple name of the app (e.g., 'calculator', 'notepad').
    Do not reply with text; use this tool.
    """
    # 1. Dynamic Lookup (Start Menu)
    path = launcher.get_app_path(app_name)
    if path:
        try:
            print(f"Launching via Shortcut: {path}")
            os.startfile(path)
            return f"Successfully launched {app_name}."
        except Exception as e:
            return f"Found {app_name}, but failed to launch: {e}"

    # 2. Hardcoded Fallback (System Apps / Special Commands)
    app_map = {
        # Windows App Mappings
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "vscode": "code",
        "spotify": "spotify",
        "terminal": "cmd.exe", # or powershell.exe
        "explorer": "explorer",
        "edge": "msedge.exe",
        "brave": "brave.exe",
        
        # Additional Windows Apps
        "firefox": "firefox.exe",
        "files": "explorer",
        "settings": "ms-settings:",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "discord": os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord PTB.lnk"),
        "vlc": "vlc.exe",
        "steam": "steam.exe",
        "control panel": "control",
        "task manager": "taskmgr",
    }
 
    # Normalize input
    key = app_name.lower()
    
    # STRICT LOOKUP: Only allow apps defined in the map
    if key not in app_map:
        return f"Error: '{app_name}' not found in installed apps or system map."
    
    target = app_map[key]
    
    try:
        # Windows specific handling
        if target.startswith("ms-settings:"):
            os.startfile(target)
            return f"Successfully launched {app_name}."
            
        # Try launching using subprocess
        # On Windows, shell=True can be useful for finding commands in PATH if not direct executables,
        # but Popen with list is generally safer.
        # However, for things like 'explorer', it works better with Popen.
        subprocess.Popen(target, shell=True)
        return f"Successfully launched {app_name}."

    except FileNotFoundError:
        return f"Failed to launch {app_name}: Executable '{target}' not found. Is it installed and in your PATH?"
    except Exception as e:
        return f"Failed to launch {app_name}: {e}"

# --- TOOL 2: SYSTEM HEALTH ---
@tool
def get_system_status():
    """Returns the current CPU usage percent and RAM usage percent."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    return f"CPU Usage: {cpu}%\nRAM Usage: {memory.percent}% ({memory.used // (1024**3)}GB used)"

# --- TOOL 3: GOOGLE SEARCH ---
@tool
def google_search(query: str):
    """
    Searches Google for the given query. 
    Use this when the user asks to 'search for', 'look up', or 'find' something online.
    Input 'query' should be the search term.
    """
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"I have opened a Google search for: {query}"

# --- TOOL 4: VOLUME CONTROL ---
@tool
def system_volume(action: str):
    """
    Controls system volume. Input 'action' must be 'up', 'down', or 'mute'.
    Use this when the user asks to increase/decrease volume or mute the system.
    """
    if action == "up":
        pyautogui.press("volumeup")
        pyautogui.press("volumeup")
        return "Volume turned up."
    elif action == "down":
        pyautogui.press("volumedown")
        pyautogui.press("volumedown")
        return "Volume turned down."
    elif action == "mute":
        pyautogui.press("volumemute")
        return "Volume muted."
    else:
        return f"Unknown volume action: {action}. Use 'up', 'down', or 'mute'."

# --- TOOL 5: MEDIA PLAY/PAUSE ---
@tool
def media_play_pause():
    """
    Toggles play/pause for any media player (Spotify, YouTube, VLC, etc.).
    Use this when the user asks to 'play', 'pause', 'resume', or 'stop' media.
    """
    pyautogui.press("playpause")
    return "Media play/pause toggled."

# --- TOOL 6: MEDIA NEXT TRACK ---
@tool
def media_next():
    """
    Skips to the next track or video in any media player.
    Use this when the user asks to 'skip', 'next song', 'next track', or 'next video'.
    """
    pyautogui.press("nexttrack")
    return "Skipped to next track."

# --- TOOL 7: MEDIA PREVIOUS TRACK ---
@tool
def media_previous():
    """
    Goes back to the previous track or video in any media player.
    Use this when the user asks to 'previous song', 'go back', or 'last track'.
    """
    pyautogui.press("prevtrack")
    return "Went back to previous track."

# --- TOOL 8: SEARCH KNOWLEDGE BASE ---
@tool
def search_knowledge_base(query: str):
    """
    Searches the personal knowledge base (brain.txt) for information.
    Use this when the user asks about personal information like WiFi passwords,
    pet names, favorite things, or any custom facts stored in the knowledge base.
    Input 'query' should be keywords to search for.
    Supports both encrypted (.enc) and plain text formats.
    """
    try:
        from core.encryption import SecureKnowledgeBase
        
        brain_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "brain.txt")
        
        # Initialize secure knowledge base (handles both encrypted and plain)
        kb = SecureKnowledgeBase(brain_file)
        matching_lines = kb.search(query)
        
        if matching_lines:
            return "From your knowledge base:\n" + "\n".join(matching_lines)
        else:
            return f"No information found in knowledge base for: {query}"
            
    except (ImportError, RuntimeError):
        # Fallback to plain text search if:
        # - encryption module not available (ImportError)
        # - running in non-interactive mode without password (RuntimeError)
        try:
            brain_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "brain.txt")
            
            if not os.path.exists(brain_file):
                return "Knowledge base not found. Please create a brain.txt file with your personal information."
            
            with open(brain_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            query_lower = query.lower()
            lines = content.split('\n')
            matching_lines = [line for line in lines if query_lower in line.lower() and line.strip()]
            
            if matching_lines:
                return "From your knowledge base:\n" + "\n".join(matching_lines)
            else:
                return f"No information found in knowledge base for: {query}"
                
        except Exception as e:
            return f"Error accessing knowledge base: {e}"
    except Exception as e:
        return f"Error accessing knowledge base: {e}"

# --- TOOL 9: DATE & TIME ---
@tool
def get_current_time():
    """
    Returns the current date and time.
    Use this when the user asks for the time, date, or day of the week.
    """
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")

# --- TOOL 10: WEATHER FORECAST ---
@tool
def get_weather(city: str):
    """
    Gets the current weather for a specific city.
    Input 'city' should be the name of the city (e.g., 'London', 'New York').
    If the user doesn't specify a city, ask them for it or check 'brain.txt'.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key not found. Please check your .env file."
    
    # OpenWeatherMap API Endpoint
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # Change to "imperial" for Fahrenheit
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        if data["cod"] != 200:
            return f"Error fetching weather: {data.get('message', 'Unknown error')}"
            
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        return f"Current weather in {city}: {weather_desc}. Temperature: {temp}°C. Humidity: {humidity}%. Wind: {wind_speed} m/s."
    except Exception as e:
        return f"Connection error: {e}"

# --- TOOL 11: GHOST WRITER ---
@tool
def write_to_screen(text: str):
    """
    Types or pastes text into the currently active window.
    Use this when the user asks you to 'write', 'type', 'code', or 'input' something.
    Best for writing code solutions, essays, or messages.
    """
    # 1. Copy text to clipboard (Safety & Speed)
    # Typing long code char-by-char often breaks indentation in editors like VS Code/LeetCode.
    # Pasting is instant and preserves formatting.
    pyperclip.copy(text)
    
    # 2. Safety Delay (Give user time to focus the box)
    # We don't want to paste immediately in case focus is wrong.
    time.sleep(0.5) 
    
    # 3. Simulate Paste (Ctrl+V)
    # pyautogui detects OS automatically usually, but standard is ctrl+v
    pyautogui.hotkey('ctrl', 'v')
    
    return "Text pasted successfully."