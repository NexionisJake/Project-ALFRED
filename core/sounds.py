"""
UI Sound Effects for ALFRED - WayneTech Edition.
Provides subtle audio feedback for interactions.
"""

import threading

# Sound enabled flag (can be toggled)
SOUNDS_ENABLED = True


def _play_tone(frequency, duration_ms):
    """Play a simple tone using winsound (Windows only)."""
    if not SOUNDS_ENABLED:
        return
    
    try:
        import winsound
        # Run in thread to avoid blocking
        def play():
            try:
                winsound.Beep(frequency, duration_ms)
            except Exception:
                pass
        
        thread = threading.Thread(target=play, daemon=True)
        thread.start()
    except ImportError:
        # winsound not available (non-Windows)
        pass


def play_click():
    """Play a subtle click sound for wake activation."""
    _play_tone(800, 50)


def play_ping():
    """Play a radar ping sound."""
    _play_tone(1200, 100)


def play_boot_beep():
    """Play boot sequence beep."""
    _play_tone(600, 80)


def play_success():
    """Play success/confirmation tone."""
    def play():
        import time
        _play_tone(800, 80)
        time.sleep(0.1)
        _play_tone(1000, 80)
    
    thread = threading.Thread(target=play, daemon=True)
    thread.start()


def play_alert():
    """Play alert/warning tone."""
    def play():
        import time
        _play_tone(400, 150)
        time.sleep(0.1)
        _play_tone(400, 150)
    
    thread = threading.Thread(target=play, daemon=True)
    thread.start()


def set_sounds_enabled(enabled):
    """Enable or disable all UI sounds."""
    global SOUNDS_ENABLED
    SOUNDS_ENABLED = enabled


if __name__ == "__main__":
    import time
    print("Testing ALFRED UI sounds...")
    
    print("Click...")
    play_click()
    time.sleep(0.3)
    
    print("Ping...")
    play_ping()
    time.sleep(0.3)
    
    print("Boot beep...")
    play_boot_beep()
    time.sleep(0.3)
    
    print("Success...")
    play_success()
    time.sleep(0.5)
    
    print("Alert...")
    play_alert()
    time.sleep(0.5)
    
    print("Done!")
