"""
Utility functions for Air Canvas application.
Contains helper functions for calculations, drawing, and UI operations.
"""

import numpy as np
import cv2
from typing import Tuple, List


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
    
    Returns:
        Distance between the points
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def smooth_points(points: List[Tuple[int, int]], window_size: int = 3) -> List[Tuple[int, int]]:
    """
    Apply moving average smoothing to a list of points.
    
    Args:
        points: List of (x, y) coordinates
        window_size: Size of the smoothing window
    
    Returns:
        Smoothed list of points
    """
    if len(points) < window_size:
        return points
    
    smoothed = []
    for i in range(len(points)):
        start = max(0, i - window_size // 2)
        end = min(len(points), i + window_size // 2 + 1)
        window = points[start:end]
        
        avg_x = sum(p[0] for p in window) / len(window)
        avg_y = sum(p[1] for p in window) / len(window)
        smoothed.append((int(avg_x), int(avg_y)))
    
    return smoothed


def draw_rounded_rectangle(img: np.ndarray, top_left: Tuple[int, int], 
                           bottom_right: Tuple[int, int], color: Tuple[int, int, int],
                           thickness: int = -1, radius: int = 10) -> None:
    """
    Draw a rounded rectangle on an image.
    
    Args:
        img: Image array to draw on
        top_left: Top-left corner (x, y)
        bottom_right: Bottom-right corner (x, y)
        color: Color in BGR format
        thickness: Line thickness (-1 for filled)
        radius: Corner radius
    """
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Draw rectangles for the main body
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
    
    # Draw circles for rounded corners
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)


def draw_text_with_background(img: np.ndarray, text: str, position: Tuple[int, int],
                               font_scale: float = 0.6, color: Tuple[int, int, int] = (255, 255, 255),
                               bg_color: Tuple[int, int, int] = (0, 0, 0),
                               padding: int = 5) -> None:
    """
    Draw text with a background rectangle.
    
    Args:
        img: Image array to draw on
        text: Text to draw
        position: Bottom-left position of text (x, y)
        font_scale: Font scale
        color: Text color in BGR format
        bg_color: Background color in BGR format
        padding: Padding around text
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw background rectangle
    x, y = position
    cv2.rectangle(img, 
                  (x - padding, y - text_height - padding),
                  (x + text_width + padding, y + baseline + padding),
                  bg_color, -1)
    
    # Draw text
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)


def is_point_in_rect(point: Tuple[int, int], rect_top_left: Tuple[int, int],
                     rect_bottom_right: Tuple[int, int]) -> bool:
    """
    Check if a point is inside a rectangle.
    
    Args:
        point: Point (x, y)
        rect_top_left: Top-left corner of rectangle
        rect_bottom_right: Bottom-right corner of rectangle
    
    Returns:
        True if point is inside rectangle
    """
    x, y = point
    x1, y1 = rect_top_left
    x2, y2 = rect_bottom_right
    return x1 <= x <= x2 and y1 <= y <= y2


def normalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[int, int]:
    """
    Convert normalized coordinates (0-1) to pixel coordinates.
    
    Args:
        x: Normalized x coordinate (0-1)
        y: Normalized y coordinate (0-1)
        width: Image width
        height: Image height
    
    Returns:
        Pixel coordinates (x, y)
    """
    return int(x * width), int(y * height)


def overlay_transparent(background: np.ndarray, overlay: np.ndarray, 
                        position: Tuple[int, int], alpha: float = 0.7) -> np.ndarray:
    """
    Overlay an image on top of another with transparency.
    
    Args:
        background: Background image
        overlay: Overlay image
        position: Position to place overlay (x, y)
        alpha: Transparency factor (0-1)
    
    Returns:
        Combined image
    """
    x, y = position
    h, w = overlay.shape[:2]
    
    # Ensure the overlay fits within the background
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        overlay = overlay[:, :w]
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        overlay = overlay[:h, :]
    
    # Blend the overlay
    roi = background[y:y+h, x:x+w]
    blended = cv2.addWeighted(roi, 1 - alpha, overlay, alpha, 0)
    background[y:y+h, x:x+w] = blended
    
    return background
