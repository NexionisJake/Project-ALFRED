from core.wake_word import WakeWordDetector
import config
from colorama import init, Fore

init(autoreset=True)

print("Testing WakeWordDetector initialization...")
try:
    detector = WakeWordDetector()
    print(f"Detector Enabled: {detector.enabled}")
    print(f"Active Wake Word: {detector.wake_word}")
    if detector.enabled:
        print(f"Model Map for current word: {detector.model_map.get(detector.wake_word.lower())}")
        print(f"Configured Threshold: {config.WAKE_WORD_THRESHOLD}")
    else:
        print("Detector disabled. Check logs above.")
except Exception as e:
    print(Fore.RED + f"CRITICAL: Failed to init detector: {e}")
