"""
Custom wake word training utilities for ALFRED.
Uses OpenWakeWord for efficient, on-device wake word recognition.
"""

import os
import json
from pathlib import Path
from typing import Optional, List
from colorama import Fore

try:
    import numpy as np
    import sounddevice as sd
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from openwakeword.model import Model
    from openwakeword import utils
    OPENWAKEWORD_AVAILABLE = True
except ImportError:
    OPENWAKEWORD_AVAILABLE = False


class WakeWordTrainer:
    """
    Utility for training custom wake words using OpenWakeWord.
    
    Note: Full custom training requires additional setup with the
    openwakeword training scripts. This class provides recording
    and basic configuration utilities.
    """
    
    SAMPLE_RATE = 16000
    DURATION = 2.0  # seconds per recording
    
    def __init__(self, data_dir: str = None):
        """
        Initialize wake word trainer.
        
        Args:
            data_dir: Directory to store training data and models
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "data", 
                "wake_words"
            )
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = self.data_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load or create wake word configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "active_wake_word": "alfred",
            "custom_models": [],
            "recordings": {}
        }
    
    def _save_config(self):
        """Save configuration to disk."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def record_sample(self, wake_word: str, sample_num: int) -> str:
        """
        Record a single wake word sample.
        
        Args:
            wake_word: Name of the wake word
            sample_num: Sample number (for creating multiple samples)
        
        Returns:
            Path to saved audio file
        """
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Audio recording not available. Install numpy and sounddevice.")
        
        word_dir = self.data_dir / wake_word
        word_dir.mkdir(exist_ok=True)
        
        output_path = word_dir / f"sample_{sample_num:03d}.wav"
        
        print(Fore.CYAN + f"\n🎤 Recording sample {sample_num} for '{wake_word}'")
        print(Fore.YELLOW + f"   Say '{wake_word}' clearly after the beep...")
        print(Fore.WHITE + "   (Recording for 2 seconds)")
        
        # Small delay before recording
        import time
        time.sleep(0.5)
        print(Fore.GREEN + "   🔴 RECORDING...")
        
        # Record audio
        audio_data = sd.rec(
            int(self.DURATION * self.SAMPLE_RATE),
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype='int16'
        )
        sd.wait()  # Wait for recording to complete
        
        print(Fore.GREEN + "   ✓ Recording complete!")
        
        # Save to WAV file
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        
        # Update config
        if wake_word not in self.config['recordings']:
            self.config['recordings'][wake_word] = []
        self.config['recordings'][wake_word].append(str(output_path))
        self._save_config()
        
        return str(output_path)
    
    def collect_training_samples(self, wake_word: str, num_samples: int = 10) -> List[str]:
        """
        Collect multiple training samples for a wake word.
        
        Args:
            wake_word: The wake word to train
            num_samples: Number of samples to collect (minimum 5-10 recommended)
        
        Returns:
            List of paths to recorded samples
        """
        print(Fore.CYAN + "=" * 50)
        print(Fore.CYAN + f"  Wake Word Training: '{wake_word}'")
        print(Fore.CYAN + "=" * 50)
        print()
        print(Fore.WHITE + f"We'll record {num_samples} samples of you saying '{wake_word}'.")
        print(Fore.WHITE + "Try to vary your tone, speed, and distance from the mic.")
        print(Fore.YELLOW + "\nPress Enter to start recording each sample...")
        
        samples = []
        for i in range(1, num_samples + 1):
            input(Fore.WHITE + f"\n[{i}/{num_samples}] Press Enter when ready...")
            path = self.record_sample(wake_word, i)
            samples.append(path)
        
        print(Fore.GREEN + f"\n✓ Collected {len(samples)} samples for '{wake_word}'")
        print(Fore.CYAN + f"  Samples saved to: {self.data_dir / wake_word}")
        
        return samples
    
    def set_active_wake_word(self, wake_word: str):
        """
        Set the active wake word to use.
        
        Args:
            wake_word: Name of wake word (must have trained model or be built-in)
        """
        self.config['active_wake_word'] = wake_word
        self._save_config()
        print(Fore.GREEN + f"✓ Active wake word set to: '{wake_word}'")
    
    def get_active_wake_word(self) -> str:
        """Get the currently active wake word."""
        return self.config.get('active_wake_word', 'alfred')
    
    def list_available_models(self) -> List[str]:
        """
        List available wake word models (built-in + custom).
        
        Returns:
            List of model names
        """
        models = []
        
        # Built-in OpenWakeWord models
        builtin = ['hey_jarvis', 'hey_mycroft', 'alexa', 'ok_google', 'hey_siri']
        models.extend(builtin)
        
        # Custom models
        models.extend(self.config.get('custom_models', []))
        
        return models
    
    def get_training_instructions(self) -> str:
        """
        Get instructions for full custom wake word training.
        
        Returns:
            Markdown-formatted instructions
        """
        return """
# Custom Wake Word Training

To train a fully custom wake word for ALFRED, follow these steps:

## 1. Collect Training Data
Use this trainer to record samples:
```python
from core.wake_word import WakeWordTrainer
trainer = WakeWordTrainer()
trainer.collect_training_samples("my_custom_word", num_samples=20)
```

## 2. Install Training Dependencies
```bash
pip install openwakeword[training]
```

## 3. Train the Model
Follow OpenWakeWord's training guide:
https://github.com/dscripka/openwakeword#training-new-models

## 4. Add Custom Model
Place the trained `.onnx` model in `data/wake_words/models/`
and update config.json.

## Alternative: Use Similar Built-in Words
OpenWakeWord's built-in models may work for similar-sounding
wake words:
- 'hey_jarvis' - Works for "Hey Alfred", "Jarvis"
- 'hey_mycroft' - Works for similar sounds
- 'alexa' - Works for 2-syllable names
"""


