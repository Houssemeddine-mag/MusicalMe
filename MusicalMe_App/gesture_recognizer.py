"""
Gesture recognition from hand landmarks
"""
from hand_detector import HandDetector
from config import FINGER_TOUCH_THRESHOLD, PINCH_THRESHOLD, NOTE_GESTURES


class GestureRecognizer:
    def __init__(self, hand_detector):
        """
        Initialize gesture recognizer
        
        Args:
            hand_detector: HandDetector instance
        """
        self.hand_detector = hand_detector
        self.previous_note_states = {}
        
    def recognize_gestures(self, hands_data):
        """
        Recognize all gestures from detected hands
        
        Args:
            hands_data: List of hand data from HandDetector
            
        Returns:
            Dictionary containing:
            - notes: List of active note gestures with hand position
            - menu_open: Boolean, frame gesture detected
            - menu_close: Boolean, pinky extended
            - cursor_pos: (x, y) position of index finger for menu navigation
            - select: Boolean, pinch gesture detected
        """
        result = {
            'notes': [],
            'menu_open': False,
            'menu_close': False,
            'cursor_pos': None,
            'select': False
        }
        
        if not hands_data:
            return result
        
        # Check for note gestures (thumb + finger touches)
        for hand_data in hands_data:
            landmarks = hand_data['landmarks']
            handedness = hand_data['handedness']
            hand_center = hand_data['hand_center']
            
            # Check thumb + finger combinations for notes
            note = self._detect_note_gesture(landmarks, handedness)
            if note:
                result['notes'].append({
                    'note': note,
                    'hand_y': hand_center[1],  # For pitch bending
                    'hand': handedness
                })
            
            # Check for index finger pointing (cursor)
            if self.hand_detector.is_finger_extended(landmarks, 'Index'):
                index_tip = self.hand_detector.get_finger_tip(landmarks, 'Index')
                result['cursor_pos'] = (index_tip[0], index_tip[1])
            
            # Check for pinch gesture (select)
            thumb_tip = self.hand_detector.get_thumb_tip(landmarks)
            index_tip = self.hand_detector.get_finger_tip(landmarks, 'Index')
            if thumb_tip and index_tip:
                dist = self.hand_detector.calculate_distance(thumb_tip, index_tip)
                if dist < PINCH_THRESHOLD:
                    result['select'] = True
        
        # Check for pinky up (menu open/close)
        result['menu_open'] = self._detect_pinky_up(hands_data)
        result['menu_close'] = result['menu_open']  # Same gesture toggles
        
        return result
    
    def _detect_note_gesture(self, landmarks, handedness):
        """
        Detect if thumb is touching any finger for note playing
        
        Args:
            landmarks: List of 21 landmarks
            handedness: 'Left' or 'Right'
            
        Returns:
            Note name string or None
        """
        thumb_tip = self.hand_detector.get_thumb_tip(landmarks)
        
        # Check each finger
        for finger_name in ['Index', 'Middle', 'Ring', 'Pinky']:
            finger_tip = self.hand_detector.get_finger_tip(landmarks, finger_name)
            if finger_tip:
                dist = self.hand_detector.calculate_distance(thumb_tip, finger_tip)
                
                if dist < FINGER_TOUCH_THRESHOLD:
                    # Look up which note this gesture corresponds to
                    note = NOTE_GESTURES.get((handedness, finger_name))
                    if note:
                        return note
        
        return None
    
    def _detect_pinky_up(self, hands_data):
        """
        Detect if only the pinky is extended and other fingers are closed
        """
        if not hands_data:
            return False
            
        for hand_data in hands_data:
            landmarks = hand_data['landmarks']
            
            # Check all fingers
            pinky_extended = self.hand_detector.is_finger_extended(landmarks, 'Pinky')
            index_extended = self.hand_detector.is_finger_extended(landmarks, 'Index')
            middle_extended = self.hand_detector.is_finger_extended(landmarks, 'Middle')
            ring_extended = self.hand_detector.is_finger_extended(landmarks, 'Ring')
            
            # Only pinky should be extended
            if pinky_extended and not (index_extended or middle_extended or ring_extended):
                return True
                
        return False
    
    def _detect_frame_gesture(self, hands_data):
        """
        Detect frame gesture (both hands with thumb and index extended)
        More lenient - allows other fingers to be slightly bent
        
        Args:
            hands_data: List of exactly 2 hand data dictionaries
            
        Returns:
            Boolean indicating if frame gesture is detected
        """
        if len(hands_data) != 2:
            return False
        
        both_hands_ok = True
        for hand_data in hands_data:
            landmarks = hand_data['landmarks']
            
            # Check if thumb and index are extended
            thumb_extended = self.hand_detector.is_finger_extended(landmarks, 'Thumb')
            index_extended = self.hand_detector.is_finger_extended(landmarks, 'Index')
            
            # Frame gesture requires AT LEAST thumb + index extended
            # (Other fingers can be in any position - more lenient)
            if not (thumb_extended and index_extended):
                both_hands_ok = False
                break
        
        return both_hands_ok
    
    def get_pitch_zone(self, hand_y):
        """
        Calculate discrete pitch zone based on hand vertical position
        Uses fixed zones instead of continuous bending for predictability
        
        Args:
            hand_y: Current hand Y position (0-1, normalized)
            
        Returns:
            Integer semitone offset (-2, -1, 0, +1, +2)
        """
        from config import NUM_PITCH_ZONES
        
        # Determine which zone the hand is in (0 = top, 4 = bottom)
        zone_index = int(hand_y * NUM_PITCH_ZONES)
        zone_index = max(0, min(NUM_PITCH_ZONES - 1, zone_index))
        
        # Map zone to semitone offset
        # Zone 0 (top) = +2, Zone 1 = +1, Zone 2 = 0, Zone 3 = -1, Zone 4 (bottom) = -2
        semitone_offset = 2 - zone_index
        
        return semitone_offset
    
    def get_pitch_bend_factor(self, hand_y, reference_y=0.5):
        """
        Calculate pitch bend factor based on hand vertical position
        
        Args:
            hand_y: Current hand Y position (0-1, normalized)
            reference_y: Reference Y position (default: center at 0.5)
            
        Returns:
            Pitch multiplier (1.0 = no bend, <1.0 = lower, >1.0 = higher)
        """
        from config import PITCH_BEND_SEMITONES
        
        # Calculate displacement from reference (-0.5 to +0.5 range)
        displacement = reference_y - hand_y  # Inverted because y=0 is top
        
        # Map to semitones (-PITCH_BEND_SEMITONES to +PITCH_BEND_SEMITONES)
        semitone_shift = displacement * PITCH_BEND_SEMITONES * 4  # *4 for sensitivity
        
        # Clamp to max range
        semitone_shift = max(-PITCH_BEND_SEMITONES, 
                            min(PITCH_BEND_SEMITONES, semitone_shift))
        
        # Convert semitones to frequency multiplier
        # Formula: freq_multiplier = 2^(semitones/12)
        pitch_multiplier = 2.0 ** (semitone_shift / 12.0)
        
        return pitch_multiplier
