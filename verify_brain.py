import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.getcwd())
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

try:
    print("Importing AlfredBrain...")
    from core.brain import AlfredBrain
    print("Initializing AlfredBrain...")
    brain = AlfredBrain()
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILURE: {e}")
