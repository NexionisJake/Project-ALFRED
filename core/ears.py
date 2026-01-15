import sounddevice as sd
import numpy as np
import wave
import os
import pygame
from faster_whisper import WhisperModel
from colorama import Fore

# Try to import openwakeword for efficient wake word detection
try:
    from openwakeword.model import Model
    OPENWAKEWORD_AVAILABLE = True
    print(Fore.GREEN + "✓ OpenWakeWord available - using efficient wake word detection")
except ImportError:
    OPENWAKEWORD_AVAILABLE = False
    print(Fore.YELLOW + "⚠ OpenWakeWord not installed - using fallback Whisper wake word detection")

# --- CONFIGURATION ---
# Import config for model size
try:
    import config
    MODEL_SIZE = config.WHISPER_SIZE  # Use config value (tiny.en) to save RAM
except ImportError:
    MODEL_SIZE = "tiny.en"  # Fallback to tiny model

CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Dynamic Thresholding Defaults
INITIAL_THRESHOLD = 500
MIN_THRESHOLD = 300
SILENCE_DURATION = 1.5   # Seconds of silence to consider "Done speaking"
NOISE_ADJUST_RATE = 0.05 # How fast we adapt to background noise

print(Fore.YELLOW + "Loading Ears (Whisper Model)...")
# running on CPU with int8 quantization for speed
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

# Initialize Wake Word Detector
detector = None
if OPENWAKEWORD_AVAILABLE:
    try:
        from core.wake_word import WakeWordDetector
        import config
        detector = WakeWordDetector()
        
    except Exception as e:
        print(Fore.YELLOW + f"⚠ Could not initialize wake word detector: {e}")

def listen_for_wake_word(wake_word="jarvis", timeout=None):
    """
    Efficiently listens for the wake word using OpenWakeWord (via WakeWordDetector).
    Falls back to Whisper if OpenWakeWord is not available.
    """
    # Fallback to Whisper if detector is not ready
    if not OPENWAKEWORD_AVAILABLE or detector is None or not detector.enabled:
        text = listen_and_transcribe()
        return wake_word.lower() in text.lower() if text else False
    
    # Efficient wake word detection
    print(Fore.WHITE + f"🎧 Listening for '{wake_word}'...")
    
    try:
        import time 
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16', blocksize=CHUNK) as stream:
            start_time = time.time() if timeout else None
            
            while True:
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    return False
                
                # Check for self-talk (Echo Cancellation)
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    # If Alfred is speaking, we shouldn't trigger wake word on his own voice
                    sd.sleep(100) 
                    continue

                # Read audio chunk
                data, overflowed = stream.read(CHUNK)
                audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Run wake word detection
                if detector.detect(audio_array, threshold=config.WAKE_WORD_THRESHOLD):
                    print(Fore.GREEN + f"✓ Wake word detected!")
                    return True
                        
    except Exception as e:
        print(Fore.RED + f"Wake word detection error: {e}")
        return False

def listen_and_transcribe():
    """
    Records audio with DYNAMIC NOISE THRESHOLDING.
    Adaptively ignores background noise and waits for speech.
    """
    print(Fore.WHITE + "🎤 Listening... (Speak now)")
    
    audio_data = []
    silent_chunks = 0
    has_spoken = False
    
    # Adaptive Threshold variables
    current_threshold = INITIAL_THRESHOLD
    noise_level = INITIAL_THRESHOLD / 2  # Estimate noise floor
    
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16') as stream:
        while True:
            # 1. Check for Self-Talking (Software Echo Cancellation)
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                # Alfred is speaking. Pause listening effectively.
                # We consume the text to empty buffer but don't process it as speech
                stream.read(CHUNK) 
                continue

            # 2. Read Audio
            data, overflowed = stream.read(CHUNK)
            np_data = np.frombuffer(data, dtype=np.int16)
            
            # 3. Calculate Volume (RMS-like)
            volume = np.abs(np_data).mean()
            
            # 4. Dynamic Threshold Logic
            if not has_spoken:
                # While waiting for speech, adapt to noise
                if volume < current_threshold:
                    # Slowly lowercase threshold or raise it to match noise
                    noise_level = (noise_level * (1 - NOISE_ADJUST_RATE)) + (volume * NOISE_ADJUST_RATE)
                    current_threshold = max(MIN_THRESHOLD, noise_level * 2.5) # Threshold is 2.5x noise floor
            
            # 5. Speech Detection
            if volume > current_threshold:
                if not has_spoken:
                    print(Fore.GREEN + "⚡ Speech detected...")
                has_spoken = True
                silent_chunks = 0
                audio_data.append(data)
            elif has_spoken:
                # We are in a "pause" after speech
                silent_chunks += 1
                audio_data.append(data) # Keep recording trails
            
            # 6. Silence Timeout
            chunks_per_second = RATE / CHUNK
            if has_spoken and silent_chunks > (SILENCE_DURATION * chunks_per_second):
                break
                
            # timeout if nothing heard for too long? (Optional)
    
    if not audio_data:
        return ""

    print(Fore.YELLOW + "Processing audio...")
    
    # Save to temporary WAV file
    filename = "temp_command.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2) # 2 bytes (16 bit)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_data))
    
    # Transcribe
    try:
        segments, info = model.transcribe(filename, beam_size=1)
        full_text = "".join([segment.text for segment in segments]).strip()
    except Exception as e:
        print(Fore.RED + f"Transcription Error: {e}")
        full_text = ""
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)
        
    return full_text

# Quick test if you run this file directly
if __name__ == "__main__":
    pygame.mixer.init() # Needed for busy check mock
    if OPENWAKEWORD_AVAILABLE:
        print("Testing wake word detection...")
        if listen_for_wake_word("jarvis", timeout=10):
            print("Wake word detected! Now transcribing...")
            print(f"Heard: {listen_and_transcribe()}")
        else:
            print("No wake word detected in 10 seconds")
    else:
        print(f"Heard: {listen_and_transcribe()}")