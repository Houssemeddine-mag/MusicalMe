import time
import subprocess
import sys
import os
import cv2
import numpy as np

# Add the MusicalMe app directory to the system path so we can import from it seamlessly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MusicalMe_App'))

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from main import MusicalMe

# Add Mathic framework
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Mathic'))
try:
    from mathic_game import Mathic
except ImportError:
    print("Warning: could not import Mathic")

# Add YouDraw framework
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'YouDraw'))
try:
    from youdraw_game import YouDraw
except ImportError:
    print("Warning: could not import YouDraw")

def overlay_image_alpha(img, img_overlay, x, y):
    """Overlay img_overlay on top of img at (x, y) accounting for the alpha channel."""
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to draw
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Check for alpha channel
    if img_overlay.shape[2] == 4:
        alpha = img_overlay[y1o:y2o, x1o:x2o, 3] / 255.0
        alpha_inv = 1.0 - alpha
        for c in range(3):
            img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                    alpha_inv * img[y1:y2, x1:x2, c])
    else:
        img[y1:y2, x1:x2] = img_overlay[y1o:y2o, x1o:x2o]

class EducationalHub:
    def __init__(self):
        """Initialize the Educational Hub for kids"""
        print("Starting Kids Educational Hub...")
        self.hand_detector = HandDetector()
        self.gesture_recognizer = GestureRecognizer(self.hand_detector)
        
        # Initialize Camera
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)

        # Full screen window setup
        self.window_name = "Kids Play & Learn Hub"
        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.hub_cooldown = 0

        self.logos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logos')
        
        # Pre-load Hub Background
        bg_path = os.path.join(self.logos_dir, "BG.png")
        self.bg = None
        if os.path.exists(bg_path):
            bg_img = cv2.imread(bg_path)
            if bg_img is not None:
                self.bg = cv2.resize(bg_img, (1280, 720))

        self.hub_cooldown = 0

        # Size mappings (scaled nicely for a seamless 1280x720 layout)
        logo_w, logo_h = 360, 240
        exit_w, exit_h = 100, 100

        # Define Games/Apps positioned according to the picture
        self.games = [
            {"name": "MusicalMe", "file": "MusicalMe_logo.png", "x": 100, "y": 140, "w": logo_w, "h": logo_h},
            {"name": "Mathic", "file": "Mathic_logo.png", "x": 460, "y": 120, "w": logo_w, "h": logo_h},
            {"name": "Alphabet", "file": "Alphabet_logo.png", "x": 820, "y": 140, "w": logo_w, "h": logo_h},
            {"name": "YouDraw", "file": "YouDraw_logo.png", "x": 100, "y": 420, "w": logo_w, "h": logo_h},
            {"name": "TheZoo", "file": "TheZoo_logo.png", "x": 460, "y": 440, "w": logo_w, "h": logo_h},
            {"name": "CarRoad", "file": "Carroad_logo.png", "x": 820, "y": 420, "w": logo_w, "h": logo_h},
            {"name": "Exit", "file": "Exit.png", "x": 1150, "y": 30, "w": exit_w, "h": exit_h}
        ]

        # Load PNGs with transparency
        for game in self.games:
            path = os.path.join(self.logos_dir, game["file"])
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    game["img"] = cv2.resize(img, (game["w"], game["h"]))
                else:
                    game["img"] = None
            else:
                print(f"Warning: Logo {path} not found")
                game["img"] = None
                
            # Set rect bounds for hitbox processing (generous hitboxes)
            game["rect"] = [game["x"], game["y"], game["x"]+game["w"], game["y"]+game["h"]]

    def launch_musical_me(self):
        """Launch the MusicalMe app"""
        print("\n=== Launching MusicalMe ===")
        # Instead of shutting down the camera, we pass our active components seamlessly!
        
        # Show loading screen with same background
        loading_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        if self.bg is not None:
            loading_frame[:] = self.bg.copy()
        else:
            loading_frame[:] = (240, 240, 240)
            
        loading_path = os.path.join(self.logos_dir, "Loading.png")
        if os.path.exists(loading_path):
            loading_img = cv2.imread(loading_path, cv2.IMREAD_UNCHANGED)
            if loading_img is not None:
                # Resize to fit nicely (e.g., 800px wide, maintaining aspect ratio)
                lw = 800
                lh = int(loading_img.shape[0] * (lw / loading_img.shape[1]))
                loading_img = cv2.resize(loading_img, (lw, lh))
                
                # Center on the screen
                x = (1280 - lw) // 2
                y = (720 - lh) // 2
                overlay_image_alpha(loading_frame, loading_img, x, y)
        else:
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (255, 255, 255), -1)
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (0, 0, 0), 4)
            cv2.putText(loading_frame, "Loading the Game...", (400, 380), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
        
        cv2.imshow(self.window_name, loading_frame)
        cv2.waitKey(100) # Give UI time to update
        
        # Start MusicalMe game sharing the same resources
        try:
            app = MusicalMe(shared_camera=self.camera, 
                            shared_hand_detector=self.hand_detector,
                            shared_gesture_recognizer=self.gesture_recognizer,
                            shared_window_name=self.window_name)
            app.run()
        except Exception as e:
            print(f"Error running MusicalMe: {e}")
        
        # Flush the cv2 input buffer so lingering 'q' presses don't close the Hub immediately
        import time
        time.sleep(0.5)
        while cv2.waitKey(10) != -1:
            pass
            
        # Flush the old frames from the camera buffer so old pinch gestures aren't processed
        for _ in range(5):
            self.camera.read()
            
        print("Returning to Hub...")

    def launch_youdraw(self):
        """Launch the YouDraw app"""
        print("\\n=== Launching YouDraw ===")
        
        # Show loading screen with same background
        loading_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        if self.bg is not None:
            loading_frame[:] = self.bg.copy()
        else:
            loading_frame[:] = (240, 240, 240)
            
        loading_path = os.path.join(self.logos_dir, "Loading.png")
        if os.path.exists(loading_path):
            loading_img = cv2.imread(loading_path, cv2.IMREAD_UNCHANGED)
            if loading_img is not None:
                lw = 800
                lh = int(loading_img.shape[0] * (lw / loading_img.shape[1]))
                loading_img = cv2.resize(loading_img, (lw, lh))
                x = (1280 - lw) // 2
                y = (720 - lh) // 2
                overlay_image_alpha(loading_frame, loading_img, x, y)
        else:
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (255, 255, 255), -1)
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (0, 0, 0), 4)
            cv2.putText(loading_frame, "Loading the Game...", (400, 380), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
        
        cv2.imshow(self.window_name, loading_frame)
        cv2.waitKey(100)
        
        try:
            app = YouDraw(shared_camera=self.camera, 
                          shared_hand_detector=self.hand_detector,
                          shared_gesture_recognizer=self.gesture_recognizer,
                          shared_window_name=self.window_name)
            app.run()
        except Exception as e:
            print(f"Error running YouDraw: {e}")
        
        import time
        time.sleep(0.5)
        # Clear out extra frames to avoid immediate re-clicks
        for _ in range(5):
            self.camera.read()
            
        print("Returning to Hub...")


    def launch_mathic(self):
        """Launch the Mathic app"""
        print("\n=== Launching Mathic ===")
        
        # Show loading screen with same background
        loading_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        if self.bg is not None:
            loading_frame[:] = self.bg.copy()
        else:
            loading_frame[:] = (240, 240, 240)
            
        loading_path = os.path.join(self.logos_dir, "Loading.png")
        if os.path.exists(loading_path):
            loading_img = cv2.imread(loading_path, cv2.IMREAD_UNCHANGED)
            if loading_img is not None:
                lw = 800
                lh = int(loading_img.shape[0] * (lw / loading_img.shape[1]))
                loading_img = cv2.resize(loading_img, (lw, lh))
                x = (1280 - lw) // 2
                y = (720 - lh) // 2
                overlay_image_alpha(loading_frame, loading_img, x, y)
        else:
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (255, 255, 255), -1)
            cv2.rectangle(loading_frame, (350, 300), (950, 420), (0, 0, 0), 4)
            cv2.putText(loading_frame, "Loading the Game...", (400, 380), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
        
        cv2.imshow(self.window_name, loading_frame)
        cv2.waitKey(100)
        
        try:
            app = Mathic(shared_camera=self.camera, 
                         shared_hand_detector=self.hand_detector,
                         shared_gesture_recognizer=self.gesture_recognizer,
                         shared_window_name=self.window_name)
            app.run()
        except Exception as e:
            print(f"Error running Mathic: {e}")
        
        import time
        time.sleep(0.5)
        while cv2.waitKey(10) != -1:
            pass
        for _ in range(5):
            self.camera.read()
            
        print("Returning to Hub...")

    def run(self):
        """Main loop for the Landing Page"""
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Detect hands directly
                hands_data = self.hand_detector.detect_hands(frame)
                gestures = self.gesture_recognizer.recognize_gestures(hands_data)
                
                # Flip the frame for display (mirror effect)
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Draw Hub Background
                if self.bg is not None:
                    frame[:] = self.bg.copy()
                else:
                    frame[:] = (240, 240, 240)
                    cv2.putText(frame, "Kids Play & Learn Hub!", (380, 100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4)

                selected_game = None
                
                if self.hub_cooldown > 0:
                    self.hub_cooldown -= 1

                # Cursor processing
                cursor_pos_norm = gestures.get('cursor_pos')
                cursor_pos_px = None
                if cursor_pos_norm:
                    cx = int(cursor_pos_norm[0] * w)
                    cy = int(cursor_pos_norm[1] * h)
                    cursor_pos_px = (cx, cy)

                # Draw Game Modules
                for game in self.games:
                    x1, y1, x2, y2 = game["rect"]
                    
                    hover = False
                    is_pinching = gestures.get('select', False)

                    if cursor_pos_px:
                        cx, cy = cursor_pos_px
                        # Generous padding of 30 for kids
                        if (x1 - 30) < cx < (x2 + 30) and (y1 - 30) < cy < (y2 + 30):
                            hover = True
                            if is_pinching and self.hub_cooldown == 0:
                                selected_game = game["name"]
                                self.hub_cooldown = 45 # Apply substantial cooldown (1.5 seconds) upon clicking any game
                                
                    # Draw Images
                    if game.get("img") is not None:
                        # Pop-out hover effect!
                        if hover:
                            render_img = cv2.resize(game["img"], (int(game["w"]*1.1), int(game["h"]*1.1)))
                            off_x = game["x"] - int(game["w"]*0.05)
                            off_y = game["y"] - int(game["h"]*0.05)
                            overlay_image_alpha(frame, render_img, off_x, off_y)
                        else:
                            overlay_image_alpha(frame, game["img"], game["x"], game["y"])
                    else:
                        # Fallback rectangles if logos failed to load
                        color = (150, 150, 150)
                        thickness = 5 if hover else -1
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                        if thickness == 5:
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), -1)
                        cv2.putText(frame, game["name"], (x1 + 40, y1 + int(game["h"]/2)), 
                                    cv2.FONT_HERSHEY_DUPLEX, 1.2, (50, 50, 50), 3)

                # Hand landmarks (draw after UI so it's on top!)
                self.hand_detector.draw_landmarks(frame, hands_data)

                # Draw our cursor point
                if cursor_pos_px:
                    cursor_color = (150, 0, 255) if gestures.get('select', False) else (0, 0, 255)
                    cv2.circle(frame, cursor_pos_px, 8, cursor_color, -1)

                cv2.imshow(self.window_name, frame)

                if selected_game == "MusicalMe":
                    self.launch_musical_me()
                    gestures['select'] = False
                elif selected_game == "Mathic":
                    self.launch_mathic()
                    gestures['select'] = False
                elif selected_game == "YouDraw":
                    self.launch_youdraw()
                    gestures['select'] = False
                elif selected_game == "Exit":
                    print("Exiting Educational Hub...")
                    break
                elif selected_game is not None:
                    # Ignore other games for now, just reset the gesture
                    gestures['select'] = False

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    hub = EducationalHub()
    hub.run()


