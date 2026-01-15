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
from core.overlay import (OverlayWindow, COLOR_SYSTEM_OK, COLOR_WARNING, 
                          COLOR_CRITICAL, COLOR_ACTIVE_SCAN, COLOR_SUCCESS)

def demo_sequence(overlay):
    """Demo the different states with sentiment colors"""
    states = [
        ("ALFRED Online", 2000, COLOR_SYSTEM_OK),
        ("", 1000, COLOR_SYSTEM_OK),
        ("🎯 Target Acquired", 2000, COLOR_ACTIVE_SCAN),
        ("🎤 Listening...", 2000, COLOR_ACTIVE_SCAN),
        ("📝 Analysis in progress...", 2000, COLOR_SYSTEM_OK),
        ("⚠ Intrusion Detected", 2000, COLOR_WARNING),
        ("🧠 Decrypting...", 2000, COLOR_SYSTEM_OK),
        ("✗ System Failure", 2000, COLOR_CRITICAL),
        ("✓ Mission Accomplished", 2000, COLOR_SUCCESS),
        ("", 1000, COLOR_SYSTEM_OK),
        ("💤 Standby Mode", 2000, COLOR_SYSTEM_OK),
        ("", 0, COLOR_SYSTEM_OK)
    ]
    
    current = [0]
    
    def next_state():
        if current[0] < len(states):
            text, delay, color = states[current[0]]
            overlay.set_sentiment_color(color)
            overlay.set_text(text)
            print(f"State: {text if text else 'Hidden'} | Color: {color.name() if hasattr(color, 'name') else 'Custom'}")
            current[0] += 1
            if delay > 0:
                QTimer.singleShot(delay, next_state)
    
    next_state()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    overlay = OverlayWindow()
    overlay.show()
    
    print("WayneTech Overlay Demo")
    print("======================")
    print("Watch the bottom-right corner of your screen!")
    print("The system radar will cycle through different states.\n")
    
    # Start demo after 1 second
    QTimer.singleShot(1000, lambda: demo_sequence(overlay))
    
    sys.exit(app.exec())
