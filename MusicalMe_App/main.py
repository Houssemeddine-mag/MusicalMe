"""
MusicalMe - Hand Gesture Controlled Music System
Main entry point for the application
"""
import cv2
import sys
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from audio_engine import AudioEngine
from ui_renderer import UIRenderer
from menu_system import MenuSystem
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, FPS


class MusicalMe:
    def __init__(self, shared_camera=None, shared_hand_detector=None, shared_gesture_recognizer=None, shared_window_name=None):
        """Initialize the MusicalMe system"""
        print("Initializing MusicalMe...")
        
        self.shared_resources = shared_camera is not None
        self.window_name = shared_window_name if shared_window_name else 'MusicalMe - Hand Gesture Music'
        
        # Initialize components
        if self.shared_resources:
            self.hand_detector = shared_hand_detector
            self.gesture_recognizer = shared_gesture_recognizer
            self.camera = shared_camera
        else:
            self.hand_detector = HandDetector()
            self.gesture_recognizer = GestureRecognizer(self.hand_detector)
            self.camera = cv2.VideoCapture(CAMERA_INDEX)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, FPS)
            
        self.audio_engine = AudioEngine()
        self.ui_renderer = UIRenderer()
        self.menu_system = MenuSystem(self.ui_renderer, self.audio_engine)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)
        
        # Track active notes
        self.active_note_gestures = set()
        
        print("MusicalMe initialized successfully!")
        print("\nGesture Guide:")
        print("  Left Hand:")
        print("    Thumb + Pinky = DO")
        print("    Thumb + Ring = RE")
        print("    Thumb + Middle = MI")
        print("    Thumb + Index = FA")
        print("  Right Hand:")
        print("    Thumb + Index = SOL")
        print("    Thumb + Middle = LA")
        print("    Thumb + Ring = SI")
        print("    Thumb + Pinky = DO (high)")
        print("\n  Menu Controls:")
        print("    Pinky UP = Open/Close menu")
        print("    Index finger = Move cursor")
        print("    Thumb + Index pinch = Select")
        print("\n  Pitch Bending:")
        print("    Move hand UP while playing = Higher pitch")
        print("    Move hand DOWN while playing = Lower pitch")
        print("\nPress 'q' to quit\n")
    
    def run(self):
        """Main application loop"""
        try:
            while True:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # Detect hands
                hands_data = self.hand_detector.detect_hands(frame)
                
                # Recognize gestures
                gestures = self.gesture_recognizer.recognize_gestures(hands_data)
                
                # Update menu system
                self.menu_system.update(gestures)
                
                # Handle note playing (only when menu is closed)
                if not self.menu_system.is_open:
                    self._handle_note_playing(gestures)
                else:
                    # Stop all notes when menu is open
                    self.audio_engine.stop_all_notes()
                    self.active_note_gestures.clear()
                
                # Render UI
                frame = self.ui_renderer.render_frame(
                    frame, 
                    hands_data, 
                    list(self.active_note_gestures),
                    self.menu_system.is_open
                )
                
                # Draw hand landmarks
                self.hand_detector.draw_landmarks(frame, hands_data)
                
                # Render menu if open
                self.menu_system.render(frame, gestures.get('cursor_pos'))
                
                # Display frame
                cv2.imshow(self.window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or self.menu_system.should_exit_app:
                    print("\nExiting MusicalMe, returning to Hub...")
                    # Reset the exit state for subsequent launches
                    self.menu_system.should_exit_app = False
                    break
        
        finally:
            self.cleanup()
    
    def _handle_note_playing(self, gestures):
        """
        Handle note playing based on detected gestures
        
        Args:
            gestures: Dictionary from GestureRecognizer
        """
        # Get currently detected notes
        current_notes = {note_data['note']: note_data for note_data in gestures['notes']}
        
        # Update or start notes with zone-based pitch
        for note_name, note_data in current_notes.items():
            if note_name not in self.active_note_gestures:
                hand_y = note_data['hand_y']
                
                # Get discrete pitch zone (returns semitone offset: -2, -1, 0, +1, +2)
                semitone_offset = self.gesture_recognizer.get_pitch_zone(hand_y)
                
                # Convert semitones to frequency multiplier
                pitch_multiplier = 2.0 ** (semitone_offset / 12.0)
                
                # Play note with zone-based pitch (no reference Y needed)
                self.audio_engine.play_note(note_name, pitch_multiplier, hand_y)
                self.active_note_gestures.add(note_name)
        
        # Stop notes that are no longer detected
        notes_to_stop = self.active_note_gestures - set(current_notes.keys())
        for note_name in notes_to_stop:
            self.audio_engine.stop_note(note_name)
            self.active_note_gestures.discard(note_name)
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources...")
        self.audio_engine.cleanup()
        
        # Only cleanup these hardware/heavy resources if we own them
        if not getattr(self, 'shared_resources', False):
            self.hand_detector.cleanup()
            self.camera.release()
            cv2.destroyAllWindows()
        print("Goodbye!")


def main():
    """Entry point"""
    window_name = 'MusicalMe - Hand Gesture Music'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    app = MusicalMe(shared_window_name=window_name)
    app.run()


if __name__ == "__main__":
    main()
