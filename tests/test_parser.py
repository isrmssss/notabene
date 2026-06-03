import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# Теперь путь соберется правильно: корень_проекта/scripts
sys.path.append(str(project_root / "scripts"))

from parsers.manager import DocumentParserManager
from parsers.exceptions import UnsupportedFileError, CorruptedFileError


def print_device_info():
    """Выводит информацию о доступном устройстве (GPU/CPU)"""
    try:
        import torch
        device = "CUDA (GPU)" if torch.cuda.is_available() else "CPU"
        print(f"Device: {device}")
    except:
        print("Device: CPU")


def run_test(file_path_str: str, ocr_mode: str = "balanced"):
    # ocr_mode игнорируется (для обратной совместимости с тестами)
    # Используется только balanced режим из config.py
    manager = DocumentParserManager()
    path = Path(file_path_str)
    
    print(f"\n{'='*60}")
    print(f"📄 Testing file: {path.name}")
    print(f"{'='*60}")
    print(f"Absolute path: {path.absolute()}")
    print(f"File exists: {path.exists()}")
    
    try:
        start_time = time.time()
        result_text = manager.parse_file(path)
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Extraction Success")
        print(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
        print(f"📊 Total characters extracted: {len(result_text)}")
        print(f"📝 Total lines: {len(result_text.split(chr(10)))}")
        print(f"\n{'─'*60}")
        print(f"Text Preview (First 1000 chars):")
        print(f"{'─'*60}")
        print(result_text[:1000])
        print(f"{'─'*60}\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
    except UnsupportedFileError as e:
        print(f"\n❌ Unsupported format: {e}")
    except CorruptedFileError as e:
        print(f"\n❌ Corrupted file or OCR failure: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected system error: {str(e)}")


if __name__ == "__main__":
    print_device_info()
    print()
    
    sample_file = "sample.pdf"
    
    if len(sys.argv) > 1:
        sample_file = sys.argv[1]
    
    print(f"Testing file: {sample_file}\n")
    run_test(sample_file)
