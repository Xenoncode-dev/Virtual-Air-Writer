"""
Configuration Module
────────────────────
Centralized settings for the Virtual Air Writer application.
Includes camera, drawing, and UI parameters.
"""

# ── Camera & Tracking Settings ──
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280    # High resolution for better drawing
CAMERA_HEIGHT = 720
FPS_DISPLAY = True

MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5

# ── Drawing Settings ──
BRUSH_THICKNESS = 4      # Small brush size as requested
ERASER_THICKNESS = 60    # Larger size for the eraser
SMOOTHING_FACTOR = 3     # Light smoothing to make lines look good

# ── UI & Color Palette (BGR format for OpenCV) ──
COLORS = {
    "BLUE": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "RED": (0, 0, 255),
    "YELLOW": (0, 255, 255),
    "WHITE": (255, 255, 255)
}

# The palette UI boxes at the top of the screen
PALETTE_BOX_WIDTH = 100
PALETTE_BOX_HEIGHT = 60
PALETTE_START_Y = 10     # Y-coordinate for the boxes
