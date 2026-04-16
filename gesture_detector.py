"""
Gesture Detector Module
───────────────────────
Analyzes hand landmark data to classify the current drawing gesture.
Gestures:
- DRAW: Index finger up, others down
- HOVER: Index and Middle fingers up OR Fist (all fingers closed)
- ERASER: All 5 fingers up
- NONE: Any other state
"""

class Gesture:
    """Enumeration of supported gestures."""
    NONE = "NONE"
    DRAW = "DRAW"
    HOVER = "HOVER"
    ERASER = "ERASER"


class GestureDetector:
    """Detects simple drawing gestures from finger states."""

    def detect(self, landmarks_norm, finger_states):
        """
        Classify the current gesture based on finger states.

        Args:
            landmarks_norm: List of 21 (x, y) normalized landmarks.
            finger_states: List of 5 booleans [thumb, index, middle, ring, pinky].

        Returns:
            gesture: One of Gesture.* constants.
        """
        thumb, index, middle, ring, pinky = finger_states

        # 1. ERASER: All 5 fingers extended widely
        if thumb and index and middle and ring and pinky:
            return Gesture.ERASER
            
        # 2. HOVER / MOVE: Fist (all fingers closed)
        if not thumb and not index and not middle and not ring and not pinky:
            return Gesture.HOVER

        # 3. HOVER / SELECT COLOR: Index and Middle extended
        if index and middle and not ring and not pinky:
            return Gesture.HOVER

        # 4. DRAW: Only Index extended
        if index and not middle and not ring and not pinky:
            return Gesture.DRAW

        return Gesture.NONE
