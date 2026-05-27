import io
import numpy as np
import easyocr
from PIL import Image
from pathlib import Path
from parsers.base import BaseParser

class OcrParser(BaseParser):
    def __init__(self):
        # gpu=False - явно указываем использование CPU (без видеокарты)
        # verbose=False - отключаем подробный вывод
        self.reader = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)

    def parse(self, file_path: Path) -> str:
        try:
            results = self.reader.readtext(str(file_path), detail=1)
            # Группируем текст по строкам на основе координат Y
            if not results:
                return ""
            
            # Сортируем по Y-координате (верх-низ), потом по X (слева-направо)
            results_sorted = sorted(results, key=lambda x: (round(x[0][0][1]), x[0][0][0]))
            
            text_lines = []
            current_line_y = None
            current_line_text = []
            
            for detection in results_sorted:
                # detection[0] - координаты, detection[1] - текст, detection[2] - уверенность
                text = detection[1]
                y_coord = round(detection[0][0][1])
                confidence = detection[2]
                
                # Пропускаем очень низкую уверенность
                if confidence < 0.3:
                    continue
                
                if current_line_y is None:
                    current_line_y = y_coord
                
                # Если Y-координата сильно отличается - новая строка
                if abs(y_coord - current_line_y) > 15:
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
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def parse_bytes(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            results = self.reader.readtext(np.array(image), detail=1)
            
            if not results:
                return ""
            
            # Сортируем по строкам
            results_sorted = sorted(results, key=lambda x: (round(x[0][0][1]), x[0][0][0]))
            
            text_lines = []
            current_line_y = None
            current_line_text = []
            
            for detection in results_sorted:
                text = detection[1]
                y_coord = round(detection[0][0][1])
                confidence = detection[2]
                
                if confidence < 0.3:
                    continue
                
                if current_line_y is None:
                    current_line_y = y_coord
                
                if abs(y_coord - current_line_y) > 15:
                    if current_line_text:
                        text_lines.append(" ".join(current_line_text))
                    current_line_text = [text]
                    current_line_y = y_coord
                else:
                    current_line_text.append(text)
            
            if current_line_text:
                text_lines.append(" ".join(current_line_text))
            
            return "\n".join(text_lines)
        except Exception as e:
            print(f"OCR Bytes Parse Error: {e}")
            return ""