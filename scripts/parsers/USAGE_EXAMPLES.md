# Примеры использования оптимизированного OCR парсера

## 🚀 Базовое использование

```python
from parsers.manager import DocumentParserManager

# Инициализируем менеджер (сбалансированный режим по умолчанию)
manager = DocumentParserManager()

# Парсим документ
text = manager.parse_file("document.pdf")
print(text)
```

## ⚡ Быстрый режим для больших объемов

```python
from parsers.manager import DocumentParserManager

# Инициализируем в быстром режиме
manager = DocumentParserManager(ocr_mode="fast")

# Обрабатываем много документов (будет быстро)
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
for doc in documents:
    text = manager.parse_file(doc)
    # Вторая и далее обработка: ~5-7 сек (вместо 15-20 сек)
    print(f"Processed {doc}")
```

## 📖 Точный режим для важных документов

```python
from parsers.manager import DocumentParserManager

# Инициализируем в точном режиме
manager = DocumentParserManager(ocr_mode="accurate")

# Парсим важный документ
text = manager.parse_file("important_contract.pdf")
print(text)  # Максимальная точность
```

## 🔄 Параллельная обработка изображений

```python
from parsers.ocr_parser import OcrParser

# Инициализируем парсер
ocr_parser = OcrParser(mode="balanced")

# Обрабатываем несколько изображений параллельно
images_data = [
    open("image1.png", "rb").read(),
    open("image2.png", "rb").read(),
    open("image3.png", "rb").read(),
]

# Обрабатываются параллельно (4 потока)
results = ocr_parser.parse_multiple(images_data)

for i, text in enumerate(results):
    print(f"Image {i}: {text}")
```

## 💾 Использование кэширования

```python
from parsers.ocr_parser import OcrParser

ocr_parser = OcrParser()

# Первый вызов - обрабатывается (~3-5 секунд)
image_bytes = open("screenshot.png", "rb").read()
text1 = ocr_parser.parse_bytes(image_bytes)  # ~3-5s

# Второй вызов того же изображения - из кэша (<0.1 секунды)
text2 = ocr_parser.parse_bytes(image_bytes)  # <0.1s ✓

# Очистить кэш если нужно
ocr_parser.clear_cache()
```

## 🌐 Веб-приложение (Flask/FastAPI)

```python
from fastapi import FastAPI
from parsers.manager import DocumentParserManager

app = FastAPI()

# Инициализируем ОДИН РАЗ при запуске приложения
parser_manager = DocumentParserManager(ocr_mode="balanced")

@app.post("/parse")
async def parse_document(file: UploadFile):
    """Парсит документ и возвращает текст"""
    # Сохраняем временный файл
    with open("/tmp/temp_doc", "wb") as tmp:
        tmp.write(await file.read())
    
    # Парсим (быстро благодаря синглтону и кэшированию!)
    text = parser_manager.parse_file("/tmp/temp_doc")
    
    return {"text": text, "chars": len(text)}
```

## 🎯 Выбор режима в зависимости от сценария

```python
from parsers.manager import DocumentParserManager
import time

# СЦЕНАРИЙ 1: Необходимо быстро
print("⚡ Fast processing")
start = time.time()
manager = DocumentParserManager(ocr_mode="fast")
text = manager.parse_file("doc.pdf")
print(f"Time: {time.time() - start:.1f}s")

# СЦЕНАРИЙ 2: Оптимум (рекомендуется)
print("✓ Balanced processing")
start = time.time()
manager = DocumentParserManager(ocr_mode="balanced")
text = manager.parse_file("doc.pdf")
print(f"Time: {time.time() - start:.1f}s")

# СЦЕНАРИЙ 3: Нужна максимальная точность
print("📖 Accurate processing")
start = time.time()
manager = DocumentParserManager(ocr_mode="accurate")
text = manager.parse_file("doc.pdf")
print(f"Time: {time.time() - start:.1f}s")
```

## 🖥️ Использование GPU (если доступна)

```python
import os
from parsers.manager import DocumentParserManager
from parsers.gpu_utils import get_device_info

# Выводим информацию об устройстве
info = get_device_info()
print(f"CUDA Available: {info['cuda_available']}")
if info['cuda_available']:
    print(f"GPU: {info['device_name']}")
    print(f"Memory: {info['total_memory']:.1f} GB")

# Парсим (будет использована GPU если доступна)
manager = DocumentParserManager(ocr_mode="balanced")
text = manager.parse_file("document.pdf")
```

## 🔧 Форсирование CPU или GPU

```python
import os

# Форсировать GPU (даже если slow)
os.environ["NOTABENE_FORCE_GPU"] = "1"
from parsers.manager import DocumentParserManager
manager = DocumentParserManager()

# Форсировать CPU (даже если есть GPU)
os.environ["NOTABENE_FORCE_CPU"] = "1"
from parsers.manager import DocumentParserManager
manager = DocumentParserManager()
```

## 📊 Получение статистики

```python
from parsers.ocr_parser import OcrParser

ocr_parser = OcrParser(mode="balanced")

# Парсим что-то
text = ocr_parser.parse_bytes(image_data)

# Получаем статистику
stats = ocr_parser.get_stats()
print(f"Mode: {stats['mode']}")
print(f"Device: {stats['device']}")
print(f"Cache size: {stats['cache_size']}")
print(f"Min confidence: {stats['min_confidence']}")
```

## 🧪 Тестирование

```bash
# Просмотр доступных режимов и информации об устройстве
python test_parser.py "document.pdf" "balanced"

# Быстрый режим
python test_parser.py "document.pdf" "fast"

# Точный режим
python test_parser.py "document.pdf" "accurate"
```

## ⚙️ Кастомизация конфигурации

Отредактируйте `ocr_config.py` для изменения параметров:

```python
# Измените пороги уверенности
OCR_MODES["balanced"]["min_confidence"] = 0.35

# Измените максимальный размер изображения
OCR_MODES["fast"]["max_image_size"] = 1200

# Измените количество потоков
MAX_WORKERS = 8

# Отключите кэширование
ENABLE_RESULT_CACHE = False

# Измените размер кэша
CACHE_MAX_SIZE = 50
```

## 💡 Pro Tips

1. **Синглтон магия:** Первый документ ~15-20s, остальные ~5-7s
2. **Режимы:** fast для батча, balanced для нормального использования, accurate для важных документов
3. **Параллельная обработка:** Используйте `parse_multiple()` для нескольких изображений
4. **Кэширование:** Одно изображение в память - второй раз <0.1s
5. **GPU:** Автоматически используется если доступна, дает 3-5x ускорение

## 🚨 Важно

- OCR Reader инициализируется один раз (первый вызов)
- Последующие документы намного быстрее благодаря синглтону
- Это нормально что первый документ медленнее
- На GPU ускорение может быть 5-10x
- Кэширование работает отлично для повторяющихся изображений
