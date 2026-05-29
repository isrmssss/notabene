"""
Менеджер для парсинга документов различных форматов

Является основной точкой входа для работы с документами.
Автоматически определяет формат и выбирает подходящий парсер.
"""

from pathlib import Path
from typing import Union

from parsers.ocr import OcrParser
from parsers.formats import (
    PlainTextParser, PdfParser, DocxParser, 
    PptxParser, CsvParser, EpubParser
)
from parsers.exceptions import UnsupportedFileError, CorruptedFileError


class DocumentParserManager:
    """
    Менеджер для парсинга документов
    
    Использует синглтон паттерн для OcrParser для оптимизации памяти.
    
    ВАЖНО для синглтона:
        # Создавайте ОДИН раз на старте приложения
        manager = DocumentParserManager()
        
        # Переиспользуйте для всех документов
        text = manager.parse_file("doc1.pdf")
        text = manager.parse_file("doc2.pdf")
        
        # Результат: первый документ с инициализацией Reader,
        # остальные быстрее благодаря синглтону
    """
    
    def __init__(self):
        self._parsers = {}
        self._ocr_parser = OcrParser()  # Синглтон - создается один раз
        self._register_parsers()
    
    def _register_parsers(self):
        """Регистрирует парсеры для различных форматов"""
        text_parser = PlainTextParser()
        
        self._parsers[".txt"] = text_parser
        self._parsers[".md"] = text_parser
        self._parsers[".csv"] = CsvParser()
        self._parsers[".epub"] = EpubParser()
        self._parsers[".pdf"] = PdfParser(self._ocr_parser)
        self._parsers[".docx"] = DocxParser(self._ocr_parser)
        self._parsers[".pptx"] = PptxParser(self._ocr_parser)
        
        # Расширения для изображений
        image_extensions = [
            ".avif", ".bmp", ".gif", ".ico", ".jp2", ".png", 
            ".webp", ".tif", ".tiff", ".heic", ".heif", ".jpeg", 
            ".jpg", ".jpe"
        ]
        for ext in image_extensions:
            self._parsers[ext] = self._ocr_parser
    
    def _validate_file_type(self, path: Path, ext: str) -> str:
        """Проверяет реальный тип файла по сигнатуре"""
        try:
            with open(path, "rb") as f:
                header = f.read(4)
            
            if header.startswith(b"%PDF"):
                return ".pdf"
            if header.startswith(b"PK\x03\x04"):
                if ext in [".docx", ".pptx", ".epub"]:
                    return ext
                return ".docx"
            if header.startswith(b"\x89PNG"):
                return ".png"
            if header.startswith(b"\xff\xd8\xff"):
                return ".jpg"
        except Exception:
            pass
        
        return ext
    
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        Парсит файл и возвращает текст
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Распознанный текст из файла
            
        Raises:
            FileNotFoundError: Если файл не найден
            UnsupportedFileError: Если формат не поддерживается
            CorruptedFileError: Если произошла ошибка при парсинге
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found at: {path}")
        
        ext = path.suffix.lower()
        real_ext = self._validate_file_type(path, ext)
        
        if real_ext not in self._parsers:
            raise UnsupportedFileError(f"Extension '{real_ext}' is not supported.")
        
        try:
            text = self._parsers[real_ext].parse(path)
            return text
        except (FileNotFoundError, UnsupportedFileError):
            raise
        except Exception as e:
            raise CorruptedFileError(f"Error parsing {real_ext.upper()} file: {str(e)}")
