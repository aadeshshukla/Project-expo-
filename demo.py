"""
Air Canvas Demo - Test the application without hand tracking.
This script demonstrates the canvas functionality using keyboard and mouse controls.
"""

import cv2
import numpy as np
from canvas import Canvas
from ui_elements import Toolbar
from gesture_guide import GestureGuide
from config import *

print("=" * 70)
print("AIR CANVAS - DEMO MODE")
print("=" * 70)
print("\nThis demo shows the canvas interface without hand tracking.")
print("\nControls:")
print("  - Click color swatches to change color")
print("  - Click and drag on canvas to draw")
print("  - Press 'C' to clear canvas")
print("  - Press 'U' to undo")
print("  - Press 'R' to redo")
print("  - Press 'Q' or ESC to quit")
print("=" * 70 + "\n")

# Initialize components
canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG_COLOR)
toolbar = Toolbar(CANVAS_WIDTH)
gesture_guide = GestureGuide(CANVAS_WIDTH, CANVAS_HEIGHT)

# Mouse state
is_drawing = False
last_point = None

def mouse_callback(event, x, y, flags, param):
    """Handle mouse events for drawing."""
    global is_drawing, last_point
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if clicked on toolbar
        if y < TOOLBAR_HEIGHT:
            color = toolbar.get_color_at_position(x, y)
            if color is not None:
                canvas.set_color(color)
                return
            
            button = toolbar.get_button_at_position(x, y)
            if button == 'Undo':
                canvas.undo()
            elif button == 'Redo':
                canvas.redo()
            elif button == 'Clear':
                canvas.clear()
            return
        
        # Start drawing
        is_drawing = True
        canvas.start_stroke()
        canvas.add_point(x, y)
        last_point = (x, y)
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if is_drawing:
            canvas.add_point(x, y)
            last_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:
        if is_drawing:
            canvas.end_stroke()
            is_drawing = False
            last_point = None

# Create window
cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

# Main loop
print("Demo running... Draw with your mouse!")

while True:
    # Get canvas
    display = canvas.get_canvas()
    
    # Draw toolbar
    display = toolbar.draw(display, canvas.current_color, canvas.current_size)
    
    # Draw gesture guide
    gesture_guide.update_active_gesture("Demo Mode")
    display = gesture_guide.draw(display)
    
    # Draw instructions
    cv2.putText(display, "DEMO MODE - Use mouse to draw", 
               (10, CANVAS_HEIGHT - GESTURE_BAR_HEIGHT - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 1, cv2.LINE_AA)
    
    # Show display
    cv2.imshow(WINDOW_NAME, display)
    
    # Handle keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # Q or ESC
        break
    elif key == ord('c'):  # Clear
        canvas.clear()
    elif key == ord('u'):  # Undo
        canvas.undo()
    elif key == ord('r'):  # Redo
        canvas.redo()

cv2.destroyAllWindows()
print("\nDemo closed. Thank you!")
