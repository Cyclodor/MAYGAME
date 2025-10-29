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

def create_bow_draw(filename):
    """Создает звук натяжения лука - глубокое натягивание тетивы с вибрацией"""
    sample_rate = 44100
    duration = 0.4
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            progress = t / duration
            
            # Основной тон - глубокое натяжение (60-120 Гц, как вибрация тетивы)
            base_freq = 60 + 60 * progress
            tone = math.sin(2 * math.pi * base_freq * t)
            
            # Обертоны для реалистичности
            tone += 0.5 * math.sin(2 * math.pi * base_freq * 2 * t)
            tone += 0.3 * math.sin(2 * math.pi * base_freq * 3 * t)
            tone += 0.15 * math.sin(2 * math.pi * base_freq * 4 * t)
            
            # Вибрация тетивы (быстрое дрожание)
            vibration_freq = 400 + 200 * progress
            vibration = 0.2 * math.sin(2 * math.pi * vibration_freq * t) * (1 - progress * 0.7)
            tone += vibration
            
            # Энvelope: плавное нарастание напряжения
            if progress < 0.85:
                # Постепенное нарастание
                envelope = progress * 0.8
            else:
                # Финальное напряжение перед выстрелом
                tension = (progress - 0.85) / 0.15
                envelope = 0.68 + 0.32 * tension
            
            volume = 0.35
            value = int(volume * 32767.0 * tone * envelope)
            value = max(-32767, min(32767, value))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

def create_arrow_shot(filename):
    """Создает звук выстрела стрелой - характерный 'твинг' тетивы"""
    sample_rate = 44100
    duration = 0.25
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            progress = t / duration
            
            # Характерный "твинг" тетивы - основной звук выстрела
            # Начальная частота резко падает (щелчок тетивы)
            twang_freq_start = 800
            twang_freq_end = 200
            twang_freq = twang_freq_start * math.exp(-3 * progress)
            twang = math.sin(2 * math.pi * twang_freq * t)
            
            # Обертоны для богатого звука тетивы
            twang += 0.6 * math.sin(2 * math.pi * twang_freq * 2 * t)
            twang += 0.4 * math.sin(2 * math.pi * twang_freq * 3 * t)
            twang += 0.2 * math.sin(2 * math.pi * twang_freq * 4 * t)
            
            # Низкочастотный ударный импульс (вибрация лука)
            impact_freq = 100 * math.exp(-10 * progress)
            impact = 0.5 * math.sin(2 * math.pi * impact_freq * t)
            twang += impact
            
            # Высокочастотный свист летящей стрелы
            if progress < 0.6:
                whistle_freq = 1200 + 800 * (1 - progress)
                whistle = 0.25 * math.sin(2 * math.pi * whistle_freq * t)
                twang += whistle
            
            # Энvelope: резкий пик в самом начале, затем быстрое затухание
            if progress < 0.1:
                # Пиковый момент выстрела
                envelope = 1.0
            elif progress < 0.3:
                # Быстрое затухание твинга
                envelope = 1.0 - (progress - 0.1) * 4.5
            else:
                # Медленное затухание остаточных вибраций
                envelope = math.exp(-8 * (progress - 0.3))
            
            volume = 0.5
            value = int(volume * 32767.0 * twang * envelope)
            value = max(-32767, min(32767, value))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

def create_arrow_hit(filename):
    """Создает звук попадания стрелы в цель - четкий удар с вибрацией"""
    sample_rate = 44100
    duration = 0.12
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            progress = t / duration
            
            # Резкий ударный импульс (попадание)
            impact_freq = 180 * math.exp(-12 * progress)
            impact = math.sin(2 * math.pi * impact_freq * t)
            
            # Обертоны для реалистичного звука удара
            impact += 0.6 * math.sin(2 * math.pi * impact_freq * 2 * t)
            impact += 0.35 * math.sin(2 * math.pi * impact_freq * 3 * t)
            impact += 0.2 * math.sin(2 * math.pi * impact_freq * 4 * t)
            impact += 0.1 * math.sin(2 * math.pi * impact_freq * 5 * t)
            
            # Высокочастотный щелчок (звук проникновения)
            if progress < 0.3:
                crack_freq = 800 * math.exp(-15 * progress)
                crack = 0.3 * math.sin(2 * math.pi * crack_freq * t)
                impact += crack
            
            # Низкочастотный грохот (отдача в цель)
            rumble_freq = 80 * math.exp(-6 * progress)
            rumble = 0.25 * math.sin(2 * math.pi * rumble_freq * t)
            impact += rumble
            
            # Энvelope: очень резкий пик в начале, быстрое затухание
            if progress < 0.05:
                envelope = 1.0
            else:
                # Быстрое затухание с остаточными вибрациями
                envelope = math.exp(-15 * progress)
            
            volume = 0.55
            value = int(volume * 32767.0 * impact * envelope)
            value = max(-32767, min(32767, value))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

# Создаем директорию для звуков, если её нет
os.makedirs('assets/sounds', exist_ok=True)

# Создаем звуки
create_sound('assets/sounds/attack.wav', 440, 0.1)  # Звук атаки
create_sound('assets/sounds/death.wav', 220, 0.3)   # Звук смерти
create_sound('assets/sounds/spell.wav', 880, 0.2)   # Звук заклинания

# Создаем звуки для стрельбы из лука
create_bow_draw('assets/sounds/bow_draw.wav')       # Звук натяжения лука
create_arrow_shot('assets/sounds/arrow_shot.wav')   # Звук выстрела стрелой
create_arrow_hit('assets/sounds/arrow_hit.wav')     # Звук попадания стрелой 