"""
Test script to verify the Sentiment Engine implementation
This demonstrates how the Arc Reactor changes color based on context
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from overlay import OverlayWindow, COLOR_HAPPY, COLOR_ALERT, COLOR_ERROR, COLOR_NEUTRAL

def test_sentiment_colors():
    """Cycle through different sentiment colors to test the visual feedback"""
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.show()
    
    # Test sequence: Show different sentiments with delays
    test_cases = [
        (1000, "System Initializing...", COLOR_NEUTRAL),
        (3000, "[HAPPY] Successfully connected to all systems!", COLOR_HAPPY),
        (6000, "[ALERT] Warning: High CPU usage detected", COLOR_ALERT),
        (9000, "[ERROR] Failed to access system file", COLOR_ERROR),
        (12000, "[NEUTRAL] Everything is back to normal", COLOR_NEUTRAL),
        (15000, "Test complete - All colors working!", COLOR_HAPPY),
    ]
    
    for delay, text, color in test_cases:
        # Remove sentiment tags for display
        display_text = text.replace("[HAPPY] ", "").replace("[ALERT] ", "").replace("[ERROR] ", "").replace("[NEUTRAL] ", "")
        QTimer.singleShot(delay, lambda t=display_text, c=color: update_overlay(overlay, t, c))
    
    # Close after all tests
    QTimer.singleShot(18000, app.quit)
    
    sys.exit(app.exec())

def update_overlay(overlay, text, color):
    """Update overlay with text and color"""
    print(f"Setting: {text} | Color: {color.name()}")
    overlay.set_text(text)
    overlay.set_sentiment_color(color)

if __name__ == "__main__":
    print("Testing Sentiment Engine...")
    print("Watch the Arc Reactor change colors:")
    print("  - CYAN (Blue) = Neutral")
    print("  - GREEN = Happy/Success")
    print("  - ORANGE = Alert/Warning")
    print("  - RED = Error/Danger")
    print("\nStarting test sequence...\n")
    test_sentiment_colors()
