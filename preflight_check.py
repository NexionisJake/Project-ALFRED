"""
Pre-Flight System Check for Project JHANGYA
Verifies all components are properly configured
"""

import sys
import os
from colorama import Fore, init

init(autoreset=True)

def check_file_exists(filename):
    """Check if a file exists"""
    exists = os.path.exists(filename)
    status = Fore.GREEN + "✓" if exists else Fore.RED + "✗"
    print(f"{status} {filename}")
    return exists

def check_imports():
    """Verify all required imports work"""
    print(f"\n{Fore.CYAN}=== Checking Imports ==={Fore.RESET}")
    
    modules = [
        ("langchain_groq", "Groq API"),
        ("langchain_ollama", "Ollama"),
        ("edge_tts", "Text-to-Speech"),
        ("pygame", "Audio Playback"),
        ("PyQt6.QtWidgets", "GUI Framework"),
        ("psutil", "System Monitoring"),
        ("pyautogui", "Automation"),
        ("faster_whisper", "Speech Recognition"),
    ]
    
    all_good = True
    for module, desc in modules:
        try:
            __import__(module)
            print(f"{Fore.GREEN}✓{Fore.RESET} {desc} ({module})")
        except ImportError:
            print(f"{Fore.RED}✗{Fore.RESET} {desc} ({module}) - MISSING!")
            all_good = False
    
    return all_good

def check_tools():
    """Verify all tools are properly defined"""
    print(f"\n{Fore.CYAN}=== Checking Tools ==={Fore.RESET}")
    
    try:
        from tools import (open_application, get_system_status, google_search, 
                          system_volume, media_play_pause, media_next, 
                          media_previous, search_knowledge_base)
        
        tools = [
            "open_application",
            "get_system_status", 
            "google_search",
            "system_volume",
            "media_play_pause",
            "media_next",
            "media_previous",
            "search_knowledge_base"
        ]
        
        for tool_name in tools:
            print(f"{Fore.GREEN}✓{Fore.RESET} {tool_name}")
        
        print(f"\n{Fore.GREEN}All 8 tools loaded successfully!{Fore.RESET}")
        return True
    except ImportError as e:
        print(f"{Fore.RED}✗ Tool import failed: {e}{Fore.RESET}")
        return False

def check_overlay():
    """Verify overlay components"""
    print(f"\n{Fore.CYAN}=== Checking Overlay ==={Fore.RESET}")
    
    try:
        from overlay import (OverlayWindow, COLOR_HAPPY, COLOR_ALERT, 
                            COLOR_ERROR, COLOR_NEUTRAL)
        
        colors = ["COLOR_HAPPY", "COLOR_ALERT", "COLOR_ERROR", "COLOR_NEUTRAL"]
        for color in colors:
            print(f"{Fore.GREEN}✓{Fore.RESET} {color}")
        
        print(f"\n{Fore.GREEN}Sentiment Engine ready!{Fore.RESET}")
        return True
    except ImportError as e:
        print(f"{Fore.RED}✗ Overlay import failed: {e}{Fore.RESET}")
        return False

def main():
    print(f"{Fore.CYAN}{'='*50}")
    print(f"   PROJECT JHANGYA - PRE-FLIGHT CHECK")
    print(f"{'='*50}{Fore.RESET}\n")
    
    print(f"{Fore.CYAN}=== Checking Core Files ==={Fore.RESET}")
    files_ok = all([
        check_file_exists("main.py"),
        check_file_exists("tools.py"),
        check_file_exists("overlay.py"),
        check_file_exists("ears.py"),
        check_file_exists("eyes.py"),
        check_file_exists("config.py"),
        check_file_exists("brain.txt"),
        check_file_exists(".env"),
    ])
    
    imports_ok = check_imports()
    tools_ok = check_tools()
    overlay_ok = check_overlay()
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"   SYSTEM STATUS")
    print(f"{'='*50}{Fore.RESET}\n")
    
    if files_ok and imports_ok and tools_ok and overlay_ok:
        print(f"{Fore.GREEN}✓ ALL SYSTEMS ONLINE{Fore.RESET}")
        print(f"\n{Fore.WHITE}Ready to launch!{Fore.RESET}")
        print(f"{Fore.YELLOW}Run: python main.py{Fore.RESET}")
        return 0
    else:
        print(f"{Fore.RED}✗ SYSTEM CHECK FAILED{Fore.RESET}")
        print(f"\n{Fore.YELLOW}Please fix the issues above before running.{Fore.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
