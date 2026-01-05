import os
import sys
import asyncio
import time
import re
import json
import edge_tts
import pygame
import keyboard  # For keyboard interrupt support
from colorama import Fore, init
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from collections import deque
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

# IMPORTS FROM YOUR OTHER FILES
from tools import (open_application, get_system_status, google_search, system_volume,
                   media_play_pause, media_next, media_previous, search_knowledge_base)
from ears import listen_and_transcribe, listen_for_wake_word, OPENWAKEWORD_AVAILABLE
from eyes import take_screenshot
from overlay import OverlayWindow, COLOR_HAPPY, COLOR_ALERT, COLOR_ERROR, COLOR_NEUTRAL
import config

init(autoreset=True)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print(Fore.RED + "ERROR: GROQ_API_KEY not found in .env file")
    sys.exit(1)

os.environ["GROQ_API_KEY"] = api_key

# --- CONFIG ---
# Using limited memory to prevent overflow
chat_memory = deque(maxlen=config.MAX_MEMORY_DEPTH)

# Memory optimization tracking
message_count = 0
conversation_summary = None  # Stores condensed conversation context

# Voice from config
VOICE = config.VOICE_NAME

# --- LONG-TERM MEMORY PERSISTENCE ---
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "long_term_memory.json")

def save_memory():
    """Save chat memory to JSON file (serialization)"""
    try:
        memory_data = []
        for msg in chat_memory:
            # Serialize message objects to dict
            msg_dict = {
                "type": msg.__class__.__name__,
                "content": msg.content
            }
            memory_data.append(msg_dict)
        
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        print(Fore.YELLOW + f"Warning: Could not save memory: {e}")

def load_memory():
    """Load chat memory from JSON file (deserialization)"""
    try:
        if not os.path.exists(MEMORY_FILE):
            print(Fore.CYAN + "No previous memory found. Starting fresh.")
            return
        
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
        
        # Deserialize dict back to message objects
        for msg_dict in memory_data:
            if msg_dict["type"] == "HumanMessage":
                chat_memory.append(HumanMessage(content=msg_dict["content"]))
            elif msg_dict["type"] == "AIMessage":
                chat_memory.append(AIMessage(content=msg_dict["content"]))
            elif msg_dict["type"] == "SystemMessage":
                chat_memory.append(SystemMessage(content=msg_dict["content"]))
        
        print(Fore.GREEN + f"✔ Loaded {len(memory_data)} messages from previous session")
    except Exception as e:
        print(Fore.YELLOW + f"Warning: Could not load memory: {e}") 

def clean_text_for_speech(text):
    """Remove markdown and special characters that shouldn't be spoken."""
    # Remove asterisks (bold/italic markdown)
    text = text.replace('*', '')
    
    # Remove hashtags
    text = text.replace('#', '')
    
    # Remove underscores
    text = text.replace('_', '')
    
    # Remove brackets
    text = text.replace('[', '').replace(']', '')
    
    # Remove parentheses content that looks like citations or references
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove code blocks and backticks
    text = text.replace('`', '')
    
    return text.strip()

def speak(text):
    """Converts text to speech using Microsoft Edge TTS."""
    if text.startswith("["):
        return
    
    # Clean text before speaking
    clean_text = clean_text_for_speech(text)
    
    print(Fore.YELLOW + f"🔊 Speaking: '{clean_text[:50]}...'")
    sys.stdout.flush()
    
    try:
        # Generate speech file with cleaned text
        asyncio.run(async_speak(clean_text))
        
        # Unload any previous audio to release file lock
        pygame.mixer.music.unload()
        
        # Play audio synchronously (blocks until complete)
        pygame.mixer.music.load("temp_speech.mp3")
        pygame.mixer.music.play()
        
        print(Fore.GREEN + "✓ Playing audio...")
        sys.stdout.flush()
        
        # Wait until audio finishes playing (with keyboard interrupt support)
        print(Fore.CYAN + "💡 Press ESC to interrupt speech")
        while pygame.mixer.music.get_busy():
            # Check for ESC key to stop speech
            if keyboard.is_pressed('esc'):
                print(Fore.YELLOW + "⏸️ Speech interrupted by user")
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        
        # Unload to release file lock for next time
        pygame.mixer.music.unload()
        
        print(Fore.CYAN + "✓ Speech completed, ready to listen")
        sys.stdout.flush()
        
        # Small buffer to ensure microphone doesn't pick up tail end
        time.sleep(0.5)
        
    except Exception as e:
        print(Fore.RED + f"Speech Error: {e}")
        pygame.mixer.music.unload()  # Cleanup on error too
        sys.stdout.flush()

