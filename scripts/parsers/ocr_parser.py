import io
import hashlib
import time
import numpy as np
import easyocr
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from parsers.base import BaseParser
from parsers.gpu_utils import should_use_gpu
from parsers.ocr_config import (
    DEFAULT_MODE, 
    OCR_MODES, 
    DEFAULT_LINE_HEIGHT_TOLERANCE,
    MAX_WORKERS,
    ENABLE_PARALLEL_PROCESSING,
    ENABLE_RESULT_CACHE,
    CACHE_MAX_SIZE,
    CACHE_TTL,
)


class OcrParser(BaseParser):
    _instance = None  # Для синглтона
    _reader = None
    _gpu_mode = None
    
    def __new__(cls, mode: str = DEFAULT_MODE):
        if cls._instance is None:
            cls._instance = super(OcrParser, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, mode: str = DEFAULT_MODE):
        # Инициализируем только один раз (синглтон)
        if self._initialized:
            return
        
        self._initialized = True
        self.mode = mode
        self.gpu_mode = should_use_gpu()
        
        # Получаем конфиг для режима
        if mode not in OCR_MODES:
            print(f"⚠️  Unknown mode '{mode}', using default '{DEFAULT_MODE}'")
            mode = DEFAULT_MODE
        
        self.config = OCR_MODES[mode]
        self.min_confidence = self.config["min_confidence"]
        self.resize_factor = self.config["resize_factor"]
        self.max_image_size = self.config["max_image_size"]
        
        print(f"🚀 Initializing OCR Parser...")
        print(f"   Mode: {mode} ({self.config['description']})")
        print(f"   Device: {'GPU ✓' if self.gpu_mode else 'CPU'}")
        print(f"   Min Confidence: {self.min_confidence}")
        print(f"   Resize Factor: {self.resize_factor}")
        
        # Инициализируем Reader один раз
        self._init_reader()
        
        # Кэш результатов
        self._result_cache = {}
        self._cache_times = {}
        
        print(f"✓ OCR Parser initialized successfully")
    
    def _init_reader(self):
        """Инициализирует easyocr Reader (делается один раз)"""
        if OcrParser._reader is None:
            OcrParser._reader = easyocr.Reader(
                ["ru", "en"], 
                gpu=self.gpu_mode,
                verbose=False
            )
    
    def _get_image_hash(self, image_data) -> str:
        """Получает хэш изображения для кэширования"""
        if isinstance(image_data, bytes):
            return hashlib.md5(image_data).hexdigest()
        return hashlib.md5(image_data.tobytes()).hexdigest()
    
    def _is_cache_valid(self, hash_key: str) -> bool:
        """Проверяет валидность кэша"""
        if not ENABLE_RESULT_CACHE:
            return False
        
        if hash_key not in self._cache_times:
            return False
        
        elapsed = time.time() - self._cache_times[hash_key]
        return elapsed < CACHE_TTL
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Оптимизирует размер изображения для обработки"""
        width, height = image.size
        
        # Если изображение меньше лимита, оставляем как есть
        if max(width, height) <= self.max_image_size:
            return image
        
        # Вычисляем новый размер
        scale = self.max_image_size / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def _process_ocr_results(self, results) -> str:
        """Обрабатывает результаты OCR и группирует текст по строкам"""
        if not results:
            return ""
        
        # Сортируем по Y-координате (верх-низ), потом по X (слева-направо)
        results_sorted = sorted(results, key=lambda x: (round(x[0][0][1]), x[0][0][0]))
        
        text_lines = []
        current_line_y = None
        current_line_text = []
        
        for detection in results_sorted:
            text = detection[1]
            y_coord = round(detection[0][0][1])
            confidence = detection[2]
            
            # Пропускаем низкую уверенность
            if confidence < self.min_confidence:
                continue
            
            if current_line_y is None:
                current_line_y = y_coord
            
            # Если Y-координата сильно отличается - новая строка
            if abs(y_coord - current_line_y) > DEFAULT_LINE_HEIGHT_TOLERANCE:
                if current_line_text:
                    text_lines.append(" ".join(current_line_text))
                current_line_text = [text]
                current_line_y = y_coord
            else:
                current_line_text.append(text)
        
        # Добавляем последнюю строку
        if current_line_text:
            text_lines.append(" ".join(current_line_text))
        
        return "\n".join(text_lines)

    def parse(self, file_path: Path) -> str:
        """Парсит текст из файла изображения"""
        try:
            file_path = Path(file_path)
            
            # Проверяем кэш
            if ENABLE_RESULT_CACHE:
                with open(file_path, "rb") as f:
                    file_hash = self._get_image_hash(f.read())
                
                if file_hash in self._result_cache and self._is_cache_valid(file_hash):
                    print(f"📦 Cache hit for {file_path.name}")
                    return self._result_cache[file_hash]
            
            results = OcrParser._reader.readtext(str(file_path), detail=1)
            text = self._process_ocr_results(results)
            
            # Сохраняем в кэш
            if ENABLE_RESULT_CACHE and file_hash:
                self._result_cache[file_hash] = text
                self._cache_times[file_hash] = time.time()
                
                # Ограничиваем размер кэша
                if len(self._result_cache) > CACHE_MAX_SIZE:
                    oldest_key = min(self._cache_times, key=self._cache_times.get)
                    del self._result_cache[oldest_key]
                    del self._cache_times[oldest_key]
            
            return text
        except Exception as e:
            print(f"❌ OCR Error: {e}")
            return ""

    def parse_bytes(self, image_bytes: bytes) -> str:
        """Парсит текст из байтов изображения"""
        try:
            # Проверяем кэш
            if ENABLE_RESULT_CACHE:
                image_hash = self._get_image_hash(image_bytes)
                
                if image_hash in self._result_cache and self._is_cache_valid(image_hash):
                    print(f"📦 Cache hit for image")
                    return self._result_cache[image_hash]
            else:
                image_hash = None
            
            # Открываем и обрабатываем изображение
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Оптимизируем размер
            image = self._resize_image(image)
            
            # Выполняем OCR
            results = OcrParser._reader.readtext(np.array(image), detail=1)
            text = self._process_ocr_results(results)
            
            # Сохраняем в кэш
            if ENABLE_RESULT_CACHE and image_hash:
                self._result_cache[image_hash] = text
                self._cache_times[image_hash] = time.time()
                
                # Ограничиваем размер кэша
                if len(self._result_cache) > CACHE_MAX_SIZE:
                    oldest_key = min(self._cache_times, key=self._cache_times.get)
                    del self._result_cache[oldest_key]
                    del self._cache_times[oldest_key]
            
            return text
        except Exception as e:
            print(f"❌ OCR Bytes Parse Error: {e}")
            return ""
    
    def parse_multiple(self, image_bytes_list: list) -> list:
        """
        Парсит несколько изображений параллельно
        Args:
            image_bytes_list: Список байтов изображений
        Returns:
            Список распознанных текстов
        """
        if not ENABLE_PARALLEL_PROCESSING:
            return [self.parse_bytes(img) for img in image_bytes_list]
        
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(self.parse_bytes, image_bytes_list))
        
        return results
    
    def clear_cache(self):
        """Очищает кэш результатов"""
        self._result_cache.clear()
        self._cache_times.clear()
        print("🗑️  OCR cache cleared")
    
    def get_stats(self) -> dict:
        """Возвращает статистику работы"""
        return {
            "mode": self.mode,
            "device": "GPU" if self.gpu_mode else "CPU",
            "cache_size": len(self._result_cache),
            "min_confidence": self.min_confidence,
            "resize_factor": self.resize_factor,
        }