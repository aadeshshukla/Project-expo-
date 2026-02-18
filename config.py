"""
Configuration constants for Air Canvas application.
Contains colors, sizes, thresholds, and other configuration parameters.
"""

import numpy as np

# Window configuration
WINDOW_NAME = "Air Canvas"
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720

# Camera configuration
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_PREVIEW_WIDTH = 240
CAMERA_PREVIEW_HEIGHT = 180
CAMERA_PREVIEW_POSITION = (CANVAS_WIDTH - CAMERA_PREVIEW_WIDTH - 20, 20)  # Top-right corner

# Color palette (BGR format for OpenCV)
COLORS = {
    'Red': (0, 0, 255),
    'Green': (0, 255, 0),
    'Blue': (255, 0, 0),
    'Yellow': (0, 255, 255),
    'Orange': (0, 165, 255),
    'Purple': (255, 0, 255),
    'White': (255, 255, 255),
    'Eraser': (40, 40, 40)  # Dark gray (matches canvas background)
}

# UI Colors
CANVAS_BG_COLOR = (40, 40, 40)  # Dark gray background
TOOLBAR_BG_COLOR = (60, 60, 60)
GESTURE_BAR_BG_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 255)  # Cyan for highlights
ACTIVE_GESTURE_COLOR = (0, 200, 0)  # Green for active gesture

# Brush sizes
BRUSH_SIZES = {
    'small': 3,
    'medium': 6,
    'large': 10
}
DEFAULT_BRUSH_SIZE = 'medium'

# Toolbar configuration
TOOLBAR_HEIGHT = 80
TOOLBAR_PADDING = 10
COLOR_SWATCH_RADIUS = 25
BUTTON_WIDTH = 60
BUTTON_HEIGHT = 60

# Gesture guide bar configuration
GESTURE_BAR_HEIGHT = 100
GESTURE_BAR_PADDING = 15

# Hand tracking configuration
MEDIAPIPE_DETECTION_CONFIDENCE = 0.7
MEDIAPIPE_TRACKING_CONFIDENCE = 0.7
MAX_NUM_HANDS = 1

# Gesture detection thresholds
FINGER_TIP_THRESHOLD = 0.1  # Distance threshold for finger being "up"
GESTURE_SMOOTHING_FRAMES = 3  # Number of frames to smooth gesture detection
MIN_GESTURE_CONFIDENCE = 0.6

# Drawing configuration
DRAWING_SMOOTHING = True
LINE_THICKNESS_MULTIPLIER = 2
ANTI_ALIAS = True

# Performance configuration
TARGET_FPS = 30
FRAME_SKIP = 0  # Number of frames to skip for processing (0 = no skip)

# Undo/Redo configuration
MAX_UNDO_STACK_SIZE = 50

# Gesture cooldown (in frames) to prevent rapid toggling
GESTURE_COOLDOWN = 10
