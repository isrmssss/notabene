from pathlib import Path
from parsers.ocr_parser import OcrParser
from parsers.exceptions import UnsupportedFileError, CorruptedFileError
from parsers.text_parser import (
    PlainTextParser, PdfParser, DocxParser, 
    PptxParser, CsvParser, EpubParser
)

class DocumentParserManager:
    def __init__(self):
        self._parsers = {}
        self._register_default_parsers()

    def _register_default_parsers(self):
        ocr_parser = OcrParser()
        text_parser = PlainTextParser()
        
        self._parsers[".txt"] = text_parser
        self._parsers[".md"] = text_parser
        self._parsers[".csv"] = CsvParser()
        self._parsers[".epub"] = EpubParser()
        self._parsers[".pdf"] = PdfParser(ocr_parser)
        self._parsers[".docx"] = DocxParser(ocr_parser)
        self._parsers[".pptx"] = PptxParser(ocr_parser)
        
        image_extensions = [
            ".avif", ".bmp", ".gif", ".ico", ".jp2", ".png", 
            ".webp", ".tif", ".tiff", ".heic", ".heif", ".jpeg", 
            ".jpg", ".jpe"
        ]
        for ext in image_extensions:
            self._parsers[ext] = ocr_parser

    def _validate_real_type(self, path: Path, ext: str) -> str:
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
        except Exception as e:
            raise CorruptedFileError(f"Failed to read file signature: {str(e)}")
        return ext

    def parse_file(self, file_path: str | Path) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found at: {path}")
            
        ext = path.suffix.lower()
        real_ext = self._validate_real_type(path, ext)
        
        if real_ext not in self._parsers:
            raise UnsupportedFileError(f"Extension '{real_ext}' is not supported.")
            
        try:
            return self._parsers[real_ext].parse(path)
        except Exception as e:
            raise CorruptedFileError(f"Error parsing {real_ext.upper()} file: {str(e)}")


### ИНСТРУКЦИЯ ПО ЗАПУСКУ ###
# from parsers.manager import DocumentParserManager

# manager = DocumentParserManager()
# extracted_text = manager.parse_file("path/to/document.pdf")