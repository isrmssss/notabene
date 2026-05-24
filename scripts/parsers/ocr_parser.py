import io
import numpy as np
import easyocr
from PIL import Image
from pathlib import Path
from parsers.base import BaseParser

class OcrParser(BaseParser):
    def __init__(self):
        self.reader = easyocr.Reader(["ru", "en"])

    def parse(self, file_path: Path) -> str:
        results = self.reader.readtext(str(file_path), detail=0)
        return "\n".join(results)

    def parse_bytes(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            results = self.reader.readtext(np.array(image), detail=0)
            return "\n".join(results)
        except Exception:
            return ""