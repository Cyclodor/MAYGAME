import wave
import struct
import math
import os

def create_sound(filename, frequency, duration, volume=0.5):
    # Параметры звука
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    
    # Создаем WAV файл
    with wave.open(filename, 'w') as wav_file:
        # Устанавливаем параметры
        wav_file.setnchannels(1)  # Моно
        wav_file.setsampwidth(2)  # 2 байта на сэмпл
        wav_file.setframerate(sample_rate)
        
        # Генерируем звук
        for i in range(num_samples):
            value = int(volume * 32767.0 * math.sin(2 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

# Создаем директорию для звуков, если её нет
os.makedirs('assets/sounds', exist_ok=True)

# Создаем звуки
create_sound('assets/sounds/attack.wav', 440, 0.1)  # Звук атаки
create_sound('assets/sounds/death.wav', 220, 0.3)   # Звук смерти
create_sound('assets/sounds/spell.wav', 880, 0.2)   # Звук заклинания 