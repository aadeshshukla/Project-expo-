"""
Canvas drawing logic for Air Canvas.
Handles drawing strokes, colors, brush sizes, and undo/redo functionality.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from config import *


class Stroke:
    """Represents a single drawing stroke."""
    
    def __init__(self, color: Tuple[int, int, int], size: int):
        """
        Initialize a stroke.
        
        Args:
            color: BGR color
            size: Brush size
        """
        self.points: List[Tuple[int, int]] = []
        self.color = color
        self.size = size
    
    def add_point(self, x: int, y: int):
        """Add a point to the stroke."""
        self.points.append((x, y))
    
    def draw(self, canvas: np.ndarray):
        """
        Draw the stroke on the canvas.
        
        Args:
            canvas: Canvas to draw on
        """
        if len(self.points) < 2:
            # Draw a single point
            if len(self.points) == 1:
                cv2.circle(canvas, self.points[0], self.size, self.color, -1)
            return
        
        # Draw lines between consecutive points
        for i in range(1, len(self.points)):
            if ANTI_ALIAS:
                cv2.line(canvas, self.points[i-1], self.points[i], 
                        self.color, self.size * LINE_THICKNESS_MULTIPLIER, cv2.LINE_AA)
            else:
                cv2.line(canvas, self.points[i-1], self.points[i], 
                        self.color, self.size * LINE_THICKNESS_MULTIPLIER)


class Canvas:
    """Canvas for drawing with support for colors, sizes, undo/redo."""
    
    def __init__(self, width: int, height: int, bg_color: Tuple[int, int, int]):
        """
        Initialize the canvas.
        
        Args:
            width: Canvas width
            height: Canvas height
            bg_color: Background color in BGR format
        """
        self.width = width
        self.height = height
        self.bg_color = bg_color
        
        self.canvas = np.full((height, width, 3), bg_color, dtype=np.uint8)
        
        self.strokes: List[Stroke] = []
        self.undo_stack: List[Stroke] = []
        
        self.current_stroke: Optional[Stroke] = None
        self.current_color = COLORS['White']
        self.current_size = BRUSH_SIZES[DEFAULT_BRUSH_SIZE]
        self.is_drawing = False
    
    def start_stroke(self):
        """Start a new stroke."""
        if not self.is_drawing:
            self.current_stroke = Stroke(self.current_color, self.current_size)
            self.is_drawing = True
    
    def add_point(self, x: int, y: int):
        """
        Add a point to the current stroke.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        if self.is_drawing and self.current_stroke:
            # Clamp coordinates to canvas bounds
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            self.current_stroke.add_point(x, y)
    
    def end_stroke(self):
        """End the current stroke and add it to history."""
        if self.is_drawing and self.current_stroke:
            if len(self.current_stroke.points) > 0:
                self.strokes.append(self.current_stroke)
                # Clear redo stack when new stroke is added
                self.undo_stack.clear()
                
                # Limit stroke history
                if len(self.strokes) > MAX_UNDO_STACK_SIZE:
                    self.strokes.pop(0)
            
            self.current_stroke = None
            self.is_drawing = False
    
    def undo(self):
        """Undo the last stroke."""
        if self.strokes:
            stroke = self.strokes.pop()
            self.undo_stack.append(stroke)
            self._redraw()
    
    def redo(self):
        """Redo the last undone stroke."""
        if self.undo_stack:
            stroke = self.undo_stack.pop()
            self.strokes.append(stroke)
            self._redraw()
    
    def clear(self):
        """Clear the entire canvas."""
        self.strokes.clear()
        self.undo_stack.clear()
        self.current_stroke = None
        self.is_drawing = False
        self._redraw()
    
    def set_color(self, color: Tuple[int, int, int]):
        """
        Set the current drawing color.
        
        Args:
            color: BGR color
        """
        self.current_color = color
    
    def set_size(self, size: int):
        """
        Set the current brush size.
        
        Args:
            size: Brush size
        """
        self.current_size = size
    
    def cycle_color(self):
        """Cycle to the next color in the palette."""
        color_list = list(COLORS.values())
        try:
            current_index = color_list.index(self.current_color)
            next_index = (current_index + 1) % len(color_list)
            self.current_color = color_list[next_index]
        except ValueError:
            self.current_color = color_list[0]
    
    def get_canvas(self) -> np.ndarray:
        """
        Get the current canvas with all strokes drawn.
        
        Returns:
            Canvas image
        """
        # Draw current stroke if in progress
        if self.is_drawing and self.current_stroke and len(self.current_stroke.points) > 0:
            temp_canvas = self.canvas.copy()
            self.current_stroke.draw(temp_canvas)
            return temp_canvas
        
        return self.canvas
    
    def _redraw(self):
        """Redraw the entire canvas from scratch."""
        # Clear canvas
        self.canvas = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
        
        # Redraw all strokes
        for stroke in self.strokes:
            stroke.draw(self.canvas)
    
    def get_current_color_name(self) -> str:
        """
        Get the name of the current color.
        
        Returns:
            Color name
        """
        for name, color in COLORS.items():
            if color == self.current_color:
                return name
        return "Unknown"
