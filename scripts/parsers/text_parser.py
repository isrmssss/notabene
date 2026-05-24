import csv
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
from parsers.base import BaseParser
from parsers.ocr_parser import OcrParser
from parsers.utils import clean_text

class PlainTextParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        encodings = ["utf-8", "windows-1251", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return clean_text(f.read())
            except UnicodeDecodeError:
                continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return clean_text(f.read())
        except Exception:
            return ""

class PdfParser(BaseParser):
    def __init__(self, ocr_parser: OcrParser):
        self.ocr_parser = ocr_parser

    def parse(self, file_path: Path) -> str:
        text = []
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                try:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
                except Exception:
                    pass
                
                try:
                    for image_file_object in page.images:
                        ocr_text = self.ocr_parser.parse_bytes(image_file_object.data)
                        if ocr_text:
                            text.append(ocr_text)
                except Exception:
                    pass
        except Exception:
            return ""
        return clean_text("\n".join(text))

class DocxParser(BaseParser):
    def __init__(self, ocr_parser: OcrParser):
        self.ocr_parser = ocr_parser

    def parse(self, file_path: Path) -> str:
        text = []
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text.append(paragraph.text)
            
            for rel_id, part in doc.part.related_parts.items():
                try:
                    if "image" in part.contentType:
                        ocr_text = self.ocr_parser.parse_bytes(part.blob)
                        if ocr_text:
                            text.append(ocr_text)
                except Exception:
                    pass
        except Exception:
            return ""
        return clean_text("\n".join(text))

class PptxParser(BaseParser):
    def __init__(self, ocr_parser: OcrParser):
        self.ocr_parser = ocr_parser

    def parse(self, file_path: Path) -> str:
        text = []
        try:
            prs = Presentation(file_path)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        text.append(shape.text)
                
                for rel_id, part in slide.part.related_parts.items():
                    try:
                        if "image" in part.contentType:
                            ocr_text = self.ocr_parser.parse_bytes(part.blob)
                            if ocr_text:
                                text.append(ocr_text)
                    except Exception:
                        pass
        except Exception:
            return ""
        return clean_text("\n".join(text))

class CsvParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        text = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    text.append(" ".join(row))
        except Exception:
            return ""
        return clean_text("\n".join(text))

class EpubParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        text = []
        try:
            book = epub.read_epub(file_path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    text.append(soup.get_text())
        except Exception:
            return ""
        return clean_text("\n".join(text))