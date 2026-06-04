from paddleocr import PaddleOCR
from .base import OCREngine
from typing import List, Dict, Any

class PaddleOCREngine(OCREngine):
    def __init__(self, lang: str = 'rs_latin'):
        # Updated parameter to match newer PaddleOCR versions
        self.ocr = PaddleOCR(use_textline_orientation=True, lang=lang)

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Runs inference and formats the output into a standardized list.
        """
        results = self.ocr.ocr(image_path, cls=True)
        
        # Flatten and format the raw result from PaddleOCR
        formatted_results = []
        for line in results[0]:
            box, (text, confidence) = line
            formatted_results.append({
                "text": text,
                "confidence": confidence,
                "box": box
            })
            
        return formatted_results

