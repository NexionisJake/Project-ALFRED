import asyncio
import os
import sys
import time
import re
import pygame
import edge_tts
import keyboard
from colorama import Fore

import config

class AlfredVoice:
    """
    Handles Text-to-Speech (TTS) using Microsoft Edge TTS and Pygame.
    """
    def __init__(self):
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            self.voice_name = config.VOICE_NAME
            self.temp_file = "temp_speech.mp3"
        except Exception as e:
            print(Fore.RED + f"Voice Init Error: {e}")

    def clean_text_for_speech(self, text):
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

    async def _async_speak(self, text):
        """Async helper for edge-tts."""
        communicate = edge_tts.Communicate(text, self.voice_name)
        await communicate.save(self.temp_file)

    def speak(self, text):
        """Converts text to speech using Microsoft Edge TTS."""
        if not text or text.startswith("["):
            return
        
        # Clean text before speaking
        clean_text = self.clean_text_for_speech(text)
        
        print(Fore.YELLOW + f"🔊 Speaking: '{clean_text[:50]}...'")
        sys.stdout.flush()
        
        try:
            # Generate speech file with cleaned text
            asyncio.run(self._async_speak(clean_text))
            
            # Unload any previous audio to release file lock
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            # Play audio synchronously (blocks until complete)
            pygame.mixer.music.load(self.temp_file)
            pygame.mixer.music.play()
            
            print(Fore.GREEN + "✓ Playing audio...")
            sys.stdout.flush()
            
            # Wait until audio finishes playing (with keyboard interrupt support)
            print(Fore.CYAN + "💡 Press ESC or ENTER to interrupt speech")
            while pygame.mixer.music.get_busy():
                # Check for ESC or ENTER key to stop speech
                if keyboard.is_pressed('esc') or keyboard.is_pressed('enter'):
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

    def stop(self):
        """Stops any current playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()
