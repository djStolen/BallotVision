import argparse
import json
from pathlib import Path
from ballot_vision.ocr.paddle_engine import PaddleOCREngine

def main():
    # Setup argument parsing to accept the directory path dynamically
    parser = argparse.ArgumentParser(description="OCR all images and PDF documents in a directory.")
    parser.add_argument("folder", type=str, help="Relative path to the folder containing images or PDFs")
    args = parser.parse_args()

    # Initialize the OCR Engine
    # Ensure you updated paddle_engine.py to handle multi-page results as well!
    engine = PaddleOCREngine()
    
    # Create Path object for the target directory
    source_dir = Path(args.folder)
    
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Error: Directory '{args.folder}' does not exist or is not a directory.")
        return

    # Supported image and document extensions (including PDFs)
    valid_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".pdf"}

    print(f"Scanning directory: {source_dir.resolve()}")
    processed_count = 0
    failed_count = 0

    # Iterate through all files in the targeted directory
    for file_path in source_dir.iterdir():
        if file_path.suffix.lower() in valid_extensions:
            print(f"\n--- Processing: {file_path.name} ---")
            
            try:
                # Execute text extraction (handles multi-page documents seamlessly)
                results = engine.extract_text(str(file_path))
                
                # Establish the output path to save the .json file next to the source file
                output_path = file_path.with_suffix(".json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"Successfully saved OCR results to: {output_path}")
                processed_count += 1
                
            except Exception as e:
                print(f"Failed to process {file_path.name}: {e}")
                failed_count += 1

    print(f"\n========================================")
    print(f"OCR Run Completed: {processed_count} succeeded, {failed_count} failed.")
    print(f"========================================")

if __name__ == "__main__":
    main()

