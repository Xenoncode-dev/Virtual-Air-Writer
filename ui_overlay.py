"""
UI Overlay Module
─────────────────
Draws the color palette, brush pointers, and instructions.
"""

import cv2
import config

class UIOverlay:
    """Draws UI elements for the drawing application."""

    def __init__(self):
        # We need a predictable screen width to draw the palette boxes nicely
        # Assuming 1280 wide like in config. Or we calculate dynamically.
        self.colors_list = list(config.COLORS.items())

    def get_color_from_position(self, x, y, frame_w):
        """
        Check if the hover position is over a color palette box.
        Returns the (B, G, R) color tuple if hovering over one, else None.
        """
        num_colors = len(self.colors_list)
        total_palette_width = num_colors * config.PALETTE_BOX_WIDTH
        start_x = (frame_w - total_palette_width) // 2

        if config.PALETTE_START_Y <= y <= config.PALETTE_START_Y + config.PALETTE_BOX_HEIGHT:
            if start_x <= x <= start_x + total_palette_width:
                # Find which box it is
                box_idx = (x - start_x) // config.PALETTE_BOX_WIDTH
                if 0 <= box_idx < num_colors:
                    name, color_bgr = self.colors_list[box_idx]
                    return color_bgr
        return None

    def draw_palette(self, frame, current_color):
        """Draw the color selection boxes at the top of the screen."""
        h, w, _ = frame.shape
        num_colors = len(self.colors_list)
        total_palette_width = num_colors * config.PALETTE_BOX_WIDTH
        start_x = (w - total_palette_width) // 2
        y1 = config.PALETTE_START_Y
        y2 = y1 + config.PALETTE_BOX_HEIGHT

        # Draw semi-transparent background for palette
        overlay = frame.copy()
        cv2.rectangle(overlay, (start_x - 10, y1 - 5), (start_x + total_palette_width + 10, y2 + 5), (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Draw color boxes
        for i, (name, color_bgr) in enumerate(self.colors_list):
            x1 = start_x + (i * config.PALETTE_BOX_WIDTH)
            x2 = x1 + config.PALETTE_BOX_WIDTH

            # Draw the filled color box
            cv2.rectangle(frame, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), color_bgr, -1)

            # Highlight if it's the currently selected color
            if color_bgr == current_color:
                cv2.rectangle(frame, (x1 + 2, y1 + 2), (x2 - 2, y2 - 2), (255, 255, 255), 3)
            else:
                cv2.rectangle(frame, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), (100, 100, 100), 1)

    def draw_pointer(self, frame, x, y, gesture, current_color):
        """Draw the brush or eraser cursor at the finger tip."""
        if gesture == "DRAW":
            # Draw a solid circle indicating pen down
            cv2.circle(frame, (x, y), config.BRUSH_THICKNESS + 2, current_color, -1)
            cv2.circle(frame, (x, y), config.BRUSH_THICKNESS + 3, (255, 255, 255), 1)
            
        elif gesture == "HOVER":
            # Draw a hollow circle indicating pen up (hovering)
            cv2.circle(frame, (x, y), config.BRUSH_THICKNESS + 4, current_color, 2)
            
        elif gesture == "ERASER":
            # Draw a large circle to represent the eraser area
            cv2.circle(frame, (x, y), config.ERASER_THICKNESS, (200, 200, 200), 2)
            cv2.putText(frame, "ERASING", (x - 30, y - config.ERASER_THICKNESS - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def draw_status(self, frame, gesture):
        """Draw current mode instructions at the bottom."""
        h, w, _ = frame.shape
        
        status_text = {
            "NONE": "Resting",
            "DRAW": "Drawing (Pen Down)",
            "HOVER": "Hovering (Pen Up)",
            "ERASER": "Erasing"
        }.get(gesture, "")

        color = {
            "NONE": (150, 150, 150),
            "DRAW": (0, 255, 0),
            "HOVER": (255, 200, 0),
            "ERASER": (0, 100, 255)
        }.get(gesture, (255, 255, 255))

        cv2.putText(frame, f"Mode: {status_text}", (20, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

        instructions = "Index: Draw | Fist/2 Fingers: Hover | 5 Fingers: Erase | 'C': Clear | 'Q': Quit"
        cv2.putText(frame, instructions, (20, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)
