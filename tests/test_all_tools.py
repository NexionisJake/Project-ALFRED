"""
Comprehensive test suite for all 11 ALFRED tools.
Uses mocking to avoid side effects during testing.
"""

import sys
import os
from unittest.mock import MagicMock, patch
import tempfile

# Mock GUI-dependent modules BEFORE importing tools
sys.modules["pyautogui"] = MagicMock()
sys.modules["pyperclip"] = MagicMock()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorama import Fore, init
init(autoreset=True)

from test_utils import TestResults, SYM_CHECK, SYM_FAIL





def test_open_application(results: TestResults):
    """Test open_application tool"""
    print(Fore.CYAN + "\n--- Testing open_application ---")
    
    from core.tools import open_application
    
    # Test 1: Valid app from allowlist
    result = open_application.invoke({"app_name": "calculator"})
    if "Successfully" in result or "not found" in result:  # Accept both (depends on system)
        results.add_pass("Valid app (calculator)")
    else:
        results.add_fail("Valid app (calculator)", result)
    
    # Test 2: Invalid app - should be blocked
    result = open_application.invoke({"app_name": "malware.exe"})
    if "Error" in result and "not in the allowed" in result:
        results.add_pass("Invalid app blocked (malware.exe)")
    else:
        results.add_fail("Invalid app blocked", result)
    
    # Test 3: Injection attempt - should be blocked
    result = open_application.invoke({"app_name": "calc; rm -rf /"})
    if "Error" in result and "not in the allowed" in result:
        results.add_pass("Injection attack blocked")
    else:
        results.add_fail("Injection attack blocked", result)
    
    # Test 4: Case insensitivity
    result = open_application.invoke({"app_name": "CALCULATOR"})
    if "Successfully" in result or "not found" in result:
        results.add_pass("Case insensitive lookup")
    else:
        results.add_fail("Case insensitive lookup", result)


def test_get_system_status(results: TestResults):
    """Test get_system_status tool"""
    print(Fore.CYAN + "\n--- Testing get_system_status ---")
    
    from core.tools import get_system_status
    
    result = get_system_status.invoke({})
    
    if "CPU Usage" in result and "RAM Usage" in result:
        results.add_pass("Returns CPU and RAM info")
    else:
        results.add_fail("Returns CPU and RAM info", result)
    
    if "%" in result:
        results.add_pass("Contains percentage values")
    else:
        results.add_fail("Contains percentage values", result)


def test_google_search(results: TestResults):
    """Test google_search tool"""
    print(Fore.CYAN + "\n--- Testing google_search ---")
    
    from core.tools import google_search
    
    # Mock webbrowser.open to prevent actual browser opening
    with patch('webbrowser.open') as mock_browser:
        result = google_search.invoke({"query": "Python programming"})
        
        if "opened a Google search" in result:
            results.add_pass("Returns confirmation message")
        else:
            results.add_fail("Returns confirmation message", result)
        
        if mock_browser.called:
            results.add_pass("Calls webbrowser.open")
        else:
            results.add_fail("Calls webbrowser.open", "webbrowser.open not called")


def test_system_volume(results: TestResults):
    """Test system_volume tool"""
    print(Fore.CYAN + "\n--- Testing system_volume ---")
    
    from core.tools import system_volume
    
    # Test volume up
    result = system_volume.invoke({"action": "up"})
    if "Volume turned up" in result:
        results.add_pass("Volume up")
    else:
        results.add_fail("Volume up", result)
    
    # Test volume down
    result = system_volume.invoke({"action": "down"})
    if "Volume turned down" in result:
        results.add_pass("Volume down")
    else:
        results.add_fail("Volume down", result)
    
    # Test mute
    result = system_volume.invoke({"action": "mute"})
    if "Volume muted" in result:
        results.add_pass("Volume mute")
    else:
        results.add_fail("Volume mute", result)
    
    # Test invalid action
    result = system_volume.invoke({"action": "invalid"})
    if "Unknown volume action" in result:
        results.add_pass("Invalid action rejected")
    else:
        results.add_fail("Invalid action rejected", result)


def test_media_controls(results: TestResults):
    """Test media control tools"""
    print(Fore.CYAN + "\n--- Testing media_controls ---")
    
    from core.tools import media_play_pause, media_next, media_previous
    
    result = media_play_pause.invoke({})
    if "play/pause toggled" in result:
        results.add_pass("media_play_pause")
    else:
        results.add_fail("media_play_pause", result)
    
    result = media_next.invoke({})
    if "next track" in result:
        results.add_pass("media_next")
    else:
        results.add_fail("media_next", result)
    
    result = media_previous.invoke({})
    if "previous track" in result:
        results.add_pass("media_previous")
    else:
        results.add_fail("media_previous", result)


