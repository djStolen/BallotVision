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
        # FIX: Removed ocr_version='PP-OCRv4' to let it use the default v5 engine,
        # which correctly maps and loads the 'rs_latin' model parameters.
        self.ocr = PaddleOCR(
            use_textline_orientation=True, 
            lang=lang, 
            enable_mkldnn=False,
            det_limit_type='max',
            det_limit_side_len=1280
        )

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Runs inference on an image or PDF page-by-page and formats the output.
        Maintains a tiny memory footprint.
        """
        formatted_results = []
        
        # Stream PDFs page-by-page to keep memory usage completely locked down
        if image_path.lower().endswith('.pdf'):
            try:
                import fitz  # PyMuPDF, bundled natively with paddleocr
                doc = fitz.open(image_path)
                
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    # Render the individual page to a low-memory 150 DPI image array
                    pix = page.get_pixmap(dpi=150)
                    
                    # Convert raw pixmap bytes into a NumPy array PaddleOCR can process
                    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    if pix.n == 4:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
                    elif pix.n == 3:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                        
                    # Process only this single page frame image
                    page_results = self.ocr.ocr(img_np)
                    
                    if page_results and isinstance(page_results, list) and page_results[0]:
                        for line in page_results[0]:
                            box, (text, confidence) = line
                            formatted_results.append({
                                "text": text,
                                "confidence": float(confidence),
                                "box": box,
                                "page": page_idx + 1
                            })
                doc.close()
                return formatted_results
                
            except Exception as pdf_error:
                print(f"Warning: PDF streaming failed, trying fallback loader: {pdf_error}")

        # Fallback track for standard flat images (.png, .jpg, etc.)
        results = self.ocr.ocr(image_path)
        if not results:
            return formatted_results
            
        for page_idx, page in enumerate(results):
            if page is None:
                continue
            for line in page:
                box, (text, confidence) = line
                formatted_results.append({
                    "text": text,
                    "confidence": float(confidence),
                    "box": box,
                    "page": page_idx + 1
                })
                
        return formatted_results

