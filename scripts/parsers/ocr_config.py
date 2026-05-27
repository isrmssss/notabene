"""
Конфигурация для OCR парсера
"""

# Режимы работы OCR
OCR_MODES = {
    "fast": {
        "description": "Быстрый режим - минимальная точность, максимальная скорость",
        "min_confidence": 0.2,
        "resize_factor": 0.7,  # Уменьшаем размер на 30%
        "max_image_size": 1500,  # Максимальный размер в пикселях
    },
    "balanced": {
        "description": "Сбалансированный режим - оптимум скорость/точность",
        "min_confidence": 0.3,
        "resize_factor": 0.9,
        "max_image_size": 2500,
    },
    "accurate": {
        "description": "Точный режим - максимальная точность, медленнее",
        "min_confidence": 0.25,
        "resize_factor": 1.0,  # Оригинальный размер
        "max_image_size": 4000,
    },
}

# Параметры по умолчанию
DEFAULT_MODE = "balanced"
DEFAULT_CONFIDENCE_THRESHOLD = 0.3
DEFAULT_LINE_HEIGHT_TOLERANCE = 15  # Допустимое отклонение Y для одной строки

# Параллельная обработка
MAX_WORKERS = 4  # Количество потоков для параллельной обработки изображений
ENABLE_PARALLEL_PROCESSING = True

# Кэширование
ENABLE_RESULT_CACHE = True
CACHE_MAX_SIZE = 100  # Максимальное количество кэшированных результатов
CACHE_TTL = 3600  # Время жизни кэша в секундах (1 час)
