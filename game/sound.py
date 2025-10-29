import os
from pygame import mixer

def load_sound(name, extension='wav'):
    """Загружает звуковой файл. Поддерживает WAV и MP3 форматы."""
    try:
        # Пробуем загрузить с указанным расширением
        path = os.path.join('assets', 'sounds', f'{name}.{extension}')
        if os.path.exists(path):
            return mixer.Sound(path)
        # Если не найден, пробуем WAV
        if extension != 'wav':
            path = os.path.join('assets', 'sounds', f'{name}.wav')
            if os.path.exists(path):
                return mixer.Sound(path)
        return None
    except Exception as e:
        print(f"Ошибка загрузки звука: {name}.{extension} - {e}")
        return None

def load_sound_mp3(name):
    """Загружает MP3 звуковой файл."""
    return load_sound(name, extension='mp3') 