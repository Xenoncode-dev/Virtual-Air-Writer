"""
Virtual Air Writer
──────────────────
Use hand gestures to draw in the air. The drawing is rendered
over the webcam feed, like drawing on glass.
"""

import sys
import cv2
import numpy as np
import config
from hand_tracker import HandTracker
from gesture_detector import GestureDetector, Gesture
from ui_overlay import UIOverlay

def main():
    print("============================================================")
    print("  Virtual Air Writer")
    print("============================================================")
    print("Starting up... Press 'q' to quit.")

    # ── Initialize Camera ──
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: Could not open camera {config.CAMERA_INDEX}.")
        sys.exit(1)

    # Note: OpenCV sets resolution as close to requested as possible.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    
    # Read first frame to get actual dimensions
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        sys.exit(1)
    
    h, w, _ = frame.shape
    print(f"Camera initialized: {w}x{h}")

    # ── Initialize Modules ──
    tracker = HandTracker()
    detector = GestureDetector()
    ui = UIOverlay()

    # ── Fullscreen Window Setup ──
    window_name = "Virtual Air Writer"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # ── Drawing State ──
    # The canvas where all lines are drawn
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    
    # State tracking
    current_color = config.COLORS["GREEN"]
    prev_x, prev_y = 0, 0
    smoother_active = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror the frame horizontally so it acts like a mirror
        # This is essential for drawing comfortably in the air
        frame = cv2.flip(frame, 1)

        # ── Process Hand Landmarks ──
        result = tracker.process(frame)
        landmarks_norm, landmarks_px = tracker.get_landmarks(result, frame.shape)
        gesture = Gesture.NONE

        if landmarks_norm is not None:
            # Determine finger states
            finger_states = tracker.finger_states(landmarks_norm)
            
            # Detect gesture
            gesture = detector.detect(landmarks_norm, finger_states)

            # Get index finger position (the "pen tip")
            cx, cy = landmarks_px[8]

            # ── Handle Palette Color Selection ──
            if gesture == Gesture.HOVER:
                color_picked = ui.get_color_from_position(cx, cy, w)
                if color_picked is not None:
                    current_color = color_picked

            # ── Drawing Logic ──
            if gesture == Gesture.DRAW:
                if not smoother_active:
                    # Just started drawing — set prev to current so it doesn't draw a huge line from nowhere
                    prev_x, prev_y = cx, cy
                    smoother_active = True
                else:
                    # Draw directly to the current point to remove all delay/lag
                    cv2.line(canvas, (prev_x, prev_y), (cx, cy), 
                             current_color, config.BRUSH_THICKNESS, cv2.LINE_AA)
                    
                    prev_x, prev_y = cx, cy

            elif gesture == Gesture.ERASER:
                # Eraser: Draw a thick black circle (or line) on the canvas to erase
                cv2.circle(canvas, (cx, cy), config.ERASER_THICKNESS, (0, 0, 0), -1)
                smoother_active = False # Stop line continuity

            else:
                # Hover or None — break the line continuity
                smoother_active = False

        else:
            # Hand lost — break the line continuity
            smoother_active = False

        # ── Combine Camera and Canvas ──
        # Where the canvas is black, show the camera frame.
        # Where the canvas has drawing, show the drawing.
        
        # Method: convert canvas to grayscale, find where it's > 0 (drawing exists)
        canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        # Background: camera frame where canvas is black
        bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        
        # Foreground: canvas where drawing exists
        fg = cv2.bitwise_and(canvas, canvas, mask=mask)
        
        # Combine
        combined_frame = cv2.add(bg, fg)

        # ── Draw UI on top ──
        ui.draw_palette(combined_frame, current_color)
        if landmarks_norm is not None:
            ui.draw_pointer(combined_frame, cx, cy, gesture, current_color)
        ui.draw_status(combined_frame, gesture)

        # ── Show Frame ──
        cv2.imshow(window_name, combined_frame)

        # ── Keyboard Controls ──
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Manual clear
            canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    main()
