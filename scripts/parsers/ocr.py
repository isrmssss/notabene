"""
OCR парсер для распознавания текста из изображений

Использует easyocr для поддержки русского и английского языков.
Реализован как синглтон для оптимизации памяти при обработке многих документов.
"""

import io
import hashlib
import time
import numpy as np
import easyocr
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from parsers.base import BaseParser
from parsers.ocr_config import OCR_CONFIG, MAX_WORKERS, ENABLE_PARALLEL_PROCESSING, ENABLE_RESULT_CACHE, CACHE_MAX_SIZE, CACHE_TTL

# Константы
MIN_CONFIDENCE = OCR_CONFIG["min_confidence"]
RESIZE_FACTOR = OCR_CONFIG["resize_factor"]
MAX_IMAGE_SIZE = OCR_CONFIG["max_image_size"]
LINE_HEIGHT_TOLERANCE = 15


class OcrParser(BaseParser):
    """
    Синглтон парсер для OCR распознавания
    
    Инициализирует easyocr Reader один раз и переиспользует для всех документов.
    Поддерживает кэширование результатов для повторяющихся изображений.
    
    Пример использования (ВАЖНО - синглтон):
        # Создаете один раз на старте приложения
        from parsers.ocr import OcrParser
        ocr = OcrParser()
        
        # Переиспользуете для всех документов
        text1 = ocr.parse_bytes(image_bytes_1)
        text2 = ocr.parse_bytes(image_bytes_2)
        
        # Результат: первый ~3-5 сек, остальные быстрее благодаря синглтону
    """
    
    _instance: Optional['OcrParser'] = None
    _reader: Optional[easyocr.Reader] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OcrParser, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Инициализируем только один раз (синглтон)
        if self._initialized:
            return
        
        self._initialized = True
        self._init_reader()
        self._result_cache = {}
        self._cache_times = {}
    
    def _init_reader(self):
        """Инициализирует easyocr Reader один раз"""
        if OcrParser._reader is not None:
            return
        
        OcrParser._reader = easyocr.Reader(
            ["ru", "en"],
            gpu=self._should_use_gpu(),
            verbose=False
        )
    
    @staticmethod
    def _should_use_gpu() -> bool:
        """Определяет, использовать ли GPU"""
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False
    
    def _get_image_hash(self, image_data: bytes) -> str:
        """Получает хэш изображения для кэширования"""
        return hashlib.md5(image_data).hexdigest()
    
    def _is_cache_valid(self, hash_key: str) -> bool:
        """Проверяет валидность кэша"""
        if not ENABLE_RESULT_CACHE or hash_key not in self._cache_times:
            return False
        elapsed = time.time() - self._cache_times[hash_key]
        return elapsed < CACHE_TTL
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Оптимизирует размер изображения"""
        width, height = image.size
        if max(width, height) <= MAX_IMAGE_SIZE:
            return image
        scale = MAX_IMAGE_SIZE / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def _process_results(self, results) -> str:
        """Обрабатывает результаты OCR и группирует текст по строкам"""
        if not results:
            return ""
        
        results_sorted = sorted(results, key=lambda x: (round(x[0][0][1]), x[0][0][0]))
        
        text_lines = []
        current_line_y = None
        current_line_text = []
        
        for detection in results_sorted:
            text = detection[1]
            y_coord = round(detection[0][0][1])
            confidence = detection[2]
            
            if confidence < MIN_CONFIDENCE:
                continue
            
            if current_line_y is None:
                current_line_y = y_coord
            
            if abs(y_coord - current_line_y) > LINE_HEIGHT_TOLERANCE:
                if current_line_text:
                    text_lines.append(" ".join(current_line_text))
                current_line_text = [text]
                current_line_y = y_coord
            else:
                current_line_text.append(text)
        
        if current_line_text:
            text_lines.append(" ".join(current_line_text))
        
        return "\n".join(text_lines)

    def parse(self, file_path: Path) -> str:
        """Парсит текст из файла изображения"""
        file_path = Path(file_path)
        
        if ENABLE_RESULT_CACHE:
            with open(file_path, "rb") as f:
                file_hash = self._get_image_hash(f.read())
            
            if self._is_cache_valid(file_hash):
                return self._result_cache[file_hash]
        else:
            file_hash = None
        
        results = OcrParser._reader.readtext(str(file_path), detail=1)
        text = self._process_results(results)
        
        if ENABLE_RESULT_CACHE and file_hash:
            self._result_cache[file_hash] = text
            self._cache_times[file_hash] = time.time()
            if len(self._result_cache) > CACHE_MAX_SIZE:
                oldest_key = min(self._cache_times, key=self._cache_times.get)
                del self._result_cache[oldest_key]
                del self._cache_times[oldest_key]
        
        return text

    def parse_bytes(self, image_bytes: bytes) -> str:
        """Парсит текст из байтов изображения"""
        if ENABLE_RESULT_CACHE:
            image_hash = self._get_image_hash(image_bytes)
            if self._is_cache_valid(image_hash):
                return self._result_cache[image_hash]
        else:
            image_hash = None
        
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = self._resize_image(image)
        results = OcrParser._reader.readtext(np.array(image), detail=1)
        text = self._process_results(results)
        
        if ENABLE_RESULT_CACHE and image_hash:
            self._result_cache[image_hash] = text
            self._cache_times[image_hash] = time.time()
            if len(self._result_cache) > CACHE_MAX_SIZE:
                oldest_key = min(self._cache_times, key=self._cache_times.get)
                del self._result_cache[oldest_key]
                del self._cache_times[oldest_key]
        
        return text
    
    def parse_multiple(self, image_bytes_list: List[bytes]) -> List[str]:
        """Парсит несколько изображений параллельно"""
        if not ENABLE_PARALLEL_PROCESSING or len(image_bytes_list) == 1:
            return [self.parse_bytes(img) for img in image_bytes_list]
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(self.parse_bytes, image_bytes_list))
        
        return results
    
    def clear_cache(self):
        """Очищает кэш результатов"""
        self._result_cache.clear()
        self._cache_times.clear()
