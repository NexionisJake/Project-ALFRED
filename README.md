# 🎩 Project ALFRED - Adaptive Logical Framework for Responsive Execution & Decisions

A sophisticated voice-activated AI assistant with a **visual Arc Reactor overlay** that can **hear, speak, see, and act** on your computer. Like a loyal British butler, ALFRED provides professional, efficient assistance.

## 🎯 Features

### Core Capabilities
- 🎤 **Advanced Voice Input** - Faster-Whisper with efficient OpenWakeWord detection (10x faster wake word recognition)
- 🔊 **Voice Output** - Microsoft Edge TTS with ESC interrupt support and markdown cleaning
- 👁️ **Computer Vision** - AI-powered screen analysis using Llama Vision with auto-code extraction
- 🛠️ **System Control** - 11 integrated tools including app launching, system monitoring, media controls, weather, and typing automation
- 🎨 **Visual Overlay** - Advanced Arc Reactor with sentiment-aware colors, auto-scrolling text bubbles, and smooth animations
- ✍️ **Ghost Writer** - AI can write/paste code directly into your active window (perfect for LeetCode, VS Code)
- 💾 **Persistent Memory** - Conversation history saved to disk and reloaded between sessions

### Hybrid Architecture
- ☁️ **Cloud Brain** - Groq's Llama 3.3 70B for general conversation with sentiment analysis
- 💻 **Local Body** - Ollama's Hermes 3 for tool execution and function calling
- 🎨 **Vision Model** - Llama 4 Scout (17B) for advanced image understanding
- 🌀 **Arc Reactor GUI** - PyQt6 animated overlay (60 FPS) with dynamic emotional states
- 🔄 **Continuous Conversation** - Stays active without repeating wake word until you say goodbye

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** (Download from [python.org](https://python.org))
- **Ollama** installed with Hermes 3 model ([ollama.com](https://ollama.com))
- **Groq API key** (Free tier available at [console.groq.com](https://console.groq.com))
- **OpenWeather API key** (Optional, for weather features - [openweathermap.org](https://openweathermap.org/api))
- **Windows OS** (Currently optimized for Windows, Linux/Mac support planned)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/NexionisJake/Project-ALFRED.git
cd Project-ALFRED

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama model (required for local tool execution)
ollama pull hermes3

# Verify installation
python preflight_check.py  # Runs system diagnostics
```

### 3. Configuration

Create a `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_key_here
OPENWEATHER_API_KEY=your_weather_key_here  # Optional: for weather features
```

Customize settings in `config.py`:
```python
ASSISTANT_NAME = "Alfred"
WAKE_WORD = "alfred"      # Change to your preferred name
VOICE_NAME = "en-GB-RyanNeural"  # British butler voice
MAX_MEMORY_DEPTH = 10     # Conversation memory (persistent across sessions)
CLOUD_MODEL = "llama-3.3-70b-versatile"  # Groq cloud model
LOCAL_MODEL = "hermes3"   # Ollama local model
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Vision AI
WHISPER_SIZE = "base"     # "tiny.en" for speed, "base" for accuracy
```

### 4. Run

```bash
python main.py
```

**You will see:**
- 🌀 **Animated Arc Reactor** in the bottom-right corner
- 💬 **Neon text bubble** showing ALFRED's status
- Console banner: "A.L.F.R.E.D. SYSTEM ONLINE"
- Console output for debugging

## � Advanced Features Deep Dive

### 1. Sentiment-Aware Interface
ALFRED now analyzes the emotional context of responses and changes the Arc Reactor color:
- **Green Glow** - Successful operations (file saved, app opened)
- **Orange Glow** - Warnings or alerts (low battery, connection issues)
- **Red Glow** - Errors or critical issues
- **Cyan Glow** - Neutral informational responses

The AI automatically tags responses with sentiment markers like `[HAPPY]`, `[ALERT]`, `[ERROR]` which the GUI interprets.

### 2. Vision + Code Extraction Workflow
When you show ALFRED a coding problem:
1. **Screen Capture** - Takes a screenshot using ultra-fast `mss` library (10ms)
2. **Vision Analysis** - Llama 4 Scout analyzes the problem
3. **Code Generation** - AI writes the solution
4. **Auto-Extraction** - Parses code blocks from response (supports Python, C++, Java, JavaScript)
5. **Smart Paste** - Automatically pastes to your active window (VS Code, LeetCode, etc.)

Just say: *"Look at this problem and write the code"* - solution appears instantly!

### 3. Persistent Conversation Memory
- All conversations auto-save to `long_term_memory.json`
- When restarted, ALFRED remembers previous discussions
- Memory serialization handles HumanMessage, AIMessage, SystemMessage types
- Automatic memory cleanup prevents token overflow
- Smart summarization planned for v2.0

### 4. Continuous Conversation Mode
- Say wake word once → Conversation starts
- Ask unlimited follow-up questions without repeating wake word
- Say "thank you", "goodbye", or "that's all" to exit
- Visual feedback shows when conversation is active (fast spinning reactor)
- Automatic timeout after prolonged silence

### 5. OpenWakeWord Integration
- **10x faster** than Whisper-based wake word detection
- Uses optimized ONNX models for real-time processing
- Runs continuously without blocking
- Fallback to Whisper if library not installed
- Configurable confidence threshold (default: 0.5)

### 6. ESC Interrupt System
While ALFRED is speaking:
- Press **ESC** to stop speech immediately
- Useful for long responses or errors
- Microphone becomes ready faster
- Audio cleanup prevents file lock issues

### 7. Ghost Writer Intelligence
The `write_to_screen` tool includes:
- **Clipboard Safety** - Uses pyperclip for reliable cross-platform pasting
- **Smart Delays** - 0.5s delay gives you time to focus correct window
- **Format Preservation** - Maintains indentation and line breaks
- **Integration with Vision** - Auto-detects when to paste code from image analysis

## �🎨 Visual Overlay Features

### Arc Reactor States
- **Idle** - Slow blue/cyan spinning rings (waiting for wake word)
- **Active** - Fast bright cyan spinning with wavy distortion (processing/speaking)
- **Sentiment Colors** (NEW!):
  - 🟢 **Green** - Happy/Success (task completed successfully)
  - 🟠 **Orange** - Alert/Warning (potential issues)
  - 🔴 **Red** - Error (something went wrong)
  - 🔵 **Cyan** - Neutral (default informational state)

### Status Messages
- 🎯 Activated - Wake word detected
- 🎤 Listening - Recording your voice
- 📝 [Command] - Shows what you said (auto-scrolling for long text)
- 🧠 Processing - AI is thinking
- ✓ Ready - Task completed
- 💤 Idle - Conversation ended

### Advanced GUI Features (NEW!)
- **Auto-scrolling Text Bubble** - Expands/scrolls for long responses
- **Typewriter Effect** - Smooth character-by-character display
- **Mouse Wheel Scrolling** - Scroll through long AI responses
- **Dynamic Sizing** - Bubble adapts to message length (80-300px height)
- **85% Window Opacity** - Subtle transparency for desktop visibility

### Test the Overlay
Preview the visual interface without the voice assistant:
```bash
python test_overlay.py
```

## 🎮 Usage Examples

### Wake Word Activation
1. **Look at bottom-right corner** - Arc Reactor spinning slowly (idle)
2. Say **"Alfred"** 
3. Arc Reactor spins **fast** - Text shows: *"🎯 Activated"*
4. ALFRED speaks: *"Yes?"* (in British accent)
5. Give your command - Text shows: *"🎤 Listening..."*

### System Control
- *"Open Chrome"* → Opens browser, status: *"✓ Ready"*
- *"Check system status"* → Shows CPU/RAM
- *"Turn volume up"*
- *"Search for Python tutorials"* → Opens Google search
- *"What's the time?"* → Reads current date and time
- *"Play music"* / *"Next song"* / *"Pause"* → Media controls

### Vision Commands
- *"Look at my screen and describe it"*
- *"What do you see?"*
- *"Read the error message"*
- *"Look at this code and fix it"* → AI analyzes and explains
- *"Look at this problem and write the code"* → **Auto-pastes solution!**

### Ghost Writer (NEW!)
- *"Write a Python function to reverse a string"* → Types/pastes code instantly
- *"Look at this LeetCode problem and write the solution"* → Vision + Auto-paste
- *"Type 'Hello World' in capital letters"* → Pastes text

### Weather & Knowledge Base
- *"What's the weather in London?"* → Real-time weather data
- *"What's my WiFi password?"* → Searches brain.txt knowledge base
- *"Tell me about my project"* → Retrieves personal information

### Continuous Conversation
- Say **"Alfred"** → Start conversation
- Ask multiple questions **without repeating the wake word**
- Say **"thank you"** or **"goodbye"** → Exit conversation mode
- Arc Reactor returns to **slow idle** spin
- Pressing **ESC** during speech → Interrupts current response

## 📁 Project Structure

```
Project-ALFRED/
├── main.py                  # Main orchestrator with threading & conversation loop
├── overlay.py               # Arc Reactor GUI with sentiment colors & auto-scroll
├── config.py                # Centralized settings (models, voice, wake word)
├── tools.py                 # 11 system tools (apps, media, weather, typing)
├── ears.py                  # Voice input (Whisper + OpenWakeWord)
├── eyes.py                  # Computer vision (mss fast screenshots)
├── brain.txt                # Personal knowledge base (WiFi, preferences, etc.)
├── long_term_memory.json    # Persistent conversation memory (auto-saved)
├── test_overlay.py          # GUI preview/testing
├── test_sentiment.py        # Test sentiment color system
├── preflight_check.py       # System diagnostics tool
├── .env                     # API keys (NEVER commit)
├── .gitignore               # Git safety
└── requirements.txt         # Dependencies
```

## 🔧 Available Tools

1. **open_application** - Launch apps (Chrome, Notepad, Calculator, VS Code, Spotify, etc.)
2. **get_system_status** - Check CPU & RAM usage with detailed metrics
3. **google_search** - Search the web and auto-open browser
4. **system_volume** - Control volume (up/down/mute)
5. **media_play_pause** - Toggle play/pause for any media player
6. **media_next** - Skip to next track/video
7. **media_previous** - Go back to previous track/video
8. **search_knowledge_base** - Query personal knowledge from brain.txt
9. **get_current_time** - Returns current date, time, and day of the week
10. **get_weather** - Real-time weather data for any city (OpenWeather API)
11. **write_to_screen** (NEW!) - Types/pastes text into active window (perfect for coding assistance)

## 🔒 Security Features

✅ API keys in `.env` (not hardcoded)  
✅ `.gitignore` prevents credential leaks  
✅ Limited conversation memory (prevents overflow)  
✅ Error handling for all external API calls  
✅ Persistent memory with JSON serialization (safe file I/O)  
✅ Input sanitization for tool execution  
✅ Separate cloud (Groq) and local (Ollama) model isolation  
✅ Safe clipboard operations for Ghost Writer feature

## ⚙️ Customization

### Change Wake Word
```python
# In config.py
WAKE_WORD = "friday"  # or "computer", "alfred", "jarvis", etc.
```

### Change Voice
```python
# In config.py
VOICE_NAME = "en-GB-RyanNeural"   # British Male (default ALFRED)
# Other options: 
# "en-US-GuyNeural" (American Male)
# "en-US-JennyNeural" (Female)
# "en-GB-SoniaNeural" (British Female)
```

### Customize Arc Reactor Colors
```python
# In overlay.py, COLOR constants at top
COLOR_HAPPY = QColor(0, 255, 100)   # Green - Success
COLOR_ALERT = QColor(255, 165, 0)   # Orange - Warning
COLOR_ERROR = QColor(255, 50, 50)   # Red - Error
COLOR_NEUTRAL = QColor(0, 255, 255) # Cyan - Default
# Try: (255, 0, 100) for pink, (0, 255, 0) for green
```

### Move Overlay Position
```python
# In overlay.py, OverlayWindow.__init__ (around line 370)
window_x = screen.width() - 600 - 20  # 20px from right
window_y = screen.height() - 200 - 50 # 50px from bottom
# Top-left: self.move(20, 20)
# Top-right: self.move(screen.width() - 600, 20)
```

### Adjust Memory & Performance
```python
# In config.py
MAX_MEMORY_DEPTH = 20  # Remember last 20 messages (default: 10)
WHISPER_SIZE = "tiny.en"  # Fastest (default: "base")
# Options: "tiny.en" (fastest) → "base" (balanced) → "small.en" (accurate)
```

### Adjust Text Bubble Size
```python
# In overlay.py, TechBubble class
self.MAX_WIDTH = 400   # Maximum width (default: 400)
self.MAX_HEIGHT = 300  # Max height before scrolling (default: 300)
self.MIN_HEIGHT = 80   # Minimum height (default: 80)
```

### Add Custom Knowledge
Edit `brain.txt` with personal information:
```
My WiFi password is "MyPassword123"
My favorite IDE is VS Code
My GitHub username is YourUsername
My pet's name is Buddy
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in project root
- Check `.env` has no spaces: `GROQ_API_KEY=xxx`
- Verify the key is valid at [console.groq.com](https://console.groq.com)

### "Connection Error" / "Empty Response"
- Check internet connection
- Verify Groq API service is online
- Ensure Ollama is running: `ollama list`
- Try restarting Ollama: `ollama serve`

### "No module named..."
- Reinstall all dependencies: `pip install -r requirements.txt`
- For openwakeword issues: `pip install openwakeword --upgrade`
- Python 3.10+ required

### Microphone not working
- Check Windows microphone permissions (Settings → Privacy → Microphone)
- Test microphone: `python ears.py`
- Adjust `SILENCE_THRESHOLD` in ears.py if cuts off too early (default: 500)

### Speech interruption (ESC) not working
- Ensure `keyboard` module is installed: `pip install keyboard`
- Run script with administrator privileges on Windows
- Alternative: Wait for speech to complete naturally

### Vision commands failing
- Verify you're using Llama 4 Scout model (supports vision)
- Check Groq API quota hasn't been exceeded
- Ensure `mss` library is installed: `pip install mss`

### GUI not appearing / Overlay position wrong
- Check `PyQt6` installation: `pip install PyQt6 --upgrade`
- Adjust position in overlay.py (window_x, window_y variables)
- Test overlay separately: `python test_overlay.py`

### Weather tool not working
- Add `OPENWEATHER_API_KEY` to `.env` file
- Get free API key at [openweathermap.org/api](https://openweathermap.org/api)
- Check city name spelling

### Ghost Writer (write_to_screen) not pasting
- Click/focus the target window first (3-second delay for safety)
- Ensure `pyautogui` and `pyperclip` are installed
- Test manually: `import pyperclip; pyperclip.copy("test")`

## 📊 Performance Tips

- **Wake Word Detection**: OpenWakeWord is 10x faster than Whisper fallback - ensure it's installed
- **Whisper Model**: Use `tiny.en` for speed (current), `base` for accuracy (recommended), `small.en` for best quality
- **Memory Management**: Reduce `MAX_MEMORY_DEPTH` (default: 10) if responses slow down
- **Screen Capture**: Using `mss` library (10ms vs 100ms with pyautogui) for 10x faster screenshots
- **Vision Optimization**: Images resized to 1024x1024 before upload (4x faster, same quality)
- **Persistent Memory**: Conversations auto-save to `long_term_memory.json` - clear file to reset
- **ESC Interrupt**: Press ESC during speech to skip waiting for completion
- **CPU Usage**: Base Whisper model uses ~15-20% CPU, tiny uses ~5-10%

## 🛣️ Roadmap

### Completed ✅
- [x] Persistent memory across sessions
- [x] Sentiment-aware visual feedback
- [x] Efficient wake word detection (OpenWakeWord)
- [x] Auto-scrolling text interface
- [x] Ghost Writer (code/text pasting automation)
- [x] Weather integration
- [x] Speech interruption (ESC key)
- [x] Vision + Code extraction workflow
- [x] Continuous conversation mode

### In Progress 🚧
- [ ] Smart memory summarization (automatic conversation compression)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Custom tool creation UI (add your own functions)
- [ ] Voice activity detection (eliminate manual wake word)

### Planned 🎯
- [ ] Mobile app integration (control from phone)
- [ ] Browser extension (web context awareness)
- [ ] Calendar & email integration
- [ ] Smart home device control
- [ ] Multiple AI personality profiles
- [ ] Local vision model option (fully offline mode)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Credits

- **Groq** - Lightning-fast LLM inference (Llama 3.3 70B & Llama 4 Scout 17B)
- **Ollama** - Local model hosting (Hermes 3)
- **Microsoft Edge TTS** - Natural voice synthesis with British accent
- **OpenAI Whisper / Faster-Whisper** - Industry-leading speech recognition
- **OpenWakeWord** - Efficient wake word detection framework
- **PyQt6** - Modern GUI framework for overlay interface
- **MSS (Multi-Screen-Shots)** - Ultra-fast screenshot library
- **OpenWeatherMap** - Real-time weather data API
- **LangChain** - AI orchestration framework

---

**Built with ❤️ for the future of personal AI assistants**

*"A good butler never tells." - ALFRED*
