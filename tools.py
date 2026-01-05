import subprocess
import psutil # pip install psutil
import webbrowser
import pyautogui # pip install pyautogui
from langchain_core.tools import tool

# --- TOOL 1: OPEN APPLICATIONS ---

@tool
def open_application(app_name: str):
    """
    Call this tool when the user asks to open, launch, or start an application.
    Input 'app_name' should be the simple name of the app (e.g., 'calculator', 'notepad').
    Do not reply with text; use this tool.
    """
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "vscode": "code",
        "spotify": "spotify",
        "cmd": "cmd.exe",
        "explorer": "explorer.exe",
        "edge": "msedge.exe",
        "brave": "brave.exe"
    }
 
    
    # Try to find the app in our map, otherwise assume it's a direct command
    target = app_map.get(app_name.lower(), app_name)
    
    try:
        subprocess.Popen(target, shell=True)
        return f"Successfully launched {app_name}."
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
    """
    try:
        import os
        brain_file = os.path.join(os.path.dirname(__file__), "brain.txt")
        
        if not os.path.exists(brain_file):
            return "Knowledge base not found. Please create a brain.txt file with your personal information."
        
        with open(brain_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple keyword search - find lines containing query words
        query_lower = query.lower()
        lines = content.split('\n')
        matching_lines = [line for line in lines if query_lower in line.lower() and line.strip()]
        
        if matching_lines:
            return "From your knowledge base:\n" + "\n".join(matching_lines)
        else:
            return f"No information found in knowledge base for: {query}"
            
    except Exception as e:
        return f"Error accessing knowledge base: {e}"