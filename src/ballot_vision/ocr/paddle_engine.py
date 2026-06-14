import os
import cv2
import numpy as np
import pprint # for debugging

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
        Recursively scans PaddleOCR's output structure to find valid text lines.
        Safely handles NumPy data types and mixed tuple/list nesting.
        """
        extracted = []
        if not paddle_output:
            return extracted

        def search_tree(item):
            # 1. Check if the current item matches the PaddleOCR line signature
            if isinstance(item, (list, tuple)) and len(item) == 2:
                box = item[0]
                text_and_conf = item[1]

                # Signature: [ [box_coordinates], ("Text string", confidence_score) ]
                if isinstance(text_and_conf, (list, tuple)) and len(text_and_conf) == 2:
                    text, conf = text_and_conf[0], text_and_conf[1]

                    if isinstance(text, str):
                        try:
                            # FIX 1: Force cast numpy.float32/64 to standard Python float
                            conf_float = float(conf)

                            # FIX 2: Ensure the box looks like an array of coordinates (usually 4 points)
                            if isinstance(box, (list, tuple)) and len(box) > 0:
                                extracted.append({
                                    "text": text,
                                    "confidence": conf_float,
                                    "box": box,
                                    "page": page_num
                                })
                                return  # Successfully captured this line, stop digging deeper here
                        except (ValueError, TypeError):
                            pass

            # FIX 3: Traverse BOTH lists and tuples to find nested lines
            if isinstance(item, (list, tuple)):
                for sub_item in item:
                    search_tree(sub_item)

        search_tree(paddle_output)
        return extracted

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        formatted_results = []

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

                    # ==========================================
                    # DEBUG BLOCK: Print the raw output for Page 1
                    # ==========================================
                    if page_idx == 0:
                        print(f"\n{'='*20} DEBUG RAW PADDLEOCR OUTPUT {'='*20}")
                        print(f"File: {image_path}")
                        print(f"Data Type: {type(page_results)}")
                        if page_results is None:
                            print("Result is None! PaddleOCR failed to process the image.")
                        elif isinstance(page_results, list) and not page_results:
                            print("Result is an empty list []. No text detected.")
                        else:
                            # Pretty print the first 2 lines to see the exact structure
                            try:
                                pprint.pprint(page_results[0][:2] if isinstance(page_results[0], list) else page_results, depth=5)
                            except Exception as e:
                                print(f"Raw data (unformatted): {page_results}")
                        print(f"{'='*60}\n")
                    # ==========================================

                    formatted_results.extend(self._parse_results(page_results, page_idx + 1))

                doc.close()
                return formatted_results

            except Exception as pdf_error:
                print(f"Warning: PDF streaming failed: {pdf_error}")