class WakeWordDetector:
    """
    Production wake word detector that supports custom configuration.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize detector with configuration.
        
        Args:
            config_path: Path to wake word config (uses default if not specified)
        """
        self.enabled = OPENWAKEWORD_AVAILABLE
        
        if not self.enabled:
            print(Fore.YELLOW + "⚠ OpenWakeWord not available - using fallback detection")
            return
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "wake_words", "config.json"
            )
        
        self.config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Get active wake word
        self.wake_word = self.config.get('active_wake_word', 'alfred')
        
        # Map wake words to OpenWakeWord models
        # Note: "hey_jarvis" is a decent fallback for "alfred" (similar cadence/vowels), 
        # but a custom model is strictly better.
        self.model_map = {
            'alfred': 'hey_jarvis', 
            'jarvis': 'hey_jarvis',
            'hey alfred': 'hey_jarvis',
            'hey jarvis': 'hey_jarvis',
            'alexa': 'alexa',
            'mycroft': 'hey_mycroft',
        }
        
        # Load model
        model_name = self.model_map.get(self.wake_word.lower(), 'hey_jarvis')
        
        # Check if we are using a fallback for Alfred
        if self.wake_word.lower() == 'alfred' and model_name == 'hey_jarvis':
            print(Fore.YELLOW + "⚠ Note: Using 'hey_jarvis' model as fallback for 'Alfred'.")
            print(Fore.YELLOW + "  For best results, run core/wake_word.py to train a custom 'alfred' model.")
        
        try:
            self.model = Model(wakeword_models=[model_name], inference_framework="onnx")
            print(Fore.GREEN + f"✓ Wake word detector ready (using '{model_name}' model)")
        except Exception as e:
            print(Fore.RED + f"✗ Failed to load wake word model: {e}")
            self.enabled = False
    
    def detect(self, audio_chunk: np.ndarray, threshold: float = 0.5) -> bool:
        """
        Check if audio chunk contains wake word.
        
        Args:
            audio_chunk: Audio data (float32, normalized to -1..1)
            threshold: Detection threshold (0-1)
        
        Returns:
            True if wake word detected
        """
        if not self.enabled:
            return False
        
        try:
            prediction = self.model.predict(audio_chunk)
            
            for model_name, score in prediction.items():
                if score > threshold:
                    return True
            
            return False
        except Exception:
            return False


# Quick test
if __name__ == "__main__":
    print(Fore.CYAN + "Wake Word Training Utility")
    print(Fore.CYAN + "=" * 40)
    
    if not AUDIO_AVAILABLE:
        print(Fore.RED + "⚠ Audio not available. Install: pip install numpy sounddevice")
    else:
        trainer = WakeWordTrainer()
        
        print("\nOptions:")
        print("  1. Record training samples")
        print("  2. View available models")
        print("  3. View training instructions")
        print("  4. Set active wake word")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            word = input("Enter wake word to train: ").strip() or "alfred"
            count = int(input("Number of samples (default 10): ").strip() or "10")
            trainer.collect_training_samples(word, count)
        elif choice == "2":
            print("\nAvailable models:", trainer.list_available_models())
        elif choice == "3":
            print(trainer.get_training_instructions())
        elif choice == "4":
            word = input("Enter wake word to activate: ").strip()
            trainer.set_active_wake_word(word)
