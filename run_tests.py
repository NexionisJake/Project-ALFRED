import sys
import os
import time
from dotenv import load_dotenv
from colorama import Fore, init

# Load Env
load_dotenv()

# Init Colorama
init(autoreset=True)

# Fix Windows Unicode Encode Error
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print(Fore.CYAN + "========================================")
print(Fore.CYAN + "   ALFRED INTEGRATION TEST SUITE")
print(Fore.CYAN + "========================================\n")

def test_config():
    print(Fore.YELLOW + "Testing Config...")
    try:
        import config
        print(Fore.GREEN + f"✓ Config loaded. Wake Word: {config.WAKE_WORD}")
    except ImportError:
        print(Fore.RED + "✗ Config load failed!")
        return False
    return True

def test_app_launcher():
    print(Fore.YELLOW + "\nTesting App Launcher...")
    try:
        from core.app_launcher import AppLauncher
        launcher = AppLauncher()
        
        if not launcher.app_index:
            print(Fore.RED + "✗ No apps indexed!")
            return False
            
        # Get first app
        first_app = list(launcher.app_index.keys())[0]
        path = launcher.get_app_path(first_app)
        
        if path:
            print(Fore.GREEN + f"✓ App Launcher works. Found: {first_app} at {path}")
            return True
        else:
            print(Fore.RED + "✗ App path resolution failed")
            return False
            
    except Exception as e:
        print(Fore.RED + f"✗ App Launcher Error: {e}")
        return False

def test_brain_init():
    print(Fore.YELLOW + "\nTesting Brain Initialization...")
    try:
        from core.brain import AlfredBrain
        brain = AlfredBrain()
        print(Fore.GREEN + "✓ Brain initialized (Tools + Memory + LLM)")
        return True
    except Exception as e:
        print(Fore.RED + f"✗ Brain Init Error: {e}")
        return False

def test_voice_init():
    print(Fore.YELLOW + "\nTesting Voice System...")
    try:
        from core.voice import AlfredVoice
        voice = AlfredVoice()
        print(Fore.GREEN + "✓ Voice initialized (EdgeTTS + Pygame)")
        return True
    except Exception as e:
        print(Fore.RED + f"✗ Voice Init Error: {e}")
        return False

def run_all_tests():
    checks = [
        test_config,
        test_app_launcher,
        test_brain_init,
        test_voice_init
    ]
    
    passed = 0
    for check in checks:
        if check():
            passed += 1
            
    print(Fore.CYAN + "\n========================================")
    if passed == len(checks):
        print(Fore.GREEN + f"ALL SYSTEMS GO ({passed}/{len(checks)} Passed)")
        print(Fore.GREEN + "Ready to run 'main.py'")
    else:
        print(Fore.RED + f"SYSTEM CHECK FAILED ({passed}/{len(checks)} Passed)")
        print(Fore.RED + "Check errors above.")
    print(Fore.CYAN + "========================================")

if __name__ == "__main__":
    run_all_tests()
