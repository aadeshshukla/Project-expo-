"""
UI elements for Air Canvas.
Includes toolbar, color palette, camera preview, and control buttons.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict
from config import *
from utils import draw_rounded_rectangle, draw_text_with_background


class Toolbar:
    """Toolbar for color selection, brush size, and control buttons."""
    
    def __init__(self, canvas_width: int):
        """
        Initialize the toolbar.
        
        Args:
            canvas_width: Width of the canvas
        """
        self.canvas_width = canvas_width
        self.height = TOOLBAR_HEIGHT
        
        # Calculate color swatch positions
        self.color_swatches = {}
        start_x = TOOLBAR_PADDING + COLOR_SWATCH_RADIUS
        spacing = (canvas_width - 2 * TOOLBAR_PADDING - BUTTON_SECTION_WIDTH) // len(COLORS)
        
        for i, (name, color) in enumerate(COLORS.items()):
            x = start_x + i * spacing
            y = TOOLBAR_HEIGHT // 2
            self.color_swatches[name] = {
                'position': (x, y),
                'color': color,
                'radius': COLOR_SWATCH_RADIUS
            }
        
        # Button positions (right side of toolbar)
        button_start_x = canvas_width - TOOLBAR_PADDING - 3 * (BUTTON_WIDTH + 10)
        self.buttons = {
            'Undo': (button_start_x, TOOLBAR_PADDING + 10),
            'Redo': (button_start_x + BUTTON_WIDTH + 10, TOOLBAR_PADDING + 10),
            'Clear': (button_start_x + 2 * (BUTTON_WIDTH + 10), TOOLBAR_PADDING + 10)
        }
    
    def draw(self, frame: np.ndarray, current_color: Tuple[int, int, int],
             current_size: int) -> np.ndarray:
        """
        Draw the toolbar on the frame.
        
        Args:
            frame: Frame to draw on
            current_color: Currently selected color
            current_size: Currently selected brush size
        
        Returns:
            Frame with toolbar drawn
        """
        # Draw toolbar background
        toolbar_overlay = frame.copy()
        cv2.rectangle(toolbar_overlay, (0, 0), (self.canvas_width, self.height),
                     TOOLBAR_BG_COLOR, -1)
        cv2.addWeighted(toolbar_overlay, 0.9, frame, 0.1, 0, frame)
        
        # Draw color swatches
        for name, swatch in self.color_swatches.items():
            pos = swatch['position']
            color = swatch['color']
            radius = swatch['radius']
            
            # Draw color circle
            cv2.circle(frame, pos, radius, color, -1)
            cv2.circle(frame, pos, radius, (200, 200, 200), 2, cv2.LINE_AA)
            
            # Highlight selected color
            if color == current_color:
                cv2.circle(frame, pos, radius + 5, HIGHLIGHT_COLOR, 3, cv2.LINE_AA)
            
            # Draw color name below
            (text_width, _), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.putText(frame, name, 
                       (pos[0] - text_width // 2, pos[1] + radius + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_COLOR, 1, cv2.LINE_AA)
        
        # Draw control buttons
        for button_name, pos in self.buttons.items():
            x, y = pos
            
            # Draw button background
            draw_rounded_rectangle(
                frame,
                (x, y),
                (x + BUTTON_WIDTH, y + BUTTON_HEIGHT - 20),
                (80, 80, 80),
                -1,
                radius=8
            )
            
            # Draw button border
            draw_rounded_rectangle(
                frame,
                (x, y),
                (x + BUTTON_WIDTH, y + BUTTON_HEIGHT - 20),
                (150, 150, 150),
                2,
                radius=8
            )
            
            # Draw button text
            (text_width, text_height), _ = cv2.getTextSize(
                button_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            text_x = x + (BUTTON_WIDTH - text_width) // 2
            text_y = y + (BUTTON_HEIGHT - 20 + text_height) // 2
            cv2.putText(frame, button_name, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1, cv2.LINE_AA)
        
        return frame
    
    def get_color_at_position(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Get the color of the swatch at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Color if position is on a swatch, None otherwise
        """
        for name, swatch in self.color_swatches.items():
            pos = swatch['position']
            radius = swatch['radius']
            distance = np.sqrt((x - pos[0])**2 + (y - pos[1])**2)
            if distance <= radius:
                return swatch['color']
        return None
    
    def get_button_at_position(self, x: int, y: int) -> Optional[str]:
        """
        Get the button at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Button name if position is on a button, None otherwise
        """
        for button_name, pos in self.buttons.items():
            bx, by = pos
            if bx <= x <= bx + BUTTON_WIDTH and by <= y <= by + BUTTON_HEIGHT - 20:
                return button_name
        return None


class CameraPreview:
    """Camera preview window showing hand tracking."""
    
    def __init__(self, position: Tuple[int, int], width: int, height: int):
        """
        Initialize camera preview.
        
        Args:
            position: Top-left position (x, y)
            width: Preview width
            height: Preview height
        """
        self.position = position
        self.width = width
        self.height = height
    
    def draw(self, frame: np.ndarray, camera_frame: np.ndarray,
             hand_landmarks=None, hand_tracker=None) -> np.ndarray:
        """
        Draw the camera preview on the frame.
        
        Args:
            frame: Main canvas frame
            camera_frame: Camera feed frame
            hand_landmarks: Hand landmarks from MediaPipe
            hand_tracker: HandTracker instance for drawing landmarks
        
        Returns:
            Frame with camera preview drawn
        """
        # Resize camera frame to preview size
        preview = cv2.resize(camera_frame, (self.width, self.height))
        
        # Draw hand landmarks on preview
        if hand_landmarks and hand_tracker:
            preview = hand_tracker.draw_landmarks(preview, hand_landmarks)
        
        # Draw border around preview
        cv2.rectangle(preview, (0, 0), (self.width - 1, self.height - 1),
                     HIGHLIGHT_COLOR, 3)
        
        # Overlay preview on main frame
        x, y = self.position
        frame[y:y+self.height, x:x+self.width] = preview
        
        return frame
