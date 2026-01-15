import os
import re
import sys
import json
from collections import deque
from colorama import Fore
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import config
from core.tools import (open_application, get_system_status, google_search, system_volume,
                   media_play_pause, media_next, media_previous, search_knowledge_base,
                   get_current_time, get_weather, write_to_screen)
from core.overlay import COLOR_SYSTEM_OK, COLOR_WARNING, COLOR_CRITICAL, COLOR_SUCCESS
from core.memory import VectorMemory

class AlfredBrain:
    """
    The Brain of ALFRED.
    Handles:
    - LLM Initialization (Cloud + Local)
    - Memory Management (Short-term + RAG)
    - Routing (Vision vs. System vs. Chat)
    - Tool Execution
    - Sentiment Analysis
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print(Fore.RED + "ERROR: GROQ_API_KEY not found in .env file")
        
        self.chat_memory = deque(maxlen=config.MAX_MEMORY_DEPTH)
        self.message_count = 0
        self.memory_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "long_term_memory.json")
        
        # Initialize Vector Memory (RAG) - Optional for performance
        print(Fore.YELLOW + "Initializing Memory Systems...")
        if getattr(config, 'ENABLE_VECTOR_MEMORY', True):
            self.vector_memory = VectorMemory()
        else:
            print(Fore.CYAN + "⚡ Vector Memory disabled (saving RAM)")
            self.vector_memory = None
        
        # Initialize Models
        print(Fore.YELLOW + "Initializing Ajax System (Brain)...")
        try:
            self.cloud_brain = ChatGroq(model=config.CLOUD_MODEL, temperature=0.7)
            
            # Local model is optional for performance
            if getattr(config, 'ENABLE_LOCAL_MODEL', True):
                self.local_body = ChatOllama(model=config.LOCAL_MODEL, temperature=0)
                
                # Bind tools to Local Body
                self.tools_list = [open_application, get_system_status, google_search, system_volume,
                              media_play_pause, media_next, media_previous, search_knowledge_base,
                              get_current_time, get_weather, write_to_screen]
                self.local_body_with_tools = self.local_body.bind_tools(self.tools_list)
                print(Fore.CYAN + "✔ Systems Online (Cloud + Local + 11 Tools)")
            else:
                self.local_body = None
                self.local_body_with_tools = None
                print(Fore.CYAN + "✔ Systems Online (Cloud Only - Local disabled for performance)")
        except Exception as e:
            print(Fore.RED + f"✘ Init Error: {e}")
            
        # Load Memory
        self.load_memory()

    def load_memory(self):
        """Load chat memory from JSON file."""
        try:
            if not os.path.exists(self.memory_file):
                print(Fore.CYAN + "No previous memory found. Starting fresh.")
                return
            
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            self.chat_memory.clear()
            for msg_dict in memory_data:
                if msg_dict["type"] == "HumanMessage":
                    self.chat_memory.append(HumanMessage(content=msg_dict["content"]))
                elif msg_dict["type"] == "AIMessage":
                    self.chat_memory.append(AIMessage(content=msg_dict["content"]))
                elif msg_dict["type"] == "SystemMessage":
                    self.chat_memory.append(SystemMessage(content=msg_dict["content"]))
            
            print(Fore.GREEN + f"✔ Loaded {len(memory_data)} messages from previous session")
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Could not load memory: {e}") 

    def save_memory(self):
        """Save chat memory to JSON file."""
        try:
            memory_data = []
            for msg in self.chat_memory:
                msg_dict = {
                    "type": msg.__class__.__name__,
                    "content": msg.content
                }
                memory_data.append(msg_dict)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Could not save memory: {e}")

    def summarize_conversation(self):
        """Summarizes conversation to save tokens."""
        if len(self.chat_memory) < 5:
            return
        
        print(Fore.MAGENTA + "🔄 Optimizing memory (summarizing conversation)...")
        try:
            conversation_text = "\n".join([f"{msg.__class__.__name__}: {msg.content}" for msg in self.chat_memory])
            summary_prompt = SystemMessage(content="Summarize this conversation in 2-3 sentences. Focus on key facts and user preferences.")
            
            response = self.cloud_brain.invoke([summary_prompt, HumanMessage(content=f"Conversation:\n{conversation_text}")])
            summary = response.content
            
            print(Fore.GREEN + f"✓ Memory optimized. Summary: {summary[:60]}...")
            self.chat_memory.clear()
            self.chat_memory.append(SystemMessage(content=f"Previous conversation summary: {summary}"))
            self.message_count = 0
            
            # Store summary in Vector DB as well
            if self.vector_memory and self.vector_memory.enabled:
                self.vector_memory.add_conversation("system", f"Conversation Summary: {summary}")
                
        except Exception as e:
            print(Fore.YELLOW + f"⚠ Summarization failed: {e}")

    def process_vision(self, user_input, image_data, ui_callback=None):
        """Handles vision-related requests."""
        print(Fore.MAGENTA + "👀 Vision Mode Activated...")
        
        msg = HumanMessage(
            content=[
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        )
        
        try:
            vision_model = ChatGroq(model=config.VISION_MODEL, temperature=0.5)
            response = vision_model.invoke([msg])
            content = response.content
            print(Fore.CYAN + f"[Vision]: {content}")
            
            if ui_callback:
                ui_callback(content, COLOR_SYSTEM_OK)
                
            self.chat_memory.append(HumanMessage(content=f"User showed an image. You saw: {content}"))
            
            # Check for code extraction
            write_keywords = ["write", "type", "paste", "input", "code it", "implement"]
            if any(k in user_input.lower() for k in write_keywords):
                code_match = re.search(r'```(?:python|cpp|java|javascript)?\n(.*?)```', content, re.DOTALL)
                if code_match:
                    code = code_match.group(1).strip()
                    write_to_screen.invoke({"text": code})
                    return f"{content}\n(Code pasted successfully)"
            
            return content
        except Exception as e:
            print(Fore.RED + f"Vision Error: {e}")
            return "I had trouble seeing that."

    def think(self, user_input, ui_callback=None):
        """
        Main decision loop.
        Arguments:
            user_input (str): The text query from the user.
            ui_callback (func): Function to update the GUI (text, color).
        Returns:
            str: The response text (or tool output).
        """
        print(Fore.WHITE + f"DEBUG: Processing input -> '{user_input}'")
        
        # Add to memory
        self.chat_memory.append(HumanMessage(content=user_input))
        self.message_count += 1
        if self.message_count >= 10:
            self.summarize_conversation()
            
        # Routing Logic
        system_keywords = config.SYSTEM_KEYWORDS
        question_starters = config.QUESTION_STARTERS
        
        # Knowledge keywords check is less strict now that we have RAG, 
        # but we keep it to force tool usage if explicitly asked.
        knowledge_keywords = ["what is my", "tell me about my", "my wifi", "my password", 
                             "my name", "my favorite", "my dog", "my pet"]
        
        has_keyword = any(k in user_input.lower() for k in system_keywords)
        needs_knowledge = any(k in user_input.lower() for k in knowledge_keywords)

        # LOCAL ROUTE (Tools)
        if has_keyword or needs_knowledge:
            return self._run_local_tools(user_input, ui_callback)
        
        # CLOUD ROUTE (Chat)
        else:
            return self._run_cloud_chat(user_input, ui_callback)

    def _run_local_tools(self, user_input, ui_callback):
        print(Fore.YELLOW + "⚡ Routing to LOCAL SYSTEM...")
        
        # If local model is disabled, fall back to cloud for tool-like requests
        if self.local_body_with_tools is None:
            print(Fore.CYAN + "⚡ Local model disabled, using cloud fallback for tools")
            return self._run_cloud_chat(user_input, ui_callback)
        
        system_instruction = SystemMessage(content="""
        You are a PC Automation Agent. USE TOOLS directly.
        - Open apps -> open_application
        - Status -> get_system_status
        - Search -> google_search
        - Volume -> system_volume
        - Media -> media_play_pause / next / prev
        - Weather -> get_weather
        - Time -> get_current_time
        - Knowledge -> search_knowledge_base
        - Type/Code -> write_to_screen
        
        Do not reply with just text if a tool fits.
        """)
        
        recent_memory = list(self.chat_memory)[-5:]
        try:
            ai_msg = self.local_body_with_tools.invoke([system_instruction] + recent_memory)
            
            # Execute Tools
            if ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    print(Fore.GREEN + f"▶ Executing Tool: {tool_name}")
                    
                    # Tool Dispatcher
                    tool_result = self._dispatch_tool(tool_name, tool_args)
                    
                    print(Fore.GREEN + f"✔ Result: {tool_result}")
                    
                    # UI Color
                    color = COLOR_SUCCESS
                    if "Error" in str(tool_result) or "Failed" in str(tool_result):
                        color = COLOR_CRITICAL
                    elif "not found" in str(tool_result).lower():
                        color = COLOR_WARNING
                        
                    if ui_callback:
                        ui_callback(f"Done. {tool_result}", color)
                        
                    self.chat_memory.append(AIMessage(content=f"[System]: {tool_result}"))
                    self.save_memory()
                    return f"Done. {tool_result}"
            
            # No tool called
            response = ai_msg.content or "I'm not sure how to help with that."
            if ui_callback:
                ui_callback(response, COLOR_SYSTEM_OK)
            return response
            
        except Exception as e:
            error_msg = f"System Error: {e}"
            print(Fore.RED + error_msg)
            return error_msg

    def _dispatch_tool(self, name, args):
        """Map tool name to function."""
        tool_map = {
            "open_application": open_application,
            "get_system_status": get_system_status,
            "google_search": google_search,
            "system_volume": system_volume,
            "media_play_pause": media_play_pause,
            "media_next": media_next,
            "media_previous": media_previous,
            "search_knowledge_base": search_knowledge_base,
            "get_current_time": get_current_time,
            "get_weather": get_weather,
            "write_to_screen": write_to_screen
        }
        if name in tool_map:
            return tool_map[name].invoke(args)
        return "Unknown Tool"

    def _extract_and_save_facts(self, user_input):
        """
        Simple heuristic to save personal facts to VectorMemory.
        Uses regex for speed, avoiding an extra LLM call for now.
        """
        if not self.vector_memory or not self.vector_memory.enabled:
            return

        # Simple patterns to catch "My X is Y" or "I live in Z"
        # This is a basic implementation; a true "Fact Extraction" agent would be better but slower.
        facts_patterns = [
            r"(my name is \w+)",
            r"(i live in \w+)",
            r"(my wifi password is .*?)",
            r"(my favorite \w+ is \w+)"
        ]
        
        for pattern in facts_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                fact = match.group(1)
                print(Fore.MAGENTA + f"⚡ Auto-Memorizing Fact: '{fact}'")
                self.vector_memory.add_knowledge(fact, category="auto_extracted")

    def _run_cloud_chat(self, user_input, ui_callback):
        print(Fore.MAGENTA + "☁️ Routing to CLOUD BRAIN...")
        
        # 1. RAG: Retrieve Context
        context_str = ""
        if self.vector_memory and self.vector_memory.enabled:
            context_str = self.vector_memory.get_relevant_context(user_input)
            if context_str:
                print(Fore.MAGENTA + f"🧩 Context Injected: {len(context_str)} chars")
        
        # 2. Auto-Memorization Check
        self._extract_and_save_facts(user_input)
        
        try:
            persona_content = """
            You are Alfred, a loyal, highly competent, and dry-witted digital butler.
            Address the user as "Sir". Be concise, formal, and helpful.
            Start responses with a sentiment tag: [HAPPY], [ALERT], [ERROR], or [NEUTRAL].
            """
            
            if context_str:
                persona_content += f"\n\nRELEVANT MEMORY:\n{context_str}\nUse this information if relevant."
            
            persona = SystemMessage(content=persona_content)
            
            messages = [persona] + list(self.chat_memory)
            response = self.cloud_brain.invoke(messages)
            content = response.content
            
            # Sentiment Color Parsing
            sentiment_color = COLOR_SYSTEM_OK
            if "[HAPPY]" in content: sentiment_color = COLOR_SUCCESS
            elif "[ALERT]" in content: sentiment_color = COLOR_WARNING
            elif "[ERROR]" in content: sentiment_color = COLOR_CRITICAL
            
            # Clean content
            clean_content = re.sub(r'\[.*?\]', '', content).strip()
            
            if ui_callback:
                ui_callback(clean_content, sentiment_color)
                
            self.chat_memory.append(AIMessage(content=content))
            self.save_memory()
            
            # Save conversation loop to vector memory for future recall
            if self.vector_memory and self.vector_memory.enabled:
                self.vector_memory.add_conversation("user", user_input)
                self.vector_memory.add_conversation("alfred", clean_content)
                
            return clean_content
            
        except Exception as e:
            print(Fore.RED + f"Cloud Error: {e}")
            return "I'm having trouble connecting to the cloud, Sir."
