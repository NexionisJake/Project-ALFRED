import base64
import os
import time
import mss
import mss.tools
from io import BytesIO
from PIL import Image

def take_screenshot():
    """
    Takes a screenshot of the main screen and converts it to a base64 string
    that the API can understand. Uses mss for 10x faster capture (~10ms vs ~100ms).
    """
    # 1. Capture the screen using mss (MUCH faster than pyautogui)
    print("📸 Taking a look...")
    
    with mss.mss() as sct:
        # Capture the primary monitor (monitor 1)
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image for processing
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    # 2. Resize specifically for AI (Optimization)
    # Sending full 4k/1080p images is slow. 
    # Resizing to max 1024x1024 preserves detail but speeds up upload by 4x.
    img.thumbnail((1024, 1024))
    
    # 3. Save to memory buffer (not disk) to be faster
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    
    # 4. Encode to Base64
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

# Test it independently
if __name__ == "__main__":
    s = take_screenshot()
    print(f"Screenshot taken! Base64 length: {len(s)}")