async def async_speak(text):
    """Async helper for edge-tts."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("temp_speech.mp3")

def summarize_conversation():
    """Summarizes the conversation history to reduce token usage."""
    global conversation_summary, message_count
    
    if len(chat_memory) < 5:  # Not enough to summarize
        return
    
    print(Fore.MAGENTA + "🔄 Optimizing memory (summarizing conversation)...")
    
    try:
        # Build conversation text from memory
        conversation_text = "\n".join([
            f"{msg.__class__.__name__}: {msg.content}" 
            for msg in chat_memory
        ])
        
        # Ask cloud brain to summarize
        summary_prompt = SystemMessage(content="""Summarize this conversation in 2-3 sentences. 
        Focus on key facts, user preferences, and ongoing topics. Be concise.""")
        
        response = cloud_brain.invoke([
            summary_prompt,
            HumanMessage(content=f"Conversation to summarize:\n{conversation_text}")
        ])
        
        conversation_summary = response.content
        print(Fore.GREEN + f"✓ Memory optimized. Summary: {conversation_summary[:60]}...")
        
        # Clear old messages but keep the summary as context
        chat_memory.clear()
        chat_memory.append(SystemMessage(content=f"Previous conversation summary: {conversation_summary}"))
        
        # Reset counter
        message_count = 0
        
    except Exception as e:
        print(Fore.YELLOW + f"⚠ Summarization failed: {e}")

print(Fore.YELLOW + "Initializing Ajax System...")

try:
    cloud_brain = ChatGroq(model=config.CLOUD_MODEL, temperature=0.7)
    local_body = ChatOllama(model=config.LOCAL_MODEL, temperature=0)
    
    # Bind tools to Local Body (now includes 8 tools)
    tools_list = [open_application, get_system_status, google_search, system_volume,
                  media_play_pause, media_next, media_previous, search_knowledge_base]
    local_body_with_tools = local_body.bind_tools(tools_list)
    print(Fore.CYAN + "✔ Systems Online (Cloud + Local + 8 Tools)")
except Exception as e:
    print(Fore.RED + f"✘ Init Error: {e}")
    sys.exit()

# Load previous conversation memory from disk
load_memory()

# --- THE ROUTER WITH VISION ---
def process_command(user_input, ui_callback=None):
    # Print what we received to confirm input works
    print(Fore.WHITE + f"DEBUG: Processing input -> '{user_input}'")
    
    # 1. Vision Check (Does the user want us to LOOK?)
    vision_keywords = config.VISION_KEYWORDS
    wants_vision = any(k in user_input.lower() for k in vision_keywords)

    if wants_vision:
        print(Fore.MAGENTA + "👀 Vision Mode Activated...")
        speak("Taking a look.")
        
        # Capture Image
        image_data = take_screenshot()
        
        # Prepare Message for Groq Vision Model
        msg = HumanMessage(
            content=[
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        )
        
        # Send to Cloud Brain (Vision Model)
        try:
            vision_model = ChatGroq(model=config.VISION_MODEL, temperature=0.5)
            response = vision_model.invoke([msg])
            
            content = response.content
            print(Fore.CYAN + f"[Vision]: {content}")
            
            # Vision gets neutral color (informational)
            if ui_callback:
                ui_callback(content, COLOR_NEUTRAL)
            
            speak(content)
            
            # Save context to memory (as text description)
            chat_memory.append(HumanMessage(content=f"User showed an image. You saw: {content}"))
            return content
            
        except Exception as e:
            print(Fore.RED + f"Vision Error: {e}")
            if ui_callback:
                ui_callback("I had trouble seeing that.", COLOR_ERROR)
            speak("I had trouble seeing that.")
            return "Error"
    
    # 2. Standard Logic - Add to memory for non-vision queries
    global message_count
    chat_memory.append(HumanMessage(content=user_input))
    message_count += 1
    
    # Check if we need to summarize (every 10 messages)
    if message_count >= 10:
        summarize_conversation()
    
    system_keywords = config.SYSTEM_KEYWORDS
    question_starters = config.QUESTION_STARTERS
    
    # Knowledge keywords that should ALWAYS route to tools (even if questions)
    knowledge_keywords = ["what is my", "tell me about my", "my wifi", "my password", 
                         "my name", "my favorite", "my dog", "my pet", "remember"]
    
    has_keyword = any(k in user_input.lower() for k in system_keywords)
    is_question = any(user_input.lower().strip().startswith(s) for s in question_starters)
    needs_knowledge = any(k in user_input.lower() for k in knowledge_keywords)

    print(Fore.WHITE + f"DEBUG: Keyword={has_keyword}, Question={is_question}, Knowledge={needs_knowledge}")

    # Route to LOCAL BODY if: has keyword AND (not a question OR needs knowledge base)
    if has_keyword and (not is_question or needs_knowledge):
        print(Fore.YELLOW + "⚡ Routing to LOCAL SYSTEM...")
        
        system_instruction = SystemMessage(content="""
        You are a PC Automation Agent with access to tools.
        - If the user asks to open/launch/start something, use open_application tool
        - If they ask about system status/CPU/RAM, use get_system_status tool
        - If they want to search Google, use google_search tool
        - If they ask about volume/sound, use system_volume tool
        - If they ask about media (play/pause/skip), use media tools
        - If they ask about personal info (name, password, favorites, etc.), use search_knowledge_base tool
        
        IMPORTANT: For personal questions (what is my..., my favorite...), you MUST call search_knowledge_base.
        Do not make up answers - use the tool to retrieve factual information.
        """)
        
        recent_memory = list(chat_memory)[-5:]
        ai_msg = local_body_with_tools.invoke([system_instruction] + recent_memory)
        
        # Tool Execution Logic
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                print(Fore.GREEN + f"▶ Executing Tool: {tool_name}")
                
                # Execute Tool
                if tool_name == "open_application":
                    tool_result = open_application.invoke(tool_args)
                elif tool_name == "get_system_status":
                    tool_result = get_system_status.invoke(tool_args)
                elif tool_name == "google_search":
                    tool_result = google_search.invoke(tool_args)
                elif tool_name == "system_volume":
                    tool_result = system_volume.invoke(tool_args)
                elif tool_name == "media_play_pause":
                    tool_result = media_play_pause.invoke(tool_args)
                elif tool_name == "media_next":
                    tool_result = media_next.invoke(tool_args)
                elif tool_name == "media_previous":
                    tool_result = media_previous.invoke(tool_args)
                elif tool_name == "search_knowledge_base":
                    tool_result = search_knowledge_base.invoke(tool_args)
                else:
                    tool_result = "Unknown Tool"
                
                print(Fore.GREEN + f"✔ Result: {tool_result}")
                
                # Determine sentiment color based on tool result
                if "Failed" in tool_result or "Error" in tool_result or "Unknown" in tool_result:
                    tool_color = COLOR_ERROR
                elif "not found" in tool_result.lower() or "no information" in tool_result.lower():
                    tool_color = COLOR_ALERT
                else:
                    tool_color = COLOR_HAPPY
                
                # --- UPDATE GUI WITH SENTIMENT COLOR ---
                response_text = f"Done. {tool_result}"
                if ui_callback:
                    ui_callback(response_text, tool_color)
                
                speak(response_text)
                
                chat_memory.append(AIMessage(content=f"[System]: {tool_result}"))
                save_memory()  # Persist to disk after tool execution
                return f"[Action]: {tool_result}"
        
        return f"[Local]: {ai_msg.content}"

    else:
        print(Fore.MAGENTA + "☁️ Routing to CLOUD BRAIN...")
        
        try:
            # Add sentiment instruction to the conversation
            sentiment_instruction = SystemMessage(content="""
