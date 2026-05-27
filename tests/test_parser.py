import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# Теперь путь соберется правильно: корень_проекта/scripts
sys.path.append(str(project_root / "scripts"))

from parsers.manager import DocumentParserManager
from parsers.exceptions import UnsupportedFileError, CorruptedFileError
from parsers.gpu_utils import print_device_info
from parsers.ocr_config import OCR_MODES

def run_test(file_path_str: str, ocr_mode: str = "balanced"):
    manager = DocumentParserManager(ocr_mode=ocr_mode)
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
        print(f"\n❌ Unsupported format: {e.message}")
    except CorruptedFileError as e:
        print(f"\n❌ Corrupted file or OCR failure: {e.message}")
    except Exception as e:
        print(f"\n❌ Unexpected system error: {str(e)}")

if __name__ == "__main__":
    print_device_info()
    print()
    
    # Выводим доступные режимы
    print("🎯 Available OCR Modes:")
    for mode_name, mode_config in OCR_MODES.items():
        print(f"   • {mode_name}: {mode_config['description']}")
    print()
    
    ocr_mode = "balanced"  # По умолчанию
    sample_file = "sample.pdf"
    
    if len(sys.argv) > 1:
        sample_file = sys.argv[1]
        # Проверяем если передан режим
        if len(sys.argv) > 2:
            ocr_mode = sys.argv[2]
            if ocr_mode not in OCR_MODES:
                print(f"⚠️  Unknown mode '{ocr_mode}', using 'balanced'")
                ocr_mode = "balanced"
    
    print(f"Using OCR mode: {ocr_mode}\n")
    run_test(sample_file, ocr_mode=ocr_mode)