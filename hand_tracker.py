"""
Hand tracking and gesture recognition for Air Canvas.

NOTE: This module requires MediaPipe for hand tracking. Due to recent API changes in MediaPipe 0.10+,
there may be compatibility issues. See README.md for installation instructions.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
from config import *

# Try to import hand tracking libraries
HAND_TRACKING_AVAILABLE = False
HAND_TRACKING_METHOD = "none"

# Try cvzone first (simpler API)
try:
    from cvzone.HandTrackingModule import HandDetector as CVZoneHandDetector
    HAND_TRACKING_AVAILABLE = True
    HAND_TRACKING_METHOD = "cvzone"
except Exception as e:
    pass

# If cvzone fails, try direct mediapipe
if not HAND_TRACKING_AVAILABLE:
    try:
        import mediapipe as mp
        if hasattr(mp, 'solutions'):
            # Legacy API (mediapipe < 0.10)
            mp_hands = mp.solutions.hands
            mp_draw = mp.solutions.drawing_utils
            HAND_TRACKING_AVAILABLE = True
            HAND_TRACKING_METHOD = "mediapipe_legacy"
    except Exception as e:
        pass


class HandTracker:
    """Hand tracking and gesture recognition."""
    
    # Finger landmark indices (MediaPipe standard)
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
        """Initialize hand tracking."""
        self.current_gesture = "None"
        self.gesture_history = []
        self.gesture_cooldown_counter = 0
        
        if not HAND_TRACKING_AVAILABLE:
            print("\n" + "=" * 70)
            print("WARNING: Hand tracking is not available!")
            print("=" * 70)
            print("\nMediaPipe hand tracking could not be initialized.")
            print("\nThis is likely due to one of the following reasons:")
            print("1. MediaPipe is not installed")
            print("2. MediaPipe version incompatibility (0.10+ has breaking changes)")
            print("\nTo fix this:")
            print("- Install MediaPipe and cvzone: pip install mediapipe cvzone")
            print("- Or use an older MediaPipe version if available for your Python version")
            print("\nThe application will run in DEMO MODE without hand tracking.")
            print("=" * 70 + "\n")
            
            self.detector = None
            self.method = "mock"
            return
        
        # Initialize based on available method
        if HAND_TRACKING_METHOD == "cvzone":
            try:
                self.detector = CVZoneHandDetector(
                    maxHands=MAX_NUM_HANDS,
                    detectionCon=MEDIAPIPE_DETECTION_CONFIDENCE,
                    minTrackCon=MEDIAPIPE_TRACKING_CONFIDENCE
                )
                self.method = "cvzone"
                print(f"✓ Hand tracking initialized using cvzone")
            except Exception as e:
                print(f"Warning: cvzone initialization failed: {e}")
                self.detector = None
                self.method = "mock"
        
        elif HAND_TRACKING_METHOD == "mediapipe_legacy":
            try:
                self.detector = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=MAX_NUM_HANDS,
                    min_detection_confidence=MEDIAPIPE_DETECTION_CONFIDENCE,
                    min_tracking_confidence=MEDIAPIPE_TRACKING_CONFIDENCE
                )
                self.mp_hands = mp_hands
                self.mp_draw = mp_draw
                self.method = "mediapipe_legacy"
                print(f"✓ Hand tracking initialized using MediaPipe legacy API")
            except Exception as e:
                print(f"Warning: MediaPipe initialization failed: {e}")
                self.detector = None
                self.method = "mock"
        else:
            self.detector = None
            self.method = "mock"
    
    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[list], Dict]:
        """
        Process a frame to detect hands and recognize gestures.
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            Tuple of (hands list, gesture info dict)
        """
        gesture_info = {
            'gesture': 'None',
            'position': None,
            'hand_landmarks': None,
            'confidence': 0.0
        }
        
        if self.method == "mock":
            # Mock mode - no actual hand tracking
            return None, gesture_info
        
        elif self.method == "cvzone":
            return self._process_cvzone(frame)
        
        elif self.method == "mediapipe_legacy":
            return self._process_mediapipe_legacy(frame)
        
        return None, gesture_info
    
    def _process_cvzone(self, frame: np.ndarray) -> Tuple[Optional[list], Dict]:
        """Process frame using cvzone."""
        try:
            hands, img = self.detector.findHands(frame, draw=False)
            
            gesture_info = {
                'gesture': 'None',
                'position': None,
                'hand_landmarks': None,
                'confidence': 0.0
            }
            
            if hands:
                hand = hands[0]
                lmList = hand['lmList']
                fingers = self.detector.fingersUp(hand)
                
                gesture = self._recognize_gesture_from_fingers(fingers)
                gesture = self._smooth_gesture(gesture)
                
                index_tip = lmList[self.INDEX_TIP]
                position = (int(index_tip[0] * CANVAS_WIDTH / frame.shape[1]), 
                           int(index_tip[1] * CANVAS_HEIGHT / frame.shape[0]))
                
                gesture_info = {
                    'gesture': self.current_gesture,
                    'position': position,
                    'hand_landmarks': hands,
                    'confidence': 0.8
                }
            
            return hands, gesture_info
        except Exception as e:
            print(f"Error in cvzone processing: {e}")
            return None, gesture_info
    
    def _process_mediapipe_legacy(self, frame: np.ndarray) -> Tuple[Optional[list], Dict]:
        """Process frame using MediaPipe legacy API."""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb_frame)
            
            gesture_info = {
                'gesture': 'None',
                'position': None,
                'hand_landmarks': None,
                'confidence': 0.0
            }
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Extract landmarks
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append((landmark.x, landmark.y, landmark.z))
                
                # Recognize gesture
                fingers = self._count_fingers_up(landmarks)
                gesture = self._recognize_gesture_from_fingers(fingers)
                gesture = self._smooth_gesture(gesture)
                
                # Get position
                index_tip = hand_landmarks.landmark[self.INDEX_TIP]
                position = (int(index_tip.x * CANVAS_WIDTH), int(index_tip.y * CANVAS_HEIGHT))
                
                gesture_info = {
                    'gesture': self.current_gesture,
                    'position': position,
                    'hand_landmarks': results.multi_hand_landmarks,
                    'confidence': 0.8
                }
            
            return results.multi_hand_landmarks if results.multi_hand_landmarks else None, gesture_info
        except Exception as e:
            print(f"Error in MediaPipe processing: {e}")
            return None, gesture_info
    
    def _count_fingers_up(self, landmarks: List[Tuple[float, float, float]]) -> List[int]:
        """Determine which fingers are up (for MediaPipe legacy)."""
        fingers = []
        
        # Thumb
        if landmarks[self.THUMB_TIP][0] < landmarks[self.THUMB_IP][0] - 0.05:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers
        finger_tips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        finger_pips = [self.INDEX_PIP, self.MIDDLE_PIP, self.RING_PIP, self.PINKY_PIP]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip][1] < landmarks[pip][1] - FINGER_TIP_THRESHOLD:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def _recognize_gesture_from_fingers(self, fingers: List[int]) -> str:
        """Recognize gesture from fingers up list."""
        if fingers == [0, 1, 0, 0, 0]:
            return "Draw"
        elif fingers == [0, 1, 1, 0, 0]:
            return "Move"
        elif fingers == [0, 1, 1, 1, 0]:
            return "ChangeColor"
        elif fingers == [1, 0, 0, 0, 0]:
            return "Undo"
        elif fingers == [0, 0, 0, 0, 1]:
            return "Redo"
        elif sum(fingers) == 5:
            return "Clear"
        elif sum(fingers) == 0:
            return "Pause"
        return "None"
    
    def _smooth_gesture(self, gesture: str) -> str:
        """Apply gesture smoothing and cooldown."""
        if self.gesture_cooldown_counter > 0:
            self.gesture_cooldown_counter -= 1
            return self.current_gesture
        
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > GESTURE_SMOOTHING_FRAMES:
            self.gesture_history.pop(0)
        
        if len(self.gesture_history) >= GESTURE_SMOOTHING_FRAMES:
            gesture = max(set(self.gesture_history), key=self.gesture_history.count)
        
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.gesture_cooldown_counter = GESTURE_COOLDOWN
        
        return self.current_gesture
    
    def draw_landmarks(self, frame: np.ndarray, hands) -> np.ndarray:
        """Draw hand landmarks on frame."""
        if self.method == "mock" or hands is None:
            return frame
        
        try:
            if self.method == "cvzone":
                frame, _ = self.detector.findHands(frame, draw=True)
            elif self.method == "mediapipe_legacy" and hands:
                for landmarks in hands:
                    self.mp_draw.draw_landmarks(
                        frame, landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2)
                    )
        except Exception as e:
            pass  # Silently handle drawing errors
        
        return frame
    
    def release(self):
        """Release resources."""
        if self.method == "mediapipe_legacy" and self.detector:
            try:
                self.detector.close()
            except:
                pass
