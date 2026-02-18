"""
Hand tracking and gesture recognition using MediaPipe.
Detects hand landmarks and recognizes various gestures for controlling the Air Canvas.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List, Dict
from config import *


class HandTracker:
    """Hand tracking and gesture recognition using MediaPipe Hands."""
    
    # Finger landmark indices
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    
    THUMB_IP = 3
    INDEX_PIP = 6
    MIDDLE_PIP = 10
    RING_PIP = 14
    PINKY_PIP = 18
    
    WRIST = 0
    
    def __init__(self):
        """Initialize MediaPipe Hands and gesture tracking."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MEDIAPIPE_DETECTION_CONFIDENCE,
            min_tracking_confidence=MEDIAPIPE_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.current_gesture = "None"
        self.gesture_history = []
        self.gesture_cooldown_counter = 0
        
    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Dict]:
        """
        Process a frame to detect hands and recognize gestures.
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            Tuple of (landmarks as list of normalized coordinates, gesture info dict)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_info = {
            'gesture': 'None',
            'position': None,
            'hand_landmarks': None,
            'confidence': 0.0
        }
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # Only use first hand
            
            # Extract landmark positions
            landmarks = []
            h, w, _ = frame.shape
            for landmark in hand_landmarks.landmark:
                landmarks.append((landmark.x, landmark.y, landmark.z))
            
            # Recognize gesture
            gesture = self._recognize_gesture(landmarks)
            
            # Update gesture with smoothing and cooldown
            if self.gesture_cooldown_counter > 0:
                self.gesture_cooldown_counter -= 1
                gesture = self.current_gesture
            else:
                self.gesture_history.append(gesture)
                if len(self.gesture_history) > GESTURE_SMOOTHING_FRAMES:
                    self.gesture_history.pop(0)
                
                # Use most common gesture in history
                if len(self.gesture_history) >= GESTURE_SMOOTHING_FRAMES:
                    gesture = max(set(self.gesture_history), key=self.gesture_history.count)
                
                # Update current gesture
                if gesture != self.current_gesture:
                    self.current_gesture = gesture
                    self.gesture_cooldown_counter = GESTURE_COOLDOWN
            
            # Get index finger tip position for drawing
            index_tip = hand_landmarks.landmark[self.INDEX_TIP]
            position = (int(index_tip.x * CANVAS_WIDTH), int(index_tip.y * CANVAS_HEIGHT))
            
            gesture_info = {
                'gesture': self.current_gesture,
                'position': position,
                'hand_landmarks': hand_landmarks,
                'confidence': 0.8  # Simplified confidence
            }
        
        return results.multi_hand_landmarks, gesture_info
    
    def _recognize_gesture(self, landmarks: List[Tuple[float, float, float]]) -> str:
        """
        Recognize gesture from hand landmarks.
        
        Args:
            landmarks: List of (x, y, z) coordinates for each landmark
        
        Returns:
            Gesture name
        """
        fingers_up = self._count_fingers_up(landmarks)
        
        # Check specific gestures
        if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up
            return "Draw"
        
        elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle fingers up
            return "Move"
        
        elif fingers_up == [0, 1, 1, 1, 0]:  # Index, middle, and ring fingers up
            return "ChangeColor"
        
        elif fingers_up == [1, 0, 0, 0, 0]:  # Only thumb up
            return "Undo"
        
        elif fingers_up == [0, 0, 0, 0, 1]:  # Only pinky up
            return "Redo"
        
        elif sum(fingers_up) == 5:  # All fingers up (open palm)
            return "Clear"
        
        elif sum(fingers_up) == 0:  # Fist (no fingers up)
            return "Pause"
        
        return "None"
    
    def _count_fingers_up(self, landmarks: List[Tuple[float, float, float]]) -> List[int]:
        """
        Determine which fingers are up.
        
        Args:
            landmarks: List of landmark coordinates
        
        Returns:
            List of 5 integers (1 if finger is up, 0 otherwise) for [thumb, index, middle, ring, pinky]
        """
        fingers = []
        
        # Thumb (compare x-coordinate for left/right hand)
        if landmarks[self.THUMB_TIP][0] < landmarks[self.THUMB_IP][0] - 0.05:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers (compare y-coordinate)
        finger_tips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        finger_pips = [self.INDEX_PIP, self.MIDDLE_PIP, self.RING_PIP, self.PINKY_PIP]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip][1] < landmarks[pip][1] - FINGER_TIP_THRESHOLD:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def draw_landmarks(self, frame: np.ndarray, hand_landmarks) -> np.ndarray:
        """
        Draw hand landmarks on frame.
        
        Args:
            frame: Input frame
            hand_landmarks: MediaPipe hand landmarks
        
        Returns:
            Frame with landmarks drawn
        """
        if hand_landmarks:
            for landmarks in hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, 
                    landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2)
                )
        return frame
    
    def release(self):
        """Release MediaPipe resources."""
        self.hands.close()
