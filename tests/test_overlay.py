"""
Quick test to preview the Jarvis Arc Reactor overlay.
Run this to see the GUI without the full voice assistant.
"""
import sys
import os
# Add the parent directory (Project JHANGYA) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.overlay import OverlayWindow

def demo_sequence(overlay):
    """Demo the different states"""
    states = [
        ("Jarvis Online", 2000),
        ("", 1000),
        ("🎯 Wake word detected", 2000),
        ("🎤 Listening...", 2000),
        ("📝 Search for AI news...", 2000),
        ("🧠 Processing...", 2000),
        ("✓ Task complete", 2000),
        ("", 1000),
        ("💤 Idle mode", 2000),
        ("", 0)
    ]
    
    current = [0]
    
    def next_state():
        if current[0] < len(states):
            text, delay = states[current[0]]
            overlay.set_text(text)
            print(f"State: {text if text else 'Hidden'}")
            current[0] += 1
            if delay > 0:
                QTimer.singleShot(delay, next_state)
    
    next_state()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    overlay = OverlayWindow()
    overlay.show()
    
    print("Jarvis Overlay Demo")
    print("==================")
    print("Watch the bottom-right corner of your screen!")
    print("The arc reactor will cycle through different states.\n")
    
    # Start demo after 1 second
    QTimer.singleShot(1000, lambda: demo_sequence(overlay))
    
    sys.exit(app.exec())
