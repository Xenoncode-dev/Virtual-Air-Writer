"""
Download the MediaPipe Hand Landmarker model.
This script is optional — the model is auto-downloaded on first run.
Run this manually only if you want to pre-download the model.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hand_tracker import _ensure_model

if __name__ == "__main__":
    path = _ensure_model()
    print(f"\nModel ready at: {path}")
    print(f"Size: {os.path.getsize(path) / (1024*1024):.1f} MB")
