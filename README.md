# 🤵🏻‍♂️ PROJECT ALFRED
## Adaptive Logical Framework for Responsive Execution & Decisions

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Engine: Groq](https://img.shields.io/badge/AI-Groq%20Llama%203-orange)](https://groq.com)
[![Local Engine: Ollama](https://img.shields.io/badge/Local-Ollama-white)](https://ollama.com)

> *"At your service, Sir."*

**ALFRED** is a sophisticated, hybrid AI desktop assistant designed to bridge the gap between cloud intelligence and local system control. Unlike standard chatbots, ALFRED acts as a fully autonomous agent that can **hear**, **speak**, **see**, and **act** on your computer.

Featuring a **holographic WayneTech-style overlay**, ALFRED provides a visual connection to the AI's thought process, complete with sentiment-aware color shifting, real-time text generation, and "Ghost Writer" capabilities.

---

## ⚡ Key Features

### 🧠 Hybrid Brain Architecture
ALFRED leverages the best of both worlds:
* **Cloud Brain (Groq + Llama 3.3 70B):** Handles complex reasoning, conversation, and sentiment analysis at lightning speeds.
* **Local Body (Ollama + Hermes 3):** Executes sensitive system tools (app launching, hardware checks) locally for privacy and security.

### 👁️ Visual Cortex (Computer Vision)
Powered by **Llama 4 Scout**, ALFRED can "see" your screen.
* **Vision-to-Code:** "Look at this LeetCode problem and write the solution."
* **Error Analysis:** "Read this error message and tell me how to fix it."
* **Instant Capture:** Uses the `mss` library for <10ms screen capture latency.

### ✍️ Ghost Writer (The "Hands")
ALFRED includes a **Ghost Writer** engine that can take control of your keyboard.
* Autonomously types or pastes code solutions directly into your IDE.
* Perfect for live coding assistance, email drafting, or filling forms.
* *Safety:* Includes smart delays to ensure you have the correct window focused.

### ⚛️ Reactive Holographic HUD
A transparency-enabled PyQt6 overlay that sits on your desktop:
* **Dynamic Speech Bubble:** Auto-resizes and auto-scrolls based on response length (teleprompter style).
* **Sentiment Engine:** The Tactical Radar changes color based on the AI's emotional context:
    * 🟢 **Green:** Success / Happy
    * 🟠 **Orange:** Alert / Warning
    * 🔴 **Red:** Error / Critical
    * 🔵 **Cyan:** Neutral / Processing

### 💾 Long-Term Memory
* Conversations persist across sessions via encrypted storage
* Automatic summarization every 10 messages
* Loads previous context on startup

---

## 🛠️ Installation

### 1. Prerequisites
* **Python 3.10+**
* **[Ollama](https://ollama.com)** installed and running.
* **Groq API Key** (Free tier available at [console.groq.com](https://console.groq.com)).
* **OpenWeatherMap API Key** (Free tier for weather features).

### 2. Setup

```bash
# 1. Clone the repository
git clone https://github.com/NexionisJake/Project-ALFRED.git
cd Project-ALFRED

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Pull the local model for tool execution
ollama pull hermes3
```

### 3. Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_key_here
OPENWEATHER_API_KEY=your_weather_key_here
```

(Optional) Customize `config.py` to change the voice or wake word:

```python
ASSISTANT_NAME = "Alfred"
WAKE_WORD = "alfred"
VOICE_NAME = "en-GB-RyanNeural" # British Butler Voice
```

### 4. Run ALFRED

```bash
python main.py
```

---

## 🎮 Capabilities & Tools

ALFRED comes equipped with **11 integrated tools** out of the box:

| Category | Tool Name | Description |
| --- | --- | --- |
| **System** | `open_application` | Launches apps (Chrome, Spotify, VS Code, etc.) |
|  | `get_system_status` | Reports real-time CPU and RAM usage. |
|  | `system_volume` | Controls volume (Up, Down, Mute). |
| **Web** | `Google Search` | Performs Google searches and opens results. |
|  | `get_weather` | Fetches real-time weather for any city. |
| **Media** | `media_play_pause` | Toggles media playback (Universal). |
|  | `media_next/prev` | Skips or rewinds tracks. |
| **Productivity** | `write_to_screen` | **(Ghost Writer)** Types generated text/code into active window. |
| **Memory** | `search_knowledge_base` | Recalls personal facts from `brain.txt`. |
|  | `get_current_time` | Provides date, time, and day briefing. |

---

## 🗣️ Voice Commands Example

### The "Morning Briefing"

> **You:** *"Alfred, give me the morning briefing."*
> **Alfred:** *"Good morning, Sir. It is currently 8:00 AM. The weather in New York is 72 degrees and clear. All systems are operational."*

### The "Coder" Workflow

> **You:** *(Open LeetCode)*
> **You:** *"Alfred, look at this problem and write the Python solution."*
> **Alfred:** *"Analyzing the Two-Sum problem... I have generated the solution. Pasting now."*
> *(Code automatically appears in your editor)*

### The "DJ" Mode

> **You:** *"Play some music and turn the volume up."*
> **Alfred:** *"Playing Spotify and adjusting audio levels, Sir."*

### Vision Commands

> **You:** *"Look at my screen and describe what you see"*
> **Alfred:** *"I can see your code editor with a Python file..."*

---

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
│  11 Actions  │  │  - Short-term   │
│              │  │  - Long-term    │
│              │  │  - Knowledge    │
└──────┬───────┘  └─────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         OUTPUT SYSTEMS                  │
│  ┌────────────────┐  ┌──────────────┐  │
│  │  Voice (TTS)   │  │  GUI Overlay │  │
│  │  Edge TTS      │  │  Tactical HUD│  │
│  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
Project-ALFRED/
│
├── 📂 core/                  # Core logic modules
│   ├── __init__.py           # Package marker
│   ├── brain.py              # The Brain (AI Processing)
│   ├── ears.py               # The Ears (Whisper + OpenWakeWord)
│   ├── eyes.py               # The Eyes (Vision Analysis)
│   ├── overlay.py            # The Face (PyQt6 Holographic GUI)
│   ├── tools.py              # The Hands (System Automation Tools)
│   ├── voice.py              # Voice synthesis
│   ├── memory.py             # Memory management
│   ├── encryption.py         # Data encryption
│   ├── wake_word.py          # Wake word detection
│   ├── sounds.py             # Sound effects
│   └── app_launcher.py       # Application launcher
│
├── 📂 data/                  # Persistent data and memory
│   ├── brain.txt             # Long-term Knowledge Base
│   ├── brain.txt.enc         # Encrypted knowledge base
│   └── long_term_memory.json # Conversation History (auto-generated)
│
├── 📂 tests/                 # Diagnostic scripts
│   ├── preflight_check.py    # System verification check
│   ├── test_overlay.py       # GUI testing script
│   ├── test_encryption.py    # Encryption tests
│   ├── test_memory.py        # Memory tests
│   ├── test_tools_security.py # Security tests
│   ├── test_utils.py         # Utility tests
│   ├── test_all_tools.py     # All tools tests
│   └── run_all_tests.py      # Master test runner
│
├── 📂 scripts/               # Utility scripts
│   └── migrate_brain.py      # Migration utilities
│
├── 📂 assets/                # Images and temp files
│   ├── temp_speech.mp3       # (Auto-generated)
│   └── temp_command.wav      # (Auto-generated)
│
├── .env                      # API Keys (Hidden in .gitignore)
├── .gitignore                # Git ignore settings
├── config.py                 # Identity & Settings
├── LICENSE                   # MIT License
├── main.py                   # The Central Nervous System (Main Loop)
├── run_tests.py              # Test runner script
├── README.md                 # This file
└── requirements.txt          # Python Dependencies
```

---

## 🐛 Troubleshooting

**Issue**: Microphone not working
- Check `ears.py` isn't running separately
- Verify microphone permissions

**Issue**: GUI not showing
- Ensure PyQt6 is installed
- Run `python tests/test_overlay.py` to test overlay

**Issue**: Tools not working
- Run `python tests/preflight_check.py`
- Verify all imports are successful

**Issue**: API errors
- Check `.env` file has valid GROQ_API_KEY
- Verify Ollama is running: `ollama list`

**Issue**: High resource usage
- Check `config.py` for performance settings
- Consider disabling optional features

---

## 🛡️ Privacy & Security

* **API Security:** Keys are loaded via `.env` and never hardcoded.
* **Local Execution:** Sensitive system commands (like opening apps) are parsed locally by Ollama, not sent to the cloud.
* **Clipboard Safety:** The Ghost Writer tool uses `pyperclip` for safe text insertion.
* **Encrypted Storage:** Sensitive data is encrypted at rest.

---

## 🤝 Contributing

ALFRED is designed to be modular.

1. Fork the repository.
2. Create a new tool in `tools.py`.
3. Register it in `main.py`.
4. Submit a Pull Request.

---

## 🏆 Credits

- **LangChain** - AI framework
- **Groq** - Cloud inference
- **Ollama** - Local models
- **Faster-Whisper** - Speech recognition
- **Edge TTS** - Voice synthesis
- **PyQt6** - GUI framework

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**🚀 SYSTEM STATUS: ALL SYSTEMS ONLINE**

**Built with ❤️ for the future of AI.**

*"We fall so that we can learn to pick ourselves up."*
