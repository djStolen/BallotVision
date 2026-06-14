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
        Recursively scans PaddleOCR's output structure to find valid text lines.
        Safely handles modern PaddleX dictionaries (singular and plural keys),
        classic nested lists, and NumPy types.
        """
        extracted = []
        if not paddle_output:
            return extracted

        def search_tree(item):
            # 1. MODERN PIPELINE SIGNATURE: PaddleX Dictionary Format
            if isinstance(item, dict):
                # Dynamically hunt for the correct keys, whether PaddleX used singular or plural
                poly_key = next((k for k in ['dt_polys', 'rec_polys', 'dt_boxes', 'rec_boxes'] if k in item), None)
                text_key = next((k for k in ['rec_texts', 'rec_text', 'texts', 'text'] if k in item), None)
                score_key = next((k for k in ['rec_scores', 'rec_score', 'scores', 'score'] if k in item), None)

                # If we found both coordinate boxes and text strings, process them
                if poly_key and text_key:
                    boxes = item[poly_key]
                    texts = item[text_key]
                    scores = item[score_key] if score_key else []

                    for i in range(min(len(boxes), len(texts))):
                        # Safely extract floats
                        try:
                            score = float(scores[i]) if i < len(scores) else 0.0
                        except (ValueError, TypeError):
                            score = 0.0

                        # Convert internal NumPy coordinate arrays to standard Python lists
                        box = boxes[i].tolist() if hasattr(boxes[i], 'tolist') else boxes[i]

                        # Force cast to string (bypasses weird paddlex.utils.fonts.Font objects)
                        text_val = str(texts[i])

                        extracted.append({
                            "text": text_val,
                            "confidence": score,
                            "box": box,
                            "page": page_num
                        })
                    return # Successfully captured the dictionary, stop digging

            # 2. CLASSIC PIPELINE SIGNATURE: Nested Lists
            if isinstance(item, (list, tuple)) and len(item) == 2:
                box = item[0]
                text_and_conf = item[1]

                if isinstance(text_and_conf, (list, tuple)) and len(text_and_conf) == 2:
                    text, conf = text_and_conf[0], text_and_conf[1]
                    if isinstance(text, str):
                        try:
                            conf_float = float(conf)
                            box_list = box.tolist() if hasattr(box, 'tolist') else box
                            extracted.append({
                                "text": text,
                                "confidence": conf_float,
                                "box": box_list,
                                "page": page_num
                            })
                            return
                        except (ValueError, TypeError):
                            pass

            # 3. Traverse lists and tuples
            if isinstance(item, (list, tuple)):
                for sub_item in item:
                    search_tree(sub_item)

            # 4. Traverse dictionaries (in case the payload is nested inside another key)
            if isinstance(item, dict):
                for val in item.values():
                    search_tree(val)

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

                    formatted_results.extend(self._parse_results(page_results, page_idx + 1))

                doc.close()
                return formatted_results

            except Exception as pdf_error:
                print(f"Warning: PDF streaming failed: {pdf_error}")

