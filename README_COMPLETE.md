# 🤖 PROJECT JHANGYA - Advanced AI Assistant

A fully integrated, multi-modal AI assistant with voice control, vision capabilities, and sentiment-aware visual feedback.

## 🌟 Features

### Core Systems
- **🧠 Hybrid Brain**: Groq Cloud (Llama 3.3 70B) + Ollama Local (Hermes 3)
- **👂 Ears**: OpenWakeWord + Faster-Whisper voice recognition
- **👁️ Eyes**: Llama 4 Scout 17B vision model for screen analysis
- **💬 Voice**: Edge TTS for natural speech output
- **🎨 Face**: PyQt6 Arc Reactor GUI with sentiment-aware colors

### 🛠️ Capabilities (8 Tools)

1. **Application Launcher** - Open apps like Chrome, Spotify, VS Code
2. **System Monitor** - Check CPU and RAM usage
3. **Web Search** - Instant Google searches
4. **Volume Control** - Adjust or mute system volume
5. **Media Controls** - Play/pause, next/previous track (works with Spotify, YouTube, etc.)
6. **Personal Knowledge Base** - Query your custom brain.txt file

### 🎭 Sentiment Engine

The Arc Reactor changes color based on context:
- **🔵 Cyan (Blue)** - Neutral/Default state
- **🟢 Green** - Success/Positive responses
- **🟠 Orange** - Warnings/Alerts
- **🔴 Red** - Errors/Problems

### 💾 Long-Term Memory

- Conversations persist across sessions via `long_term_memory.json`
- Automatic summarization every 10 messages
- Loads previous context on startup

## 📋 Requirements

```bash
# Install dependencies
pip install -r requirements.txt
```

### Required API Keys

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Local Models (Ollama)

Install Ollama and pull required models:
```bash
ollama pull hermes3
ollama pull llama3.2-vision
```

## 🚀 Quick Start

1. **Pre-Flight Check**
```bash
python preflight_check.py
```

2. **Launch System**
```bash
python main.py
```

3. **Wake Word Activation**
   - Say "Jarvis" to activate
   - Speak your command
   - Say "thank you" or "goodbye" to end conversation

## 📝 Personal Knowledge Base

Edit `brain.txt` to add your personal information:
```
My name is [Your Name].
My WiFi password is [Password].
My favorite [thing] is [value].
```

The AI can then recall this information when asked!

## 🧪 Testing

### Test Sentiment Colors
```bash
python test_sentiment.py
```

### Test Individual Components
```bash
python overlay.py  # Test GUI overlay
python ears.py     # Test voice input
python eyes.py     # Test vision capture
```

## 📂 Project Structure

```
Project JHANGYA/
├── main.py              # Main orchestrator
├── tools.py             # 8 AI tools
├── overlay.py           # GUI with sentiment engine
├── ears.py              # Voice input (Whisper)
├── eyes.py              # Vision capture
├── config.py            # Configuration
├── brain.txt            # Personal knowledge base
├── .env                 # API keys
├── long_term_memory.json  # Conversation history
└── requirements.txt     # Dependencies
```

## 🎮 Example Commands

**Application Control:**
- "Jarvis, open Spotify"
- "Launch calculator"
- "Start Chrome"

**System Commands:**
- "Check system status"
- "Volume up"
- "Mute the system"

**Media Control:**
- "Pause the music"
- "Skip this song"
- "Go back to the previous track"

**Personal Knowledge:**
- "What's my WiFi password?"
- "What's my favorite music genre?"
- "Tell me about my project"

**Vision:**
- "Look at my screen and describe what you see"
- "What's in this image?"
- "Read the text on my screen"

**Conversation:**
- "Tell me a joke"
- "What's 2+2?"
- "Explain quantum physics"

## 🎨 Sentiment Examples

- **Green Response**: "Jarvis, play music" → "✓ Successfully launched Spotify" (GREEN)
- **Orange Warning**: "Should I delete system32?" → "⚠️ That's dangerous!" (ORANGE)
- **Red Error**: "Open nonexistent_app" → "❌ Failed to launch" (RED)

## 🔧 Configuration

Edit `config.py` to customize:
- Models (cloud/local/vision)
- Wake word
- Memory depth
- Voice settings
- System keywords

## 🐛 Troubleshooting

**Issue**: Microphone not working
- Check `ears.py` isn't running separately
- Verify microphone permissions

**Issue**: GUI not showing
- Ensure PyQt6 is installed
- Run `python test_sentiment.py` to test overlay

**Issue**: Tools not working
- Run `python preflight_check.py`
- Verify all imports are successful

**Issue**: API errors
- Check `.env` file has valid GROQ_API_KEY
- Verify Ollama is running: `ollama list`

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│          USER INTERACTION               │
│  (Voice Input via Microphone)           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│          EARS (Whisper STT)             │
│  - Wake word detection                  │
│  - Speech-to-text transcription         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│     BRAIN (Hybrid Intelligence)         │
│  ┌─────────────────────────────────┐   │
│  │  Cloud Brain (Groq Llama 3.3)  │   │
│  │  - Conversation                  │   │
│  │  - Sentiment analysis            │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Local Body (Ollama Hermes 3)   │   │
│  │  - Tool execution                │   │
│  │  - System commands               │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Eyes (Llama Scout Vision)      │   │
│  │  - Screen analysis               │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐  ┌─────────────────┐
│    TOOLS     │  │  MEMORY SYSTEM  │
│  8 Actions   │  │  - Short-term   │
│              │  │  - Long-term    │
│              │  │  - Knowledge    │
└──────┬───────┘  └─────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         OUTPUT SYSTEMS                  │
│  ┌────────────────┐  ┌──────────────┐  │
│  │  Voice (TTS)   │  │  GUI Overlay │  │
│  │  Edge TTS      │  │  Arc Reactor │  │
│  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────┘
```

## 🎓 Technical Details

### Sentiment Engine Logic
1. System prompt instructs AI to prefix responses with tags
2. Regex extracts `[HAPPY]`, `[ALERT]`, `[ERROR]`, `[NEUTRAL]`
3. Tags mapped to colors: Green, Orange, Red, Cyan
4. Color signals sent to Qt GUI
5. Smooth interpolation for visual transitions

### Memory Persistence
1. Every response serialized to JSON
2. Message objects converted to dicts
3. Saved to `long_term_memory.json`
4. Loaded on startup and deserialized

### Knowledge Retrieval (RAG Lite)
1. User query → `search_knowledge_base` tool
2. Opens `brain.txt` file
3. Simple keyword matching
4. Returns matching lines
5. Separates private data from cloud AI

## 🏆 Credits

- **LangChain** - AI framework
- **Groq** - Cloud inference
- **Ollama** - Local models
- **Faster-Whisper** - Speech recognition
- **Edge TTS** - Voice synthesis
- **PyQt6** - GUI framework

## 📜 License

MIT License - Feel free to modify and extend!

---

**🚀 SYSTEM STATUS: ALL SYSTEMS ONLINE**

Welcome to the future of personal AI assistants.
