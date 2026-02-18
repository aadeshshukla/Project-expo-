"""
Air Canvas - Main Application
Draw on a canvas using hand gestures tracked via webcam.
Uses MediaPipe for hand tracking and OpenCV for rendering.
"""

import cv2
import numpy as np
import time
from typing import Optional

from config import *
from hand_tracker import HandTracker
from canvas import Canvas
from ui_elements import Toolbar, CameraPreview
from gesture_guide import GestureGuide


class AirCanvas:
    """Main Air Canvas application."""
    
    def __init__(self):
        """Initialize the Air Canvas application."""
        print("Initializing Air Canvas...")
        
        # Initialize camera
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        if not self.camera.isOpened():
            raise RuntimeError("Failed to open camera. Please check camera connection.")
        
        print("Camera initialized successfully")
        
        # Initialize components
        self.hand_tracker = HandTracker()
        self.canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG_COLOR)
        self.toolbar = Toolbar(CANVAS_WIDTH)
        self.camera_preview = CameraPreview(
            CAMERA_PREVIEW_POSITION, 
            CAMERA_PREVIEW_WIDTH, 
            CAMERA_PREVIEW_HEIGHT
        )
        self.gesture_guide = GestureGuide(CANVAS_WIDTH, CANVAS_HEIGHT)
        
        print("All components initialized")
        
        # State variables
        self.running = True
        self.last_gesture = "None"
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Mouse callback for toolbar interaction
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self._mouse_callback)
    
    def _mouse_callback(self, event, x, y, flags, param):
        """
        Handle mouse clicks on toolbar.
        
        Args:
            event: Mouse event type
            x: Mouse x coordinate
            y: Mouse y coordinate
            flags: Event flags
            param: Additional parameters
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicked on a color swatch
            if y < TOOLBAR_HEIGHT:
                color = self.toolbar.get_color_at_position(x, y)
                if color is not None:
                    self.canvas.set_color(color)
                
                # Check if clicked on a button
                button = self.toolbar.get_button_at_position(x, y)
                if button == 'Undo':
                    self.canvas.undo()
                elif button == 'Redo':
                    self.canvas.redo()
                elif button == 'Clear':
                    self.canvas.clear()
    
    def _handle_gesture(self, gesture: str, position: Optional[tuple]):
        """
        Handle recognized gesture.
        
        Args:
            gesture: Gesture name
            position: Hand position (x, y)
        """
        # Only process gesture changes to avoid repeated actions
        gesture_changed = (gesture != self.last_gesture)
        
        if gesture == "Draw" and position:
            # Start or continue drawing
            if not self.canvas.is_drawing:
                self.canvas.start_stroke()
            self.canvas.add_point(position[0], position[1])
        
        elif gesture == "Move":
            # Stop drawing but show cursor position
            if self.canvas.is_drawing:
                self.canvas.end_stroke()
        
        elif gesture == "Pause":
            # Stop drawing
            if self.canvas.is_drawing:
                self.canvas.end_stroke()
        
        elif gesture == "Undo" and gesture_changed:
            # Undo last stroke
            self.canvas.undo()
        
        elif gesture == "Redo" and gesture_changed:
            # Redo last undone stroke
            self.canvas.redo()
        
        elif gesture == "Clear" and gesture_changed:
            # Clear canvas
            self.canvas.clear()
        
        elif gesture == "ChangeColor" and gesture_changed:
            # Cycle to next color
            self.canvas.cycle_color()
        
        else:
            # No recognized gesture - stop drawing
            if self.canvas.is_drawing and gesture != "Draw":
                self.canvas.end_stroke()
        
        self.last_gesture = gesture
    
    def _calculate_fps(self):
        """Calculate and update FPS."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
    
    def run(self):
        """Main application loop."""
        print("Starting Air Canvas application...")
        print("Press 'q' or 'ESC' to quit")
        print("\nGesture Controls:")
        print("  ☝️  Index finger up: Draw")
        print("  ✌️  Index + Middle up: Move (no draw)")
        print("  ✊  Fist: Pause")
        print("  👍  Thumb up: Undo")
        print("  🤙  Pinky up: Redo")
        print("  🖐️  Open palm (5 fingers): Clear canvas")
        print("  🤟  3 fingers up: Change color")
        print("\nYou can also click on the toolbar to change colors or use buttons.")
        print("-" * 60)
        
        while self.running:
            # Read camera frame
            ret, camera_frame = self.camera.read()
            if not ret:
                print("Failed to read from camera")
                break
            
            # Flip frame horizontally for mirror effect
            camera_frame = cv2.flip(camera_frame, 1)
            
            # Process hand tracking
            hand_landmarks, gesture_info = self.hand_tracker.process_frame(camera_frame)
            
            gesture = gesture_info['gesture']
            position = gesture_info['position']
            
            # Handle gesture
            self._handle_gesture(gesture, position)
            
            # Update gesture guide
            self.gesture_guide.update_active_gesture(gesture)
            
            # Get canvas with drawings
            canvas_img = self.canvas.get_canvas()
            
            # Create display frame
            display = canvas_img.copy()
            
            # Draw toolbar
            display = self.toolbar.draw(
                display, 
                self.canvas.current_color,
                self.canvas.current_size
            )
            
            # Draw gesture guide bar
            display = self.gesture_guide.draw(display)
            
            # Draw camera preview
            display = self.camera_preview.draw(
                display, 
                camera_frame,
                hand_landmarks,
                self.hand_tracker
            )
            
            # Draw cursor position indicator when in Move mode
            if gesture == "Move" and position:
                cv2.circle(display, position, 10, HIGHLIGHT_COLOR, 2)
                cv2.circle(display, position, 3, HIGHLIGHT_COLOR, -1)
            
            # Draw FPS and info
            self._calculate_fps()
            info_text = f"FPS: {self.fps:.1f} | Gesture: {gesture} | Color: {self.canvas.get_current_color_name()}"
            cv2.putText(display, info_text, (10, CANVAS_HEIGHT - GESTURE_BAR_HEIGHT - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 1, cv2.LINE_AA)
            
            # Show display
            cv2.imshow(WINDOW_NAME, display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                self.running = False
            elif key == ord('c'):  # Clear canvas
                self.canvas.clear()
            elif key == ord('u'):  # Undo
                self.canvas.undo()
            elif key == ord('r'):  # Redo
                self.canvas.redo()
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up...")
        self.camera.release()
        self.hand_tracker.release()
        cv2.destroyAllWindows()
        print("Air Canvas closed successfully")


def main():
    """Main entry point."""
    try:
        app = AirCanvas()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
