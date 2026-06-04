from abc import ABC, abstractmethod
from typing import List, Dict, Any

class OCREngine(ABC):
    """Abstract interface for all OCR engines."""
    
    @abstractmethod
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Processes an image and returns a list of detected text 
        with confidence scores and bounding boxes.
        """
        pass