def test_search_knowledge_base(results: TestResults):
    """Test search_knowledge_base tool"""
    print(Fore.CYAN + "\n--- Testing search_knowledge_base ---")
    
    from core.tools import search_knowledge_base
    
    # The tool now handles non-interactive mode by falling back to plain text
    # Test search for known content (if brain.txt exists)
    result = search_knowledge_base.invoke({"query": "name"})
    if "knowledge base" in result.lower():
        results.add_pass("Returns knowledge base response")
    else:
        results.add_fail("Returns knowledge base response", result)
    
    # Test search for non-existent content
    result = search_knowledge_base.invoke({"query": "xyznonexistent123"})
    if "No information found" in result or "knowledge base" in result.lower():
        results.add_pass("Handles missing data gracefully")
    else:
        results.add_fail("Handles missing data gracefully", result)


def test_get_current_time(results: TestResults):
    """Test get_current_time tool"""
    print(Fore.CYAN + "\n--- Testing get_current_time ---")
    
    from core.tools import get_current_time
    import datetime
    
    result = get_current_time.invoke({})
    
    # Check format contains day and date
    today = datetime.datetime.now()
    if today.strftime("%A") in result:  # Day name
        results.add_pass("Contains day name")
    else:
        results.add_fail("Contains day name", result)
    
    if today.strftime("%B") in result:  # Month name
        results.add_pass("Contains month name")
    else:
        results.add_fail("Contains month name", result)


def test_get_weather(results: TestResults):
    """Test get_weather tool with mocked API"""
    print(Fore.CYAN + "\n--- Testing get_weather ---")
    
    from core.tools import get_weather
    
    # Mock API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cod": 200,
        "weather": [{"description": "clear sky"}],
        "main": {"temp": 25, "humidity": 60},
        "wind": {"speed": 5}
    }
    
    with patch('requests.get', return_value=mock_response):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}):
            result = get_weather.invoke({"city": "London"})
            
            if "weather in London" in result.lower() or "clear sky" in result:
                results.add_pass("Returns weather data")
            else:
                results.add_fail("Returns weather data", result)
    
    # Test missing API key
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""}, clear=True):
        # Remove the key temporarily
        original = os.environ.get("OPENWEATHER_API_KEY")
        if "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
        
        result = get_weather.invoke({"city": "London"})
        
        if original:
            os.environ["OPENWEATHER_API_KEY"] = original
        
        if "API key not found" in result or "Error" in result:
            results.add_pass("Handles missing API key")
        else:
            results.add_fail("Handles missing API key", result)


def test_write_to_screen(results: TestResults):
    """Test write_to_screen tool (Ghost Writer)"""
    print(Fore.CYAN + "\n--- Testing write_to_screen ---")
    
    from core.tools import write_to_screen
    import pyperclip
    
    # Reset mock
    pyperclip.copy = MagicMock()
    
    result = write_to_screen.invoke({"text": "Hello World"})
    
    if "pasted successfully" in result.lower() or "text" in result.lower():
        results.add_pass("Returns success message")
    else:
        results.add_fail("Returns success message", result)


def main():
    print(Fore.CYAN + "=" * 55)
    print(Fore.CYAN + "  ALFRED Tools Test Suite")
    print(Fore.CYAN + "=" * 55)
    
    results = TestResults()
    
    # Run all tests
    test_open_application(results)
    test_get_system_status(results)
    test_google_search(results)
    test_system_volume(results)
    test_media_controls(results)
    test_search_knowledge_base(results)
    test_get_current_time(results)
    test_get_weather(results)
    test_write_to_screen(results)
    
    # Summary
    print(Fore.CYAN + "\n" + "=" * 55)
    print(Fore.CYAN + "  TEST SUMMARY")
    print(Fore.CYAN + "=" * 55)
    
    total = results.passed + results.failed
    print(f"\n  Total Tests: {total}")
    print(Fore.GREEN + f"  Passed: {results.passed}")
    print(Fore.RED + f"  Failed: {results.failed}")
    
    if results.failed == 0:
        print(Fore.GREEN + f"\n  {SYM_CHECK} ALL TESTS PASSED!")
        return 0
    else:
        print(Fore.RED + f"\n  {SYM_FAIL} {results.failed} test(s) failed")
        print(Fore.YELLOW + "\n  Failed tests:")
        for name, reason in results.errors:
            print(Fore.YELLOW + f"    - {name}: {reason[:50]}...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
