"""Configuration settings for ALFRED."""

# --- IDENTITY ---
ASSISTANT_NAME = "ALFRED"
WAKE_WORD = "alfred"

# --- MODELS ---
CLOUD_MODEL = "llama-3.3-70b-versatile"
LOCAL_MODEL = "hermes3"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- AUDIO ---
VOICE_NAME = "en-GB-RyanNeural"  # Switched to British Male (Classic Alfred vibe)
# Options: "en-US-GuyNeural" (American), "en-GB-RyanNeural" (British)
WHISPER_SIZE = "tiny.en"        # Faster-Whisper Model

# --- MEMORY ---
MAX_MEMORY_DEPTH = 10           # Keep last 10 messages to save RAM

# --- VISION ---
VISION_KEYWORDS = ["look", "see", "screen", "what is this", "describe", "read"]

# --- SYSTEM ---
SYSTEM_INSTRUCTION = """
You are ALFRED (Adaptive Logical Framework for Responsive Execution & Decisions).
You are a loyal, sophisticated, and efficient AI assistant.
Your tone should be professional, concise, and polite (like a British butler).
"""

SYSTEM_KEYWORDS = ["open", "start", "launch", "check", "cpu", "ram", "memory", "system", "pc", "search", "google", "volume", 
                   "play", "pause", "skip", "next", "previous", "stop", "resume", "song", "track", "music", "video",
                   "wifi", "password", "knowledge", "remember", "what is my", "tell me about", "dog", "pet", "favorite"]
QUESTION_STARTERS = ["what", "who", "where", "why", "when", "how", "explain", "tell", "can", "could", "would", "should", "please"]
