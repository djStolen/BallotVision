import sys
import numpy as np
import cv2

def test_python_version():
    """Verify that we are running the correct Python environment."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 10

def test_opencv_import():
    """Ensure OpenCV and its system dependencies are fully functional."""
    # Create a blank black image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    assert img.shape == (100, 100, 3)
    
    # Test a basic OpenCV function to ensure shared libraries are linked correctly
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    assert gray.shape == (100, 100)