You are an emotionally aware AI assistant. Before each response, assess the sentiment:
- If your response is positive/successful, prefix with [HAPPY]
- If your response is a warning/caution, prefix with [ALERT]
- If your response reports an error/problem, prefix with [ERROR]
- Otherwise, use [NEUTRAL]

Example: "[HAPPY] I successfully completed that task for you."
Example: "[ALERT] That action could be risky."
Example: "[ERROR] I encountered a problem accessing that file."
""")
            
            # Prepend sentiment instruction to memory
            messages_with_sentiment = [sentiment_instruction] + list(chat_memory)
            
            # Force a print before sending to Groq
            print(Fore.MAGENTA + "DEBUG: Sending to Groq API...")
            
            response = cloud_brain.invoke(messages_with_sentiment)
            
            # Print the RAW object to see if it's empty
            print(Fore.WHITE + f"DEBUG: Raw Response Object: {response}")
            
            content = response.content
            
            if not content:
                print(Fore.RED + "ERROR: Groq returned EMPTY content!")
                return "Error: Empty response."
            
            # Extract sentiment and determine color
            sentiment_color = COLOR_NEUTRAL  # Default
            sentiment_pattern = r'\[(HAPPY|ALERT|ERROR|NEUTRAL)\]\s*'
            match = re.match(sentiment_pattern, content)
            
            if match:
                sentiment = match.group(1)
                if sentiment == "HAPPY":
                    sentiment_color = COLOR_HAPPY
                elif sentiment == "ALERT":
                    sentiment_color = COLOR_ALERT
                elif sentiment == "ERROR":
                    sentiment_color = COLOR_ERROR
                else:
                    sentiment_color = COLOR_NEUTRAL
                
                # Remove the tag from content before display
                content = re.sub(sentiment_pattern, '', content).strip()
                
            print(Fore.CYAN + f"[Cloud]: {content}")
            
            # --- UPDATE GUI WITH SENTIMENT COLOR ---
            if ui_callback:
                ui_callback(content, sentiment_color)
            
            speak(content) # Then start blocking audio
            
            chat_memory.append(AIMessage(content=content))
            message_count += 1
            save_memory()  # Persist to disk after each response
            return content
            
        except Exception as e:
            print(Fore.RED + f"CRITICAL CLOUD ERROR: {e}")
            return "Error."

# --- WORKER THREAD FOR GUI INTEGRATION ---
class AlfredWorker(QThread):
    """
    Background thread that handles Listening -> Thinking -> Acting.
    Signals the GUI overlay to update status.
    """
    status_update = pyqtSignal(str)  # Signal to update GUI text
    color_update = pyqtSignal(object)  # Signal to update sentiment color
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def stop(self):
        self.running = False
        
    def run(self):
        """Main execution loop in background thread"""
        self.status_update.emit(f"{config.WAKE_WORD.capitalize()} Online")
        time.sleep(1)
        self.status_update.emit("")  # Hide bubble
        
        speak(f"{config.WAKE_WORD.capitalize()} is online. Say my name to activate.")
        print(Fore.WHITE + "\n-----------------------------------")
        print(Fore.WHITE + "   A.L.F.R.E.D. SYSTEM ONLINE")
        print(Fore.WHITE + "   (Adaptive Logical Framework)")
        print(Fore.WHITE + "-----------------------------------\n")
        
        in_conversation = False  # Track if we're in an active conversation
        
        while self.running:
            try:
                # 1. Listen for wake word or command
                if not in_conversation:
                    # Use efficient wake word detection if available
                    if OPENWAKEWORD_AVAILABLE:
                        wake_detected = listen_for_wake_word(config.WAKE_WORD)
                        if not wake_detected:
                            continue
                        user_text = config.WAKE_WORD  # Placeholder
                    else:
                        # Fallback: Use Whisper transcription
                        user_text = listen_and_transcribe()
                        
                        if not user_text:
                            continue
                        
                        if config.WAKE_WORD.lower() not in user_text.lower():
                            print(Fore.LIGHTBLACK_EX + f"Ignored (no wake word): {user_text}")
                            continue
                else:
                    # Already in conversation, just transcribe
                    user_text = listen_and_transcribe()
                
                if not user_text: 
                    if in_conversation:
                        # If silence during conversation, exit conversation mode
                        in_conversation = False
                        self.status_update.emit("💤 Idle")
                        time.sleep(1)
                        self.status_update.emit("")
                        print(Fore.CYAN + "💤 Conversation ended. Say my name to wake me.")
                    continue
                
                # 2. Wake Word Detection (only if not in conversation)
                if not in_conversation:
                    # Wake word detected!
                    print(Fore.WHITE + f"\n🎯 You: {user_text}")
                    self.status_update.emit("🎯 Activated")
                    speak("Yes?")
                    in_conversation = True
                    
                    # Listen for the actual command
                    self.status_update.emit("🎤 Listening...")
                    user_text = listen_and_transcribe()
                    
                    if not user_text: 
                        speak("I didn't catch that.")
                        in_conversation = False
                        self.status_update.emit("")
                        continue
                
                # 3. Process command (works for both wake word and follow-up)
                print(Fore.WHITE + f"Command: {user_text}")
                self.status_update.emit(f"📝 {user_text[:40]}...")

                if "exit" in user_text.lower() or "quit" in user_text.lower():
                    self.status_update.emit("👋 Shutting down...")
                    speak("Shutting down.")
                    time.sleep(2)
                    self.running = False
                    QApplication.quit()  # Close the app
                    break
                
                # Check for conversation end phrases
                end_phrases = ["that's all", "thank you", "thanks", "goodbye", "bye", "stop listening"]
                if any(phrase in user_text.lower() for phrase in end_phrases):
                    speak("You're welcome. Say my name if you need me.")
                    in_conversation = False
                    self.status_update.emit("✓ Ready")
                    time.sleep(1.5)
                    self.status_update.emit("")
                    continue
                
                # 4. Process & Speak
                self.status_update.emit("🧠 Processing...")
                
                # Create a callback to bridge the signal with color support
                # This lets process_command emit text and color directly to the GUI
                def gui_updater(text, color=COLOR_NEUTRAL):
                    self.status_update.emit(text)
                    self.color_update.emit(color)
                
                process_command(user_text, ui_callback=gui_updater)
                
                # Keep conversation active - will continue listening
                print(Fore.CYAN + "🎤 Listening for follow-up...")
                self.status_update.emit("🎤 Listening...")
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
                self.status_update.emit(f"❌ Error: {str(e)[:30]}")
                time.sleep(2)
                self.status_update.emit("")

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    # Create Qt Application
    app = QApplication(sys.argv)
    
    # Create Overlay Window
    overlay = OverlayWindow()
    overlay.show()
    
    # Create and Start Worker Thread
    worker = AlfredWorker()
    worker.status_update.connect(overlay.set_text)  # Connect text signal to GUI
    worker.color_update.connect(overlay.set_sentiment_color)  # Connect color signal to GUI
    worker.start()
    
    # Run Qt Event Loop (keeps GUI alive)
    sys.exit(app.exec())