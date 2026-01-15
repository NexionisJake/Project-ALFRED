"""Configuration settings for ALFRED."""

# --- IDENTITY ---
ASSISTANT_NAME = "Alfred"
WAKE_WORD = "alfred"
# Sensitivity of wake word detection (0.0 to 1.0). 
# Lower value = easier to trigger (more false positives).
# Higher value = harder to trigger (fewer false positives).
WAKE_WORD_THRESHOLD = 0.5

# --- MODELS ---
CLOUD_MODEL = "llama-3.3-70b-versatile"
LOCAL_MODEL = "hermes3"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- AUDIO (The British Butler) ---
# 'en-GB-RyanNeural' is a crisp, professional British male voice.
# 'en-GB-SoniaNeural' is a British female option if you prefer.
VOICE_NAME = "en-GB-RyanNeural"  
WHISPER_SIZE = "tiny.en"

# --- MEMORY ---
MAX_MEMORY_DEPTH = 10

# --- PERFORMANCE / RESOURCE CONTROL ---
# Set to False to save ~1GB+ RAM by disabling semantic search features
ENABLE_VECTOR_MEMORY = False

# Set to False to skip loading local Ollama model (saves RAM if using cloud only)
ENABLE_LOCAL_MODEL = True

# Animation frame rates (lower = less CPU usage)
OVERLAY_ANIMATION_INTERVAL = 60    # ms (default was 30)
WAVEFORM_ANIMATION_INTERVAL = 100  # ms (default was 50)
DIAGNOSTICS_UPDATE_INTERVAL = 5000 # ms (default was 2000)

# --- VISION KEYWORDS ---
VISION_KEYWORDS = ["look", "see", "screen", "what is this", "describe", "read"]

# --- SYSTEM KEYWORDS ---
SYSTEM_KEYWORDS = ["open", "start", "launch", "check", "cpu", "ram", "memory", "system", "pc", "search", "google", "volume", 
                   "play", "pause", "skip", "next", "previous", "stop", "resume", "song", "track", "music", "video",
                   "wifi", "password", "knowledge", "remember", "what is my", "tell me about", "dog", "pet", "favorite",
                   "write", "type", "code", "input", "paste",  # Typing keywords
                   "weather", "temperature", "forecast", "climate"]  # Weather keywords

QUESTION_STARTERS = ["what", "who", "where", "why", "when", "how", "explain", "tell", "can", "could", "would", "should", "please"]
