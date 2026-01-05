# 🎩 Project ALFRED - Adaptive Logical Framework for Responsive Execution & Decisions

A sophisticated voice-activated AI assistant with a **visual Arc Reactor overlay** that can **hear, speak, see, and act** on your computer. Like a loyal British butler, ALFRED provides professional, efficient assistance.

## 🎯 Features

### Core Capabilities
- 🎤 **Voice Input** - Uses Faster-Whisper for real-time speech-to-text
- 🔊 **Voice Output** - Microsoft Edge TTS for natural-sounding responses
- 👁️ **Computer Vision** - Can see and analyze your screen using Llama Vision
- 🛠️ **System Control** - Opens apps, checks status, controls volume, searches web
- 🎨 **Visual Overlay** - Iron Man-style Arc Reactor animation with status display

### Hybrid Architecture
- ☁️ **Cloud Brain** - Groq's Llama 3.3 70B for general conversation
- 💻 **Local Body** - Ollama's Hermes 3 for tool execution
- 🎨 **Vision Model** - Llama 4 Scout for image understanding
- 🌀 **Arc Reactor GUI** - PyQt6 animated overlay (60 FPS)

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Ollama installed with Hermes 3 model
- Groq API key (get from [console.groq.com](https://console.groq.com))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/NexionisJake/Project-ALFRED.git
cd Project-ALFRED

# Install dependencies
pip install -r requirements.txt

# Install Ollama model
ollama pull hermes3
```

### 3. Configuration

Create a `.env` file with your API key:
```env
GROQ_API_KEY=your_key_here
```

Customize settings in `config.py`:
```python
ASSISTANT_NAME = "ALFRED"
WAKE_WORD = "alfred"      # Change to your preferred name
VOICE_NAME = "en-GB-RyanNeural"  # British butler voice
MAX_MEMORY_DEPTH = 10     # Conversation memory
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

## 🎨 Visual Overlay Features

### Arc Reactor States
- **Idle** - Slow blue spinning rings (waiting for wake word)
- **Active** - Fast bright cyan spinning (processing/speaking)

### Status Messages
- 🎯 Activated - Wake word detected
- 🎤 Listening - Recording your voice
- 📝 [Command] - Shows what you said
- 🧠 Processing - AI is thinking
- ✓ Ready - Task completed
- 💤 Idle - Conversation ended

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

### Vision Commands
- *"Look at my screen and describe it"*
- *"What do you see?"*
- *"Read the error message"*

### Continuous Conversation
- Say **"Alfred"** → Start conversation
- Ask multiple questions **without repeating the wake word**
- Say **"thank you"** or **"goodbye"** → Exit conversation mode
- Arc Reactor returns to **slow idle** spin

## 📁 Project Structure

```
Project-ALFRED/
├── main.py                  # Main orchestrator with threading
├── overlay.py               # Arc Reactor GUI (PyQt6)
├── config.py                # Centralized settings (ALFRED identity)
├── tools.py                 # System tools
├── ears.py                  # Voice input (Whisper)
├── eyes.py                  # Computer vision
├── brain.txt                # Personal knowledge base
├── long_term_memory.json    # Persistent conversation memory
├── test_overlay.py          # GUI preview/testing
├── .env                     # API keys (NEVER commit)
├── .gitignore               # Git safety
└── requirements.txt         # Dependencies
```

## 🔧 Available Tools

1. **open_application** - Launch apps (Chrome, Notepad, Calculator, etc.)
2. **get_system_status** - Check CPU & RAM usage
3. **google_search** - Search the web
4. **system_volume** - Control volume (up/down/mute)
5. **media_controls** - Play/pause, next, previous track
6. **search_knowledge_base** - Query personal knowledge from brain.txt

## 🔒 Security Features

✅ API keys in `.env` (not hardcoded)  
✅ `.gitignore` prevents credential leaks  
✅ Limited conversation memory (prevents overflow)  
✅ Error handling for all external calls

## ⚙️ Customization

### Change Wake Word
```python
# In config.py
WAKE_WORD = "friday"  # or "computer", "alfred", etc.
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
# In overlay.py, line 48-50
color_base = QColor(0, 200, 255)  # Change RGB values
# Try: (255, 0, 100) for pink, (0, 255, 0) for green
```

### Move Overlay Position
```python
# In overlay.py, line 113
self.move(screen.width() - 450, screen.height() - 200)
# Adjust X and Y coordinates
# Top-left: self.move(20, 20)
# Top-right: self.move(screen.width() - 450, 20)
```

### Adjust Memory
```python
# In config.py
MAX_MEMORY_DEPTH = 20  # Remember last 20 messages
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists
- Check `.env` has no spaces: `GROQ_API_KEY=xxx`

### "Connection Error"
- Check internet connection
- Verify Ollama is running: `ollama list`

### "No module named..."
- Reinstall: `pip install -r requirements.txt`

### Microphone not working
- Check Windows microphone permissions
- Test with: `python ears.py`

## 📊 Performance Tips

- Use `tiny.en` Whisper model for speed (current setting)
- Adjust `MAX_MEMORY_DEPTH` lower if responses slow down
- Consider using `base.en` for better accuracy (slower)

## 🛣️ Roadmap

- [ ] Smart memory summarization
- [ ] Multiple language support
- [ ] Custom tool creation UI
- [ ] Mobile app integration
- [ ] Voice activity detection (no manual wake)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Credits

- **Groq** - Lightning-fast LLM inference
- **Ollama** - Local model hosting
- **Microsoft Edge TTS** - Natural voice synthesis
- **OpenAI Whisper** - Speech recognition

---

**Built with ❤️ for the future of personal AI assistants**
