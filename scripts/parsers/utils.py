import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Удаляем управляющие символы, но СОХРАНЯЕМ переводы строк
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Заменяем множественные пробелы/табы на один (но НЕ переводы строк)
    text = re.sub(r"[ \t]+", " ", text)
    # Удаляем пустые строки
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)