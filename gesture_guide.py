"""
Gesture guide bar rendering for Air Canvas.
Displays available gestures and highlights the active one.
"""

import cv2
import numpy as np
from typing import Tuple
from config import *
from utils import draw_rounded_rectangle, draw_text_with_background


class GestureGuide:
    """Gesture guide bar showing available gestures and active one."""
    
    # Gesture definitions with emoji and description
    GESTURES = [
        ("Draw", "☝️", "Draw"),
        ("Move", "✌️", "Move"),
        ("Pause", "✊", "Pause"),
        ("Undo", "👍", "Undo"),
        ("Redo", "🤙", "Redo"),
        ("Clear", "🖐️", "Clear"),
        ("ChangeColor", "🤟", "Color"),
    ]
    
    def __init__(self, canvas_width: int, canvas_height: int):
        """
        Initialize the gesture guide.
        
        Args:
            canvas_width: Width of the canvas
            canvas_height: Height of the canvas
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.bar_y = canvas_height - GESTURE_BAR_HEIGHT
        self.active_gesture = "None"
    
    def update_active_gesture(self, gesture: str):
        """
        Update the currently active gesture.
        
        Args:
            gesture: Gesture name
        """
        self.active_gesture = gesture
    
    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw the gesture guide bar on the frame.
        
        Args:
            frame: Frame to draw on
        
        Returns:
            Frame with gesture guide drawn
        """
        # Draw background bar
        bar_overlay = frame.copy()
        cv2.rectangle(bar_overlay, 
                     (0, self.bar_y), 
                     (self.canvas_width, self.canvas_height),
                     GESTURE_BAR_BG_COLOR, -1)
        cv2.addWeighted(bar_overlay, 0.8, frame, 0.2, 0, frame)
        
        # Calculate spacing for gestures
        num_gestures = len(self.GESTURES)
        gesture_width = (self.canvas_width - 2 * GESTURE_BAR_PADDING) // num_gestures
        
        # Draw each gesture
        for i, (gesture_name, emoji, label) in enumerate(self.GESTURES):
            x_center = GESTURE_BAR_PADDING + i * gesture_width + gesture_width // 2
            y_center = self.bar_y + GESTURE_BAR_HEIGHT // 2
            
            # Highlight active gesture
            is_active = (gesture_name == self.active_gesture)
            
            if is_active:
                # Draw highlight rectangle
                rect_margin = 10
                draw_rounded_rectangle(
                    frame,
                    (x_center - gesture_width // 2 + rect_margin, self.bar_y + rect_margin),
                    (x_center + gesture_width // 2 - rect_margin, self.canvas_height - rect_margin),
                    ACTIVE_GESTURE_COLOR,
                    2,
                    radius=8
                )
            
            # Draw emoji/icon (using text as fallback since emojis may not render well)
            icon_color = ACTIVE_GESTURE_COLOR if is_active else TEXT_COLOR
            cv2.putText(frame, emoji, 
                       (x_center - 15, y_center - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, icon_color, 2, cv2.LINE_AA)
            
            # Draw label
            label_color = ACTIVE_GESTURE_COLOR if is_active else TEXT_COLOR
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.putText(frame, label,
                       (x_center - text_width // 2, y_center + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 1, cv2.LINE_AA)
        
        return frame
