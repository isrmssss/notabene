"""
Document Parsers - RAG система для парсинга документов

Основной модуль для работы с документами различных форматов.
Использует синглтон паттерн для оптимизации памяти при обработке многих документов.

Основные компоненты:
- DocumentParserManager: основной класс для парсинга документов
- OcrParser: синглтон для распознавания текста из изображений
- Поддерживаемые форматы: PDF, DOCX, PPTX, TXT, MD, CSV, EPUB, изображения
"""

from parsers.manager import DocumentParserManager
from parsers.exceptions import UnsupportedFileError, CorruptedFileError

__all__ = [
    "DocumentParserManager",
    "UnsupportedFileError",
    "CorruptedFileError",
]

__version__ = "1.0.0"
