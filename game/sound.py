import os
from pygame import mixer

def load_sound(name):
    try:
        return mixer.Sound(os.path.join('assets', 'sounds', f'{name}.wav'))
    except:
        print(f"Ошибка загрузки звука: {name}")
        return None 