import sys
import time
import keyboard
from dotenv import load_dotenv # pip install python-dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from colorama import Fore, init

# Load Environment Variables
load_dotenv()

# Import Core Modules
from core.brain import AlfredBrain
from core.voice import AlfredVoice
from core.overlay import OverlayWindow, COLOR_SYSTEM_OK, COLOR_ACTIVE_SCAN
from core.ears import listen_and_transcribe, listen_for_wake_word, OPENWAKEWORD_AVAILABLE
import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

init(autoreset=True)


class AlfredWorker(QThread):
    """
    Background thread that handles Listening -> Thinking -> Acting.
    """
    status_update = pyqtSignal(str)
    color_update = pyqtSignal(object)
    wake_signal = pyqtSignal() # external wake trigger
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.brain = AlfredBrain()
        self.voice = AlfredVoice()
        
        # Flag for manual wake
        self.manual_wake = False
        self.wake_signal.connect(self.trigger_wake)
        
    def trigger_wake(self):
        self.manual_wake = True

    def run(self):
        """Main execution loop."""
        self.status_update.emit(f"{config.WAKE_WORD.capitalize()} Online")
        self.voice.speak(f"{config.WAKE_WORD.capitalize()} is online.")
        
        print(Fore.WHITE + "\n-----------------------------------")
        print(Fore.WHITE + "   A.L.F.R.E.D. SYSTEM ONLINE")
        print(Fore.WHITE + "   (Modular Architecture v2.0)")
        print(Fore.WHITE + "-----------------------------------\n")
        
        in_conversation = False
        
        while self.running:
            try:
                # 1. Listen Logic
                user_text = ""
                
                if not in_conversation:
                    # Check manual wake first
                    if self.manual_wake:
                        user_text = config.WAKE_WORD
                        self.manual_wake = False
                    
                    # Wake Word Check (if not manual)
                    elif OPENWAKEWORD_AVAILABLE:
                        # Use timeout=1 to unblock periodically and check signals
                        if listen_for_wake_word(config.WAKE_WORD, timeout=1):
                            user_text = config.WAKE_WORD # Trigger activation
                        else:
                            continue
                    else:
                        # Fallback Whisper
                        audio_text = listen_and_transcribe()
                        if audio_text and config.WAKE_WORD.lower() in audio_text.lower():
                            user_text = audio_text
                        else:
                            continue
                else:
                    # Active Conversation Listening
                    user_text = listen_and_transcribe()
                    
                if not user_text and not self.manual_wake:
                    if in_conversation:
                        print(Fore.CYAN + "💤 Conversation timeout.")
                        self.status_update.emit("💤 Idle")
                        in_conversation = False
                    continue

                # 2. Activation / Interaction
                if not in_conversation:
                    print(Fore.WHITE + f"\n🎯 Wake Word Detected!")
                    self.status_update.emit("🎯 Activated")
                    self.voice.speak("Yes?")
                    in_conversation = True
                    
                    # Listen for command immediately
                    self.status_update.emit("🎤 Listening...")
                    user_text = listen_and_transcribe()
                    if not user_text:
                        self.voice.speak("I didn't hear a command, Sir.")
                        in_conversation = False
                        self.status_update.emit("")
                        continue

                # 3. Process Command
                print(Fore.WHITE + f"Command: {user_text}")
                self.status_update.emit(f"📝 {user_text[:30]}..." if len(user_text) > 30 else f"📝 {user_text}")
                
                # Check for exit
                if "exit" in user_text.lower() or "quit" in user_text.lower():
                    self.voice.speak("Shutting down, Sir.")
                    self.status_update.emit("👋 Shutting down...")
                    self.running = False
                    QApplication.instance().quit()
                    break

                # UI Callback
                def update_ui(text, color):
                    self.status_update.emit(text)
                    self.color_update.emit(color)

                # 4. THINK & ACT
                # Check Vision
                vision_keywords = config.VISION_KEYWORDS
                if any(k in user_text.lower() for k in vision_keywords):
                    from core.eyes import take_screenshot
                    self.status_update.emit("👀 Looking...")
                    self.voice.speak("Taking a look.")
                    img = take_screenshot()
                    response = self.brain.process_vision(user_text, img, update_ui)
                else:
                    self.status_update.emit("🧠 Thinking...")
                    response = self.brain.think(user_text, update_ui)
                
                # 5. SPEAK
                self.voice.speak(response)
                
                self.status_update.emit("🎤 Listening...")
                print(Fore.CYAN + "🎤 Listening for follow-up...")

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(Fore.RED + f"Critical Loop Error: {e}")
                self.status_update.emit("❌ System Error")
                time.sleep(2)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        overlay = OverlayWindow()
        overlay.show()
        
        worker = AlfredWorker()
        worker.status_update.connect(overlay.set_text)
        worker.color_update.connect(overlay.set_sentiment_color)
        
        # Connect Wake Signal
        overlay.wake_request.connect(worker.wake_signal.emit)
        
        worker.start()
        
        sys.exit(app.exec())
        
    except Exception as e:
        # Global Crash Handler
        error_msg = f"CRITICAL CRASH: {str(e)}"
        print(Fore.RED + error_msg)
        with open("crash.log", "w") as f:
            f.write(f"{time.ctime()}: {error_msg}\n")
        sys.exit(1)