import pytest
from ballot_vision.ocr.paddle_engine import PaddleOCREngine
import os

# Skip this test if you are in a CI environment without graphical dependencies
@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skipping OCR inference in CI")
def test_paddle_engine_initialization():
    engine = PaddleOCREngine()
    assert engine is not None
    # We aren't testing OCR accuracy yet, just that the wrapper works

