"""
Hand Tracker Module
───────────────────
Wraps MediaPipe HandLandmarker (Task API) to provide cleaned-up
landmark data and finger-state utilities.

Compatible with mediapipe >= 0.10.18 (Task-based API).
Uses VIDEO running mode for synchronous, low-latency results.
"""

import os
import sys
import time
import urllib.request

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
    RunningMode,
)

import config

# ── Model download URL ──
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)


def _ensure_model() -> str:
    """
    Ensure the hand_landmarker.task model file is available.
    Downloads it to a cache directory if not already present.

    Returns:
        Absolute path to the .task model file.
    """
    # Try local directory first
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task"
    )
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path

    # Fall back to a cache directory in user's home
    cache_dir = os.path.join(os.path.expanduser("~"), ".mediapipe_cache")
    os.makedirs(cache_dir, exist_ok=True)
    cached_path = os.path.join(cache_dir, "hand_landmarker.task")

    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
        print(f"Using cached model: {cached_path}")
        return cached_path

    # Download
    print(f"Downloading hand_landmarker.task model (~10 MB)...")
    print(f"  From: {_MODEL_URL}")
    print(f"  To:   {cached_path}")

    try:
        urllib.request.urlretrieve(_MODEL_URL, cached_path)
        size_mb = os.path.getsize(cached_path) / (1024 * 1024)
        print(f"  Download complete! ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"ERROR: Failed to download model: {e}")
        print("Please download manually from:")
        print(f"  {_MODEL_URL}")
        print(f"And place it at: {cached_path}")
        sys.exit(1)

    return cached_path


class HandTracker:
    """Detects and tracks a single hand using MediaPipe HandLandmarker (Task API)."""

    # MediaPipe landmark indices for fingertip and PIP joints
    FINGER_TIPS = [8, 12, 16, 20]    # Index, Middle, Ring, Pinky tips
    FINGER_PIPS = [6, 10, 14, 18]    # Corresponding PIP joints
    THUMB_TIP = 4
    THUMB_IP = 3
    THUMB_MCP = 2

    def __init__(self):
        model_path = _ensure_model()

        # Timestamp counter for VIDEO mode (must be strictly increasing)
        self._frame_timestamp_ms = 0

        # ── Use VIDEO mode: synchronous, returns results immediately ──
        # This gives us zero-latency results unlike LIVE_STREAM
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )

        self.landmarker = HandLandmarker.create_from_options(options)
        print("HandLandmarker initialized successfully (VIDEO mode).")

    def process(self, frame):
        """
        Process a BGR frame and detect hands synchronously.

        Args:
            frame: BGR image from OpenCV.

        Returns:
            result: HandLandmarkerResult with detected hand data.
        """
        # Convert BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Wrap in MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Use actual timestamp for accurate tracking
        self._frame_timestamp_ms = int(time.time() * 1000)

        # Synchronous detection — returns result immediately
        result = self.landmarker.detect_for_video(mp_image, self._frame_timestamp_ms)

        return result

    def get_landmarks(self, result, frame_shape):
        """
        Extract normalized and pixel landmark positions from results.

        Args:
            result: HandLandmarkerResult from self.process().
            frame_shape: (height, width, channels) of the original frame.

        Returns:
            landmarks_norm: List of (x, y) in normalized [0,1] coords, or None.
            landmarks_px: List of (x, y) in pixel coords, or None.
        """
        if result is None or not result.hand_landmarks:
            return None, None

        hand = result.hand_landmarks[0]  # Single hand only
        h, w, _ = frame_shape

        landmarks_norm = [(lm.x, lm.y) for lm in hand]
        landmarks_px = [(int(lm.x * w), int(lm.y * h)) for lm in hand]

        return landmarks_norm, landmarks_px

    def finger_states(self, landmarks_norm):
        """
        Determine which fingers are up using robust checks.

        Returns:
            list of 5 booleans: [thumb, index, middle, ring, pinky]
        """
        states = []

        # ── Thumb detection (more robust) ──
        # Use the angle between thumb MCP → IP → TIP
        # A simpler heuristic: thumb tip is further from palm center than IP
        thumb_tip = landmarks_norm[self.THUMB_TIP]
        thumb_ip = landmarks_norm[self.THUMB_IP]
        thumb_mcp = landmarks_norm[self.THUMB_MCP]
        wrist = landmarks_norm[0]

        # Thumb: tip x is further from wrist than IP x (works for both hands after mirror)
        thumb_tip_dist = abs(thumb_tip[0] - wrist[0])
        thumb_ip_dist = abs(thumb_ip[0] - wrist[0])
        thumb_up = thumb_tip_dist > thumb_ip_dist
        states.append(thumb_up)

        # ── Other fingers: tip y < PIP y means the finger is raised ──
        for tip, pip in zip(self.FINGER_TIPS, self.FINGER_PIPS):
            states.append(landmarks_norm[tip][1] < landmarks_norm[pip][1])

        return states

    def draw_landmarks(self, frame, result):
        """Draw hand landmarks and connections on the frame."""
        if not config.SHOW_LANDMARKS:
            return
        if result is None or not result.hand_landmarks:
            return

        hand = result.hand_landmarks[0]
        h, w, _ = frame.shape

        # MediaPipe hand connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),       # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),       # Index
            (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
            (0, 13), (13, 14), (14, 15), (15, 16), # Ring
            (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (5, 9), (9, 13), (13, 17),              # Palm
        ]

        # Convert landmarks to pixel coordinates
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand]

        # Draw connections with gradient coloring
        for start, end in connections:
            if start < len(points) and end < len(points):
                cv2.line(frame, points[start], points[end], (0, 220, 0), 2,
                         cv2.LINE_AA)

        # Draw landmark points
        for i, pt in enumerate(points):
            if i in [4, 8, 12, 16, 20]:  # Fingertips
                cv2.circle(frame, pt, 7, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, pt, 7, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(frame, pt, 4, (0, 200, 0), -1, cv2.LINE_AA)

    def release(self):
        """Release MediaPipe resources."""
        self.landmarker.close()
