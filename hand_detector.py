"""
Hand detection and tracking using MediaPipe
"""
import cv2
import mediapipe as mp
import numpy as np
from config import DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, MAX_HANDS


class HandDetector:
    def __init__(self):
        """Initialize MediaPipe hand detector"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def detect_hands(self, frame):
        """
        Detect hands in the frame and return landmarks
        
        Args:
            frame: BGR image from camera
            
        Returns:
            List of hand data dictionaries containing:
            - landmarks: List of 21 (x, y, z) tuples (normalized 0-1)
            - handedness: 'Left' or 'Right'
            - hand_center: (x, y) center of palm
        """
        # FLIP frame first so MediaPipe sees mirrored view
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the FLIPPED frame
        results = self.hands.process(rgb_frame)
        
        hands_data = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                   results.multi_handedness):
                # Get handedness (Left or Right) - now correct because frame is flipped
                hand_label = handedness.classification[0].label
                
                # Extract landmarks as list of (x, y, z) tuples (no flipping needed now)
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append((landmark.x, landmark.y, landmark.z))
                
                # Calculate hand center (average of all landmarks)
                center_x = np.mean([lm[0] for lm in landmarks])
                center_y = np.mean([lm[1] for lm in landmarks])
                
                hands_data.append({
                    'landmarks': landmarks,
                    'handedness': hand_label,
                    'hand_center': (center_x, center_y),
                    'raw_landmarks': hand_landmarks
                })
        
        return hands_data
    
    def draw_landmarks(self, frame, hands_data):
        """
        Draw hand landmarks on the frame
        
        Args:
            frame: BGR image
            hands_data: List of hand data from detect_hands()
        """
        for hand_data in hands_data:
            self.mp_draw.draw_landmarks(
                frame,
                hand_data['raw_landmarks'],
                self.mp_hands.HAND_CONNECTIONS
            )
    
    def get_finger_tip(self, landmarks, finger_name):
        """
        Get the tip position of a specific finger
        
        Args:
            landmarks: List of 21 landmarks
            finger_name: 'Thumb', 'Index', 'Middle', 'Ring', or 'Pinky'
            
        Returns:
            (x, y, z) tuple of finger tip position
        """
        finger_tips = {
            'Thumb': 4,
            'Index': 8,
            'Middle': 12,
            'Ring': 16,
            'Pinky': 20
        }
        
        tip_idx = finger_tips.get(finger_name)
        if tip_idx is not None:
            return landmarks[tip_idx]
        return None
    
    def get_thumb_tip(self, landmarks):
        """Get thumb tip position"""
        return landmarks[4]
    
    def calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points
        
        Args:
            point1: (x, y, z) tuple
            point2: (x, y, z) tuple
            
        Returns:
            Float distance
        """
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def is_finger_extended(self, landmarks, finger_name):
        """
        Check if a finger is extended (not curled)
        
        Args:
            landmarks: List of 21 landmarks
            finger_name: 'Thumb', 'Index', 'Middle', 'Ring', or 'Pinky'
            
        Returns:
            Boolean indicating if finger is extended
        """
        finger_indices = {
            'Thumb': [2, 3, 4],
            'Index': [5, 6, 7, 8],
            'Middle': [9, 10, 11, 12],
            'Ring': [13, 14, 15, 16],
            'Pinky': [17, 18, 19, 20]
        }
        
        indices = finger_indices.get(finger_name)
        if not indices:
            return False
        
        # For thumb, check if tip is far from base
        if finger_name == 'Thumb':
            tip = landmarks[4]
            base = landmarks[2]
            dist = self.calculate_distance(tip, base)
            return dist > 0.1
        
        # For other fingers, check if tip is higher than middle joint
        tip_idx = indices[-1]
        mid_idx = indices[1]
        
        tip_y = landmarks[tip_idx][1]
        mid_y = landmarks[mid_idx][1]
        
        # Extended if tip is above middle joint (lower y value in screen coords)
        return tip_y < mid_y - 0.02
    
    def cleanup(self):
        """Release resources"""
        self.hands.close()
