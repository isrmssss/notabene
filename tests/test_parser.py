import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# Теперь путь соберется правильно: корень_проекта/scripts
sys.path.append(str(project_root / "scripts"))

from parsers.manager import DocumentParserManager
from parsers.exceptions import UnsupportedFileError, CorruptedFileError

def run_test(file_path_str: str):
    manager = DocumentParserManager()
    path = Path(file_path_str)
    
    print(f"=== Testing file: {path.name} ===")
    print(f"Absolute path: {path.absolute()}")
    print(f"File exists: {path.exists()}")
    
    try:
        result_text = manager.parse_file(path)
        print("\n--- Extraction Success ---")
        print(f"Total characters extracted: {len(result_text)}")
        print("\n--- Text Preview (First 1000 chars) ---")
        print(result_text[:1000])
        print("\n---------------------------------------")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] File not found: {e}")
    except UnsupportedFileError as e:
        print(f"\n[ERROR] Unsupported format: {e.message}")
    except CorruptedFileError as e:
        print(f"\n[ERROR] Corrupted file or OCR failure: {e.message}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected system error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_test(sys.argv[1])
    else:
        sample_file = "sample.pdf"
        run_test(sample_file)