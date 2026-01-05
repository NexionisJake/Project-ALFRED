import sounddevice as sd
import numpy as np
import wave
import os
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
# "tiny.en" is the fastest model. Use "base.en" if you want better accuracy.
MODEL_SIZE = "tiny.en" 
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 500  # Adjust this if it cuts off too early/late
SILENCE_DURATION = 1.5   # Seconds of silence to consider "Done speaking"

print(Fore.YELLOW + "Loading Ears (Whisper Model)...")
# running on CPU with int8 quantization for speed
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

# Initialize OpenWakeWord if available
owwModel = None
if OPENWAKEWORD_AVAILABLE:
    try:
        print(Fore.YELLOW + "Loading Wake Word Model...")
        # Load pre-trained models (hey_jarvis is a generic wake word similar to "Jarvis")
        # You can also use "hey_mycroft" or "alexa" - they work for similar sounds
        owwModel = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        print(Fore.GREEN + "✓ Wake Word Model loaded")
    except Exception as e:
        print(Fore.YELLOW + f"⚠ Could not load wake word model: {e}")
        OPENWAKEWORD_AVAILABLE = False

def listen_for_wake_word(wake_word="jarvis", timeout=None):
    """
    Efficiently listens for the wake word using OpenWakeWord (if available).
    Falls back to Whisper if OpenWakeWord is not installed.
    
    Returns: True if wake word detected, False otherwise
    """
    if not OPENWAKEWORD_AVAILABLE or owwModel is None:
        # Fallback: Use Whisper to detect wake word (original method)
        text = listen_and_transcribe()
        return wake_word.lower() in text.lower() if text else False
    
    # Efficient wake word detection using OpenWakeWord
    print(Fore.WHITE + f"🎧 Listening for '{wake_word}'...")
    
    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16', blocksize=CHUNK) as stream:
            start_time = None if timeout is None else sd.get_stream_time(stream)
            
            while True:
                # Check timeout
                if timeout and (sd.get_stream_time(stream) - start_time) > timeout:
                    return False
                
                # Read audio chunk
                data, overflowed = stream.read(CHUNK)
                audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Run wake word detection
                prediction = owwModel.predict(audio_array)
                
                # Check if any wake word was detected (threshold: 0.5)
                for mdl_name, score in prediction.items():
                    if score > 0.5:
                        print(Fore.GREEN + f"✓ Wake word detected! (confidence: {score:.2f})")
                        return True
                        
    except Exception as e:
        print(Fore.RED + f"Wake word detection error: {e}")
        return False

def listen_and_transcribe():
    """
    Records audio until silence is detected, then transcribes it.
    """
    print(Fore.WHITE + "🎤 Listening... (Speak now)")
    
    audio_data = []
    silent_chunks = 0
    has_spoken = False
    
    # 1. Start Recording Stream
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16') as stream:
        while True:
            # Read a chunk of audio
            data, overflowed = stream.read(CHUNK)
            np_data = np.frombuffer(data, dtype=np.int16)
            audio_data.append(data)
            
            # Check volume level
            volume = np.abs(np_data).mean()
            
            if volume > SILENCE_THRESHOLD:
                has_spoken = True
                silent_chunks = 0
            elif has_spoken:
                silent_chunks += 1
            
            # If we have been silent for X seconds, stop recording
            # (RATE / CHUNK) is roughly how many chunks per second
            chunks_per_second = RATE / CHUNK
            if has_spoken and silent_chunks > (SILENCE_DURATION * chunks_per_second):
                break
    
    print(Fore.YELLOW + "Processing audio...")
    
    # 2. Save to temporary WAV file
    filename = "temp_command.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2) # 2 bytes (16 bit)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_data))
    
    # 3. Transcribe
    segments, info = model.transcribe(filename, beam_size=1)
    full_text = "".join([segment.text for segment in segments]).strip()
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)
        
    return full_text

# Quick test if you run this file directly
if __name__ == "__main__":
    if OPENWAKEWORD_AVAILABLE:
        print("Testing wake word detection...")
        if listen_for_wake_word("jarvis", timeout=10):
            print("Wake word detected! Now transcribing...")
            print(f"Heard: {listen_and_transcribe()}")
        else:
            print("No wake word detected in 10 seconds")
    else:
        print(f"Heard: {listen_and_transcribe()}")