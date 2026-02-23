import math
import struct
import base64
import io
import wave

def generate_tone(frequency=440, duration=1, volume=0.5, sample_rate=44100, wave_type='sine', decay=True):
    """
    Generate a single tone with optional decay.
    """
    n_samples = int(sample_rate * duration)
    data = []
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        
        # Amplitude envelope
        if decay:
            # Exponential decay
            envelope = math.exp(-3 * t / duration)
        else:
            envelope = 1.0
            
        # Waveform
        if wave_type == 'sine':
            value = math.sin(2.0 * math.pi * frequency * t)
        elif wave_type == 'square':
            value = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
        elif wave_type == 'sawtooth':
            value = 2.0 * (t * frequency - math.floor(0.5 + t * frequency))
        else:
            value = math.sin(2.0 * math.pi * frequency * t)
            
        # Apply volume and envelope
        sample = volume * envelope * value
        
        # Clamp to -1 to 1
        sample = max(min(sample, 1.0), -1.0)
        
        # Convert to 16-bit PCM
        data.append(int(sample * 32767.0))
        
    return data

def generate_chord(frequencies, duration=0.5, volume=0.5, sample_rate=44100):
    """
    Generate a chord locally (superposition of waves).
    """
    n_samples = int(sample_rate * duration)
    mixed_data = [0.0] * n_samples
    
    # Generate each note
    for freq in frequencies:
        # Slight detune or stagger could be added here
        tone_data = generate_tone(freq, duration, volume/len(frequencies), sample_rate)
        for i in range(n_samples):
            mixed_data[i] += tone_data[i]
            
    # Clamp and convert
    final_data = []
    for s in mixed_data:
        # data in tone_data is already scaled to 32767, so we sum them
        # We need to be careful about overflow if we just summed integers
        # Actually generate_tone returns int. Let's refactor to return floats for mixing?
        # For simplicity, let's just regenerate floats here.
        pass
    
    # Re-implementing mix separately for simplicity
    final_data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        sample = 0.0
        envelope = math.exp(-4 * t / duration) # Faster decay for chord
        
        for freq in frequencies:
            sample += math.sin(2.0 * math.pi * freq * t)
        
        # Average and apply volume
        sample = (sample / len(frequencies)) * volume * envelope
        final_data.append(int(max(min(sample, 1.0), -1.0) * 32767.0))
        
    return final_data

def create_wav_base64(audio_data, sample_rate=44100):
    """
    Create a WAV file in memory and return base64 string.
    """
    # Create an in-memory binary stream
    wav_buffer = io.BytesIO()
    
    # Open a wave file object with the buffer
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        # Pack data
        packed_data = struct.pack('<' + ('h' * len(audio_data)), *audio_data)
        wav_file.writeframes(packed_data)
        
    # Get the bytes from the buffer
    wav_bytes = wav_buffer.getvalue()
    
    # Encode to base64
    return base64.b64encode(wav_bytes).decode('utf-8')

def get_sound_by_name(name):
    """
    Factory to return base64 string for a named sound.
    """
    name = name.lower()
    
    if "chime" in name:
        # A nice high ping
        data = generate_tone(frequency=880, duration=0.8, volume=0.6)
    elif "pop" in name:
        # A short low blip
        data = generate_tone(frequency=500, duration=0.15, volume=0.5, decay=True)
    elif "success" in name:
        # C Major Chord (C5, E5, G5) -> 523.25, 659.25, 783.99
        data = generate_chord([523.25, 659.25, 783.99], duration=1.0, volume=0.6)
    elif "alert" in name:
        # Two tone
        part1 = generate_tone(880, 0.1, 0.5)
        part2 = generate_tone(440, 0.3, 0.5)
        data = part1 + part2
    else:
        # Default simple beep
        data = generate_tone(440, 0.3)
        
    return create_wav_base64(data)
