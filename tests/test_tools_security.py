import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MOCK PYAUTOGUI TO AVOID DISPLAY ERRORS
sys.modules["pyautogui"] = MagicMock()
sys.modules["pyperclip"] = MagicMock()

from core.tools import open_application
from colorama import Fore, init
import time

init(autoreset=True)

def test_open_application():
    print(Fore.CYAN + "--- Testing open_application Tool ---\n")

    # 1. Test Valid App (should pass check, might fail execution if not installed)
    print(Fore.YELLOW + "Test 1: Valid App ('calculator')")
    result = open_application.invoke({"app_name": "calculator"})
    print(Fore.WHITE + f"Result: {result}")
    print("-" * 30)

    # 2. Test Invalid App (should be blocked by allowlist)
    print(Fore.YELLOW + "Test 2: Invalid App ('malware.exe')")
    result = open_application.invoke({"app_name": "malware.exe"})
    print(Fore.WHITE + f"Result: {result}")
    
    if "Error" in result and "safety restriction" in result.lower():
         print(Fore.GREEN + "PASS: Invalid app blocked.")
    else:
         print(Fore.RED + "FAIL: Invalid app was NOT blocked.")
    print("-" * 30)

    # 3. Test Injection Attack (should be blocked by allowlist)
    print(Fore.YELLOW + "Test 3: Injection Attack ('calculator; rm -rf /')")
    result = open_application.invoke({"app_name": "calculator; rm -rf /"})
    print(Fore.WHITE + f"Result: {result}")
    
    if "Error" in result and "safety restriction" in result.lower():
         print(Fore.GREEN + "PASS: Injection blocked.")
    else:
         print(Fore.RED + "FAIL: Injection was NOT blocked.")
    print("-" * 30)

if __name__ == "__main__":
    test_open_application()
