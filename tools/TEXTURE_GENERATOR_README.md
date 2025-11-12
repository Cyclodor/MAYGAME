# 🎨 Генератор статических текстур

Этот инструмент позволяет генерировать **непроцедурные (статические) текстуры** в формате PNG для использования в игре.

## 📋 Что это даёт?

**Процедурные текстуры** (текущий подход):
- Генерируются каждый раз во время выполнения игры
- Могут быть медленнее при первой загрузке
- Ограничены возможностями pygame.draw

**Статические текстуры** (новый подход):
- Генерируются один раз, сохраняются как PNG файлы
- Загружаются мгновенно из файла
- Можно редактировать вручную в графических редакторах
- Более высокое качество благодаря антиалиасингу

## 🚀 Использование

### Базовое использование

```bash
python tools/texture_generator.py
```

Это сгенерирует все текстуры героев в папку `assets/sprites/`

### Генерация кастомных текстур

```python
from tools.texture_generator import generate_custom_texture
import pygame

def draw_my_texture(surface, width, height):
    """Ваша функция рисования"""
    surface.fill((100, 150, 200))
    pygame.draw.circle(surface, (255, 255, 0), 
                      (width//2, height//2), width//4)

# Генерируем текстуру
generate_custom_texture("my_custom_texture", callback=draw_my_texture)
```

## 📁 Структура файлов

После генерации файлы сохраняются в:
```
assets/sprites/
  ├── hero_human_warrior.png
  ├── hero_human_archer.png
  ├── hero_human_mage.png
  ├── hero_elf_warrior.png
  └── ...
```

## 🔧 Настройка

В файле `tools/texture_generator.py` можно настроить:

- `TEXTURE_SIZE` - размер итоговой текстуры (по умолчанию CELL_SIZE = 40)
- `GENERATION_SIZE` - размер при генерации (больше = лучше качество)
- `OUTPUT_DIR` - папка для сохранения текстур

## 🎯 Интеграция с игрой

После генерации текстур, игра автоматически будет использовать их, если они существуют в папке `assets/sprites/`. Если текстура не найдена, будет использована процедурная генерация как fallback.

## 🛠️ Альтернативные инструменты

Если вам нужны более сложные текстуры, можно использовать:

1. **GIMP / Photoshop** - для ручного редактирования сгенерированных текстур
2. **Aseprite** - для пиксельной графики
3. **AI генераторы** (Stable Diffusion, DALL-E) - для создания уникальных текстур
4. **Библиотеки Python**:
   - `PIL/Pillow` - уже установлена, для сложной обработки изображений
   - `opencv-python` - для фильтров и эффектов
   - `noise` - для генерации шумовых текстур (Procedural, но сохраняемых)

## 📝 Пример: Генерация текстур с шумами

```python
from tools.texture_generator import generate_custom_texture
from PIL import Image, ImageFilter
import numpy as np

def draw_noise_texture(surface, width, height):
    # Создаём шумовую текстуру
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Конвертируем обратно в pygame surface
    # ... (код конвертации)

generate_custom_texture("noise_background", callback=draw_noise_texture)
```

## 💡 Советы

1. **Качество**: Увеличьте `GENERATION_SIZE` для более детализированных текстур
2. **Производительность**: Статические текстуры загружаются быстрее
3. **Гибкость**: Можно комбинировать - некоторые текстуры статические, некоторые процедурные
4. **Редактирование**: После генерации можно открыть PNG в графическом редакторе и доработать


