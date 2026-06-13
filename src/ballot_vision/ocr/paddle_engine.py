import os
import cv2
import numpy as np

# Force disabling oneDNN/MKLDNN to prevent framework attribute bugs
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR
from .base import OCREngine
from typing import List, Dict, Any

class PaddleOCREngine(OCREngine):
    def __init__(self, lang: str = 'rs_latin'):
        self.ocr = PaddleOCR(
            use_textline_orientation=True, 
            lang=lang, 
            enable_mkldnn=False,
            det_limit_type='max',
            det_limit_side_len=1280
        )

    def _parse_results(self, paddle_output: Any, page_num: int) -> List[Dict[str, Any]]:
        """
        Recursively scans PaddleOCR's unpredictable output structure to find valid text lines.
        Safely bypasses all 'too many values to unpack' structural errors.
        """
        extracted = []
        if not paddle_output:
            return extracted
            
        def search_tree(item):
            # Signature of a valid line: list/tuple of length >= 2, 
            # where the second element is a tuple/list of (text, confidence)
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                text_block = item[1]
                if isinstance(text_block, (list, tuple)) and len(text_block) >= 2:
                    if isinstance(text_block[0], str) and isinstance(text_block[1], (float, int)):
                        extracted.append({
                            "text": text_block[0],
                            "confidence": float(text_block[1]),
                            "box": item[0],
                            "page": page_num
                        })
                        return # Found the line signature, stop digging deeper
                        
            # Otherwise, if it's a list, keep traversing the tree
            if isinstance(item, list):
                for sub_item in item:
                    search_tree(sub_item)

        search_tree(paddle_output)
        return extracted

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Runs inference safely on images or PDFs page-by-page.
        """
        formatted_results = []
        
        # Stream PDFs page-by-page
        if image_path.lower().endswith('.pdf'):
            try:
                import fitz
                doc = fitz.open(image_path)
                
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    pix = page.get_pixmap(dpi=150)
                    
                    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    if pix.n == 4:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
                    elif pix.n == 3:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                        
                    page_results = self.ocr.ocr(img_np)
                    
                    # FIX: Pass the raw results to our robust recursive parser
                    formatted_results.extend(self._parse_results(page_results, page_idx + 1))
                    
                doc.close()
                return formatted_results
                
            except Exception as pdf_error:
                print(f"Warning: PDF streaming failed, trying fallback loader: {pdf_error}")

        # Fallback track for flat images or if PDF streaming failed
        results = self.ocr.ocr(image_path)
        
        # Since fallback might be multipage, we check if it looks like a list of pages
        is_list_of_pages = False
        if isinstance(results, list) and len(results) > 0 and isinstance(results[0], list):
            first_item = results[0]
            if len(first_item) > 0 and isinstance(first_item[0], list) and not isinstance(first_item[0][0], (str, float)):
                is_list_of_pages = True

        if is_list_of_pages:
            for idx, page_data in enumerate(results):
                formatted_results.extend(self._parse_results(page_data, idx + 1))
        else:
            formatted_results.extend(self._parse_results(results, 1))
            
        return formatted_results

