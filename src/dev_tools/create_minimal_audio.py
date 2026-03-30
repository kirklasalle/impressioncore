#!/usr/bin/env python3
"""
Create minimal synthetic audio for ImpressionCore training.
"""
import numpy as np
import soundfile as sf
import os

def create_minimal_audio():
    """Create minimal synthetic audio files for testing."""
    output_dir = "src/data/minimal_datasets/audio"
    os.makedirs(output_dir, exist_ok=True)
    
    sample_rate = 16000  # 16kHz
    duration = 1.0       # 1 second
    
    # Create 5 simple synthetic audio files
    for i in range(1, 6):
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Different waveforms for each audio
        if i == 1:
            # Sine wave at 440Hz (A4)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        elif i == 2:
            # Sine wave at 523Hz (C5)
            audio = 0.3 * np.sin(2 * np.pi * 523 * t)
        elif i == 3:
            # Square wave at 330Hz
            audio = 0.3 * np.sign(np.sin(2 * np.pi * 330 * t))
        elif i == 4:
            # Sawtooth wave at 262Hz
            audio = 0.3 * (2 * (262 * t - np.floor(262 * t + 0.5)))
        else:
            # White noise
            audio = 0.1 * np.random.normal(0, 1, len(t))
        
        # Apply fade in/out to avoid clicks
        fade_samples = int(0.01 * sample_rate)  # 10ms fade
        audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
        audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        # Save audio file
        filename = f"{output_dir}/sample_{i:03d}.wav"
        sf.write(filename, audio, sample_rate)
        print(f"Created {filename}")

if __name__ == "__main__":
    create_minimal_audio()
