import cv2
import sys
import os
import numpy as np
import pygame
from pygame import mixer

# Add the MusicalMe app directory to the system path so we can reuse the hand tracking engine natively
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MusicalMe_App'))

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer

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

class Mathic:
    def __init__(self, shared_camera=None, shared_hand_detector=None, shared_gesture_recognizer=None, shared_window_name=None):
        """Initialize the Mathic game"""
        print("Initializing Mathic...")
        
        self.shared_resources = shared_camera is not None
        self.window_name = shared_window_name if shared_window_name else 'Kids Play & Learn Hub'
        
        # Initialize components
        if self.shared_resources:
            self.hand_detector = shared_hand_detector
            self.gesture_recognizer = shared_gesture_recognizer
            self.camera = shared_camera
        else:
            self.hand_detector = HandDetector()
            self.gesture_recognizer = GestureRecognizer(self.hand_detector)
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)
            
        # State for equation
        self.game_mode = 'BUILDER' # BUILDER or QUIZ
        self.quiz_state = 'SELECT_LEVEL' # SELECT_LEVEL or PLAY
        self.quiz_level = 1
        self.quiz_operator = '+'
        self.quiz_eq = None
        self.quiz_input = ""
        self.quiz_feedback = 'NONE'
        self.quiz_feedback_timer = 0
        
        self.equation = []
        self.result = None
        self.anim_state = 'IDLE' # IDLE, SHRINKING, SHOW_RESULT
        self.anim_scale = 1.0
        
        # Debounce logic
        self.pinch_cooldown = 0
        self.was_pinching = False
        
        # Menu logic (like MusicalMe)

        self.menu_open = False
        self.menu_cooldown = 0
        self.learn_number = None

        import pygame
        from pygame import mixer
        try:
            if getattr(pygame, 'get_init', None) and not pygame.get_init(): pygame.init()
            if getattr(mixer, 'get_init', None) and not mixer.get_init(): mixer.init()
        except:
            pass

        # Load number images
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Load background image
        self.bg_image = None
        bg_path = os.path.join(base_dir, 'logos', 'BG_Mathical.png')
        if os.path.exists(bg_path):
            self.bg_image = cv2.imread(bg_path)
            
        self.numbers_dir = os.path.join(base_dir, 'numbers')
        self.number_images = {}
        for i in range(10):
            img_path = os.path.join(self.numbers_dir, f"{i}.png")
            if os.path.exists(img_path):
                img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    # We'll rely on the run loop to resize if needed or just resize it now to fit 80x80
                    self.number_images[str(i)] = cv2.resize(img, (80, 80))
        
        print("Mathic initialized successfully!")
    
    def evaluate_equation(self):
        """Evaluate the current equation list (e.g., ['5', '+', '3'])"""
        if not self.equation:
            return ""
            
        try:
            # Join the equation properly, replacing 'x' with '*' for evaluation
            eq_str = "".join(self.equation)
            eval_str = eq_str.replace('x', '*')
            
            import re
            # Remove leading zeros to prevent Python SyntaxError during eval
            eval_str = re.sub(r'\b0+(?=[0-9])', '', eval_str)
            
            # Use eval carefully (only math characters are allowed)
            result = eval(eval_str)
            
            # Format nicely
            if isinstance(result, float) and result.is_integer():
                return str(int(result))
            return str(round(result, 2))
        except Exception as e:
            return "?"

    import random
    def generate_quiz(self, level, op):
        import random
        # Level 1: n (0-9)
        # Level 2: nn (10-99) and n (0-9)
        # Level 3: nn (10-99) and nn (10-99)
        # Level 4: nnn (100-999) and n (0-9)
        if level == 1:
            n1 = random.randint(0, 9)
            n2 = random.randint(0, 9)
        elif level == 2:
            n1 = random.randint(10, 99)
            n2 = random.randint(0, 9)
        elif level == 3:
            n1 = random.randint(10, 99)
            n2 = random.randint(10, 99)
        elif level == 4:
            n1 = random.randint(100, 999)
            n2 = random.randint(0, 9)
        else:
            n1, n2 = 1, 1

        # Fix subtraction so n1 >= n2
        if op == '-':
            if n1 < n2:
                n1, n2 = n2, n1

        # Fix division so result is an integer
        if op == '/':
            n2 = max(1, n2) # Prevent division by 0
            n1 = n1 * n2 # Enforce clean division

        # Calculate result
        eval_str = f"{n1} {'*' if op=='x' else op} {n2}"
        ans = int(eval(eval_str))
        
        self.quiz_eq = {'num1': n1, 'num2': n2, 'op': op, 'ans': ans}
        self.quiz_input = ""
        self.quiz_feedback = 'NONE'
        self.quiz_feedback_timer = 0
            
    def run(self):
        """Main application loop"""
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Detect hands
                hands_data = self.hand_detector.detect_hands(frame)
                gestures = self.gesture_recognizer.recognize_gestures(hands_data)
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Set background
                if self.bg_image is not None:
                    bg_resized = cv2.resize(self.bg_image, (w, h))
                    frame[:] = bg_resized
                else:
                    # Fallback simple kid-friendly background
                    frame[:] = (245, 245, 245)
                
                # --- Draw UI ---
                hit_btn = None
                
                if self.game_mode == 'QUIZ':
                    if self.quiz_state == 'SELECT_LEVEL':
                        cv2.putText(frame, "Select Quiz Level", (w//2 - 250, 150), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 0), 4)
                        level_rects = []
                        lvl_w, lvl_h = 200, 150
                        lvl_spacing = 50
                        start_x = (w - (4 * lvl_w + 3 * lvl_spacing)) // 2
                        for i in range(1, 5):
                            lx1 = start_x + (i-1) * (lvl_w + lvl_spacing)
                            ly1 = h//2 - lvl_h//2
                            lx2 = lx1 + lvl_w
                            ly2 = ly1 + lvl_h
                            level_rects.append({'val': f"L{i}", 'rect': (lx1, ly1, lx2, ly2)})
                            
                            cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (200, 220, 255), -1)
                            cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (100, 150, 255), 3)
                            
                            lbl = f"Level {i}"
                            cv2.putText(frame, lbl, (lx1 + 20, ly1 + 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (50, 50, 200), 2)
                    elif self.quiz_state == 'PLAY':
                        # Operators Top
                        op_rects = []
                        op_w, op_h = 100, 100
                        operators = ['+', '-', 'x', '/']
                        start_op_x = (w - (4 * op_w + 3 * 40)) // 2
                        for i, op in enumerate(operators):
                            ox1 = start_op_x + i * (op_w + 40)
                            oy1 = 80
                            ox2 = ox1 + op_w
                            oy2 = oy1 + op_h
                            op_rects.append({'val': op, 'rect': (ox1, oy1, ox2, oy2)})
                            
                            # Highlight the active operator
                            if self.quiz_eq is not None and self.quiz_eq['op'] == op:
                                cv2.rectangle(frame, (ox1, oy1), (ox2, oy2), (150, 255, 150), -1)
                            else:
                                cv2.rectangle(frame, (ox1, oy1), (ox2, oy2), (200, 240, 255), -1)
                            cv2.rectangle(frame, (ox1, oy1), (ox2, oy2), (100, 150, 200), 2)
                            ts = cv2.getTextSize(op, cv2.FONT_HERSHEY_DUPLEX, 2.0, 3)[0]
                            cv2.putText(frame, op, (ox1 + (op_w - ts[0])//2, oy1 + (op_h + ts[1])//2), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 150), 3)

                        # Numbers Bottom
                        num_rects = []
                        num_width = 80
                        num_height = 80
                        spacing = (w - (10 * num_width)) // 11
                        for i in range(10):
                            nx1 = spacing + i * (num_width + spacing)
                            ny1 = h - num_height - 60
                            nx2 = nx1 + num_width
                            ny2 = ny1 + num_height
                            num_rects.append({'val': str(i), 'rect': (nx1, ny1, nx2, ny2)})
                            
                            if str(i) in self.number_images:
                                overlay_image_alpha(frame, self.number_images[str(i)], nx1, ny1)
                            else:
                                cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (200, 220, 200), -1)
                                cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (100, 120, 100), 2)
                                ts = cv2.getTextSize(str(i), cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
                                cv2.putText(frame, str(i), (nx1 + (num_width - ts[0])//2, ny1 + (num_height + ts[1])//2), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 3)
                        
                        # DEL Bottom Rightish corner above numbers
                        del_w, del_h = 100, 80
                        dx1 = w - del_w - 40
                        dy1 = h - del_h - 180
                        dx2 = dx1 + del_w
                        dy2 = dy1 + del_h
                        num_rects.append({'val': 'DEL', 'rect': (dx1, dy1, dx2, dy2)})
                        cv2.rectangle(frame, (dx1, dy1), (dx2, dy2), (200, 200, 255), -1)
                        ts = cv2.getTextSize('DEL', cv2.FONT_HERSHEY_DUPLEX, 1.2, 3)[0]
                        cv2.putText(frame, 'DEL', (dx1 + (del_w - ts[0])//2, dy1 + (del_h + ts[1])//2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 200), 3)

                        # CHECK Bottom Leftish corner above numbers
                        chk_w, chk_h = 120, 80
                        cx1 = 40
                        cy1 = h - chk_h - 180
                        cx2 = cx1 + chk_w
                        cy2 = cy1 + chk_h
                        num_rects.append({'val': 'CHECK', 'rect': (cx1, cy1, cx2, cy2)})
                        cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (200, 255, 200), -1)
                        ts = cv2.getTextSize('Check', cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
                        cv2.putText(frame, 'Check', (cx1 + (chk_w - ts[0])//2, cy1 + (chk_h + ts[1])//2), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 150, 0), 2)

                        # Mid Equation
                        if self.quiz_eq is None:
                            cv2.putText(frame, "Select an operator above", (w//2 - 300, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.5, (100, 100, 100), 3)
                        else:
                            eq_str = f"{self.quiz_eq['num1']} {self.quiz_eq['op']} {self.quiz_eq['num2']} = {self.quiz_input}"
                            
                            color = (0, 0, 0) # default Black
                            
                            if self.quiz_feedback == 'CORRECT':
                                color = (0, 200, 0)
                            elif self.quiz_feedback == 'WRONG':
                                color = (0, 0, 255)
                                
                            text_size = cv2.getTextSize(eq_str, cv2.FONT_HERSHEY_DUPLEX, 3.0, 5)[0]
                            tx = (w - text_size[0]) // 2
                            ty = h // 2
                            cv2.putText(frame, eq_str, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 3.0, color, 5)
                            
                            if self.quiz_feedback == 'CORRECT':
                                cv2.putText(frame, "Correct! Pinch anywhere for the next equation", (w//2 - 280, h//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 150, 100), 2)
                            elif self.quiz_feedback == 'WRONG':
                                cv2.putText(frame, "ooh, Try again", (w//2 - 110, h//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                elif self.game_mode == 'BUILDER':
                        # 1. Numbers 0-9 at the top (small)
                    num_rects = []
                    num_width = 80
                    num_height = 80
                    # Calculate spacing to fit 10 numbers evenly across the 1280 width
                    spacing = (w - (10 * num_width)) // 11
                    for i in range(10):
                        x1 = spacing + i * (num_width + spacing)
                        y1 = 30 # At the very top
                        x2 = x1 + num_width
                        y2 = y1 + num_height
                        num_rects.append({'val': str(i), 'rect': (x1, y1, x2, y2)})
                    
                        if str(i) in self.number_images:
                            overlay_image_alpha(frame, self.number_images[str(i)], x1, y1)
                        else:
                            # Fallback Draw box
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 220, 200), -1)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 120, 100), 2)
                        
                            # Draw number
                            text_size = cv2.getTextSize(str(i), cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
                            tx = x1 + (num_width - text_size[0]) // 2
                            ty = y1 + (num_height + text_size[1]) // 2
                            cv2.putText(frame, str(i), (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 3)

                    # 2. Operators at the right side and '=' at the left (larger)
                    operators = ['+', '-', 'x', '/']
                    op_rects = []
                    op_width = 110
                    op_height = 110
                    op_start_y = 150
                    op_spacing = 25
                
                    for i, op in enumerate(operators):
                        x1 = w - op_width - 40 # Right side with a 40px margin
                        y1 = op_start_y + i * (op_height + op_spacing)
                        x2 = x1 + op_width
                        y2 = y1 + op_height
                        op_rects.append({'val': op, 'rect': (x1, y1, x2, y2)})
                    
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 240, 255), -1)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 150, 200), 2)
                    
                        # Draw operator
                        text_size = cv2.getTextSize(op, cv2.FONT_HERSHEY_DUPLEX, 2.0, 4)[0]
                        tx = x1 + (op_width - text_size[0]) // 2
                        ty = y1 + (op_height + text_size[1]) // 2
                        cv2.putText(frame, op, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 150), 4)

                    # Left side '=' operator
                    eq_x1 = 40  # Left side margin
                    eq_y1 = op_start_y + int(1.5 * (op_height + op_spacing)) # roughly middle
                    eq_x2 = eq_x1 + op_width
                    eq_y2 = eq_y1 + op_height
                    op_rects.append({'val': '=', 'rect': (eq_x1, eq_y1, eq_x2, eq_y2)})
                
                    cv2.rectangle(frame, (eq_x1, eq_y1), (eq_x2, eq_y2), (200, 255, 200), -1)
                    cv2.rectangle(frame, (eq_x1, eq_y1), (eq_x2, eq_y2), (100, 200, 100), 2)
                    text_size = cv2.getTextSize('=', cv2.FONT_HERSHEY_DUPLEX, 2.0, 4)[0]
                    eq_tx = eq_x1 + (op_width - text_size[0]) // 2
                    eq_ty = eq_y1 + (op_height + text_size[1]) // 2
                    cv2.putText(frame, '=', (eq_tx, eq_ty), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 150, 0), 4)

                    # Left side 'DEL' operator
                    del_x1 = 40  # Left side margin
                    del_y1 = op_start_y # Top left
                    del_x2 = del_x1 + op_width
                    del_y2 = del_y1 + op_height
                    op_rects.append({'val': 'DEL', 'rect': (del_x1, del_y1, del_x2, del_y2)})
                
                    cv2.rectangle(frame, (del_x1, del_y1), (del_x2, del_y2), (200, 200, 255), -1)
                    cv2.rectangle(frame, (del_x1, del_y1), (del_x2, del_y2), (100, 100, 255), 2)
                    text_size = cv2.getTextSize('DEL', cv2.FONT_HERSHEY_DUPLEX, 1.2, 3)[0]
                    del_tx = del_x1 + (op_width - text_size[0]) // 2
                    del_ty = del_y1 + (op_height + text_size[1]) // 2
                    cv2.putText(frame, 'DEL', (del_tx, del_ty), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 200), 3)

                    # --- Middle Equation Area ---
                    eq_str = " ".join(self.equation)
                    if self.anim_state == 'IDLE':
                        if eq_str:
                            # Draw normal equation
                            text_size = cv2.getTextSize(eq_str, cv2.FONT_HERSHEY_DUPLEX, 3.0, 5)[0]
                            tx = (w - text_size[0]) // 2
                            ty = (h + text_size[1]) // 2
                            cv2.putText(frame, eq_str, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 3.0, (100, 100, 255), 5)
                        else:
                            cv2.putText(frame, "Pinch numbers to write an equation!", (w//2 - 400, h//2), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (180, 180, 180), 3)
                        
                    elif self.anim_state == 'SHRINKING':
                        # Scale goes 1.0 -> 0.0
                        self.anim_scale = max(0.0, self.anim_scale - 0.05)
                        if self.anim_scale == 0.0:
                            self.anim_state = 'SHOW_RESULT'
                            self.anim_scale = 0.0 # reset for popup
                            self.result = self.evaluate_equation()
                            self.equation.clear()
                        else:
                            # Shrink equation
                            font_scale = max(0.1, 3.0 * self.anim_scale)
                            thickness = max(1, int(5 * self.anim_scale))
                            text_size = cv2.getTextSize(eq_str, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)[0]
                            tx = (w - text_size[0]) // 2
                            ty = (h + text_size[1]) // 2
                            cv2.putText(frame, eq_str, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, (100, 100, 255), thickness)
                        
                    elif self.anim_state == 'SHOW_RESULT':
                        # Scale goes 0.0 -> 1.0 for result
                        self.anim_scale = min(1.0, self.anim_scale + 0.05)
                        res_str = f"{self.result}"
                        font_scale = max(0.1, 4.0 * self.anim_scale)
                        thickness = max(1, int(8 * self.anim_scale))
                        text_size = cv2.getTextSize(res_str, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)[0]
                        tx = (w - text_size[0]) // 2
                        ty = (h + text_size[1]) // 2
                        cv2.putText(frame, res_str, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 200, 0), thickness)
                    
                        if self.anim_scale >= 1.0:
                            # Wait a bit or let user click new numbers to reset
                            cv2.putText(frame, "Pinch anywhere to continue", (w//2 - 200, h - 100), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (150, 150, 150), 2)

                elif self.game_mode == 'LEARN':
                    num_rects = []
                    left_x = 100
                    right_x = w - 180
                    y_spacing = (h - 100) // 5
                    
                    for i in range(10):
                        if i < 5:
                            nx1 = left_x
                            ny1 = 50 + i * y_spacing
                        else:
                            nx1 = right_x
                            ny1 = 50 + (i-5) * y_spacing
                            
                        nx2 = nx1 + 80
                        ny2 = ny1 + 80
                        
                        num_rects.append({'val': str(i), 'rect': (nx1, ny1, nx2, ny2)})
                        
                        if str(i) in self.number_images:
                            overlay_image_alpha(frame, self.number_images[str(i)], nx1, ny1)
                        else:
                            cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (200, 220, 200), -1)
                            cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (100, 120, 100), 2)
                            ts = cv2.getTextSize(str(i), cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
                            cv2.putText(frame, str(i), (nx1 + (80 - ts[0])//2, ny1 + (80 + ts[1])//2), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 3)

                    if self.learn_number is not None:
                        cx_center = w // 2
                        cy_center = h // 2 - 100
                        num_str = str(self.learn_number)
                        
                        if num_str in self.number_images:
                            large_img = cv2.resize(self.number_images[num_str], (200, 200))
                            overlay_image_alpha(frame, large_img, cx_center - 100, cy_center - 100)
                        else:
                            cv2.putText(frame, num_str, (cx_center - 50, cy_center + 50), cv2.FONT_HERSHEY_DUPLEX, 6.0, (0, 0, 0), 8)
                            
                        en_w, en_h = 160, 80
                        en_x1 = cx_center - 200
                        en_y1 = cy_center + 150
                        en_x2 = en_x1 + en_w
                        en_y2 = en_y1 + en_h
                        
                        num_rects.append({'val': 'EN', 'rect': (en_x1, en_y1, en_x2, en_y2)})
                        cv2.rectangle(frame, (en_x1, en_y1), (en_x2, en_y2), (150, 150, 255), -1)
                        cv2.rectangle(frame, (en_x1, en_y1), (en_x2, en_y2), (100, 100, 200), 2)
                        cv2.putText(frame, "English", (en_x1 + 15, en_y1 + 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)

                        fr_x1 = cx_center + 40
                        fr_y1 = cy_center + 150
                        fr_x2 = fr_x1 + en_w
                        fr_y2 = fr_y1 + en_h
                        
                        num_rects.append({'val': 'FR', 'rect': (fr_x1, fr_y1, fr_x2, fr_y2)})
                        cv2.rectangle(frame, (fr_x1, fr_y1), (fr_x2, fr_y2), (255, 150, 150), -1)
                        cv2.rectangle(frame, (fr_x1, fr_y1), (fr_x2, fr_y2), (200, 100, 100), 2)
                        cv2.putText(frame, "Francais", (fr_x1 + 10, fr_y1 + 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)

                # Decrease cooldowns
                if self.pinch_cooldown > 0:
                    self.pinch_cooldown -= 1
                if self.menu_cooldown > 0:
                    self.menu_cooldown -= 1

                # Check for pinky up (Menu toggle)
                is_pinky_up = gestures.get('menu_open', False)
                if is_pinky_up and self.menu_cooldown == 0:
                    self.menu_open = not self.menu_open
                    self.menu_cooldown = 15 # Delay to avoid rapidly opening/closing
                    
                # If Menu is open, draw the Exit menu overlay
                exit_clicked = False
                if self.menu_open:
                    menu_w, menu_h = 400, 400
                    mx1 = (w - menu_w) // 2
                    my1 = (h - menu_h) // 2
                    mx2 = mx1 + menu_w
                    my2 = my1 + menu_h
                    
                    # Darken background slightly
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (mx1, my1), (mx2, my2), (50, 50, 60), -1)
                    cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
                    cv2.rectangle(frame, (mx1, my1), (mx2, my2), (200, 200, 255), 4)
                    
                    cv2.putText(frame, "MENU", (mx1 + 130, my1 + 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
                    
                    # Builder button
                    bbx1, bby1 = mx1 + 50, my1 + 100
                    bbx2, bby2 = mx2 - 50, my1 + 150
                    builder_rect = (bbx1, bby1, bbx2, bby2)
                    cv2.rectangle(frame, (bbx1, bby1), (bbx2, bby2), (150, 200, 150), -1)
                    cv2.rectangle(frame, (bbx1, bby1), (bbx2, bby2), (255, 255, 255), 2)
                    cv2.putText(frame, "Play Builder", (bbx1 + 30, bby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                    # Quiz button
                    qbx1, qby1 = mx1 + 50, my1 + 170
                    qbx2, qby2 = mx2 - 50, my1 + 220
                    quiz_rect = (qbx1, qby1, qbx2, qby2)
                    cv2.rectangle(frame, (qbx1, qby1), (qbx2, qby2), (150, 200, 150), -1)
                    cv2.rectangle(frame, (qbx1, qby1), (qbx2, qby2), (255, 255, 255), 2)
                    cv2.putText(frame, "Play Quiz", (qbx1 + 30, qby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                    # Learn button
                    lbx1, lby1 = mx1 + 50, my1 + 240
                    lbx2, lby2 = mx2 - 50, my1 + 290
                    learn_rect = (lbx1, lby1, lbx2, lby2)
                    cv2.rectangle(frame, (lbx1, lby1), (lbx2, lby2), (150, 200, 150), -1)
                    cv2.rectangle(frame, (lbx1, lby1), (lbx2, lby2), (255, 255, 255), 2)
                    cv2.putText(frame, "Play Learn", (lbx1 + 30, lby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                    # Exit button hitbox inside menu
                    bx1, by1 = mx1 + 50, my1 + 310
                    bx2, by2 = mx2 - 50, my1 + 360
                    exit_rect = (bx1, by1, bx2, by2)
                    
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (100, 100, 150), -1)
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
                    cv2.putText(frame, "Return to Hub", (bx1 + 30, by1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                # Cursor processing
                cursor_pos_norm = gestures.get('cursor_pos')
                if cursor_pos_norm:
                    cx = int(cursor_pos_norm[0] * w)
                    cy = int(cursor_pos_norm[1] * h)
                    
                    is_pinching = gestures.get('select', False)
                    cursor_color = (150, 0, 255) if is_pinching else (0, 0, 255)
                    
                    if self.menu_open:
                        # Process Menu Hover/Click
                        ex1, ey1, ex2, ey2 = exit_rect
                        if (ex1 - 15) < cx < (ex2 + 15) and (ey1 - 15) < cy < (ey2 + 15):
                            cv2.rectangle(frame, (ex1, ey1), (ex2, ey2), (150, 150, 200), -1)
                            cv2.putText(frame, "Return to Hub", (ex1 + 30, ey1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                exit_clicked = True
                                
                        bbx1, bby1, bbx2, bby2 = builder_rect
                        if (bbx1 - 15) < cx < (bbx2 + 15) and (bby1 - 15) < cy < (bby2 + 15):
                            cv2.rectangle(frame, (bbx1, bby1), (bbx2, bby2), (180, 230, 180), -1)
                            cv2.putText(frame, "Play Builder", (bbx1 + 30, bby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.game_mode = 'BUILDER'
                                self.menu_open = False
                                self.pinch_cooldown = 15

                        qbx1, qby1, qbx2, qby2 = quiz_rect
                        if (qbx1 - 15) < cx < (qbx2 + 15) and (qby1 - 15) < cy < (qby2 + 15):
                            cv2.rectangle(frame, (qbx1, qby1), (qbx2, qby2), (180, 230, 180), -1)
                            cv2.putText(frame, "Play Quiz", (qbx1 + 30, qby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.game_mode = 'QUIZ'
                                self.quiz_state = 'SELECT_LEVEL'
                                self.menu_open = False
                                self.pinch_cooldown = 15

                        lbx1, lby1, lbx2, lby2 = learn_rect
                        if (lbx1 - 15) < cx < (lbx2 + 15) and (lby1 - 15) < cy < (lby2 + 15):
                            cv2.rectangle(frame, (lbx1, lby1), (lbx2, lby2), (180, 230, 180), -1)
                            cv2.putText(frame, "Play Learn", (lbx1 + 30, lby1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.game_mode = 'LEARN'
                                self.learn_number = None
                                self.menu_open = False
                                self.pinch_cooldown = 15
                    else:
                        # Process normal Game UI Hover/Click
                        
                        # ----- QUIZ MODE CLICKS -----
                        if self.game_mode == 'QUIZ':
                            if self.quiz_state == 'SELECT_LEVEL':
                                for lvl in level_rects:
                                    x1, y1, x2, y2 = lvl['rect']
                                    if (x1 - 15) < cx < (x2 + 15) and (y1 - 15) < cy < (y2 + 15):
                                        cv2.rectangle(frame, (x1, y1), (x2, y2), (220, 240, 255), -1)
                                        cv2.putText(frame, f"Level {lvl['val'][1]}", (x1 + 20, y1 + 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (50, 50, 255), 3)
                                        hit_btn = lvl['val']
                                        break
                                if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                    if hit_btn and hit_btn.startswith('L'):
                                        self.quiz_level = int(hit_btn[1])
                                        self.quiz_state = 'PLAY'
                                        self.quiz_eq = None
                                        self.quiz_input = ""
                                        self.pinch_cooldown = 15
                            elif self.quiz_state == 'PLAY':
                                # Update feedback timer
                                if self.quiz_feedback_timer > 0:
                                    self.quiz_feedback_timer -= 1
                                    if self.quiz_feedback_timer == 0:
                                        if self.quiz_feedback == 'WRONG':
                                            self.quiz_feedback = 'NONE'
                                            
                                # Check Operators
                                for op in op_rects:
                                    x1, y1, x2, y2 = op['rect']
                                    if (x1 - 15) < cx < (x2 + 15) and (y1 - 15) < cy < (y2 + 15):
                                        cv2.rectangle(frame, (x1, y1), (x2, y2), (220, 255, 255), -1)
                                        cv2.putText(frame, op['val'], (x1 + (op_w - cv2.getTextSize(op['val'], cv2.FONT_HERSHEY_DUPLEX, 2.0, 3)[0][0])//2, y1 + (op_h + cv2.getTextSize(op['val'], cv2.FONT_HERSHEY_DUPLEX, 2.0, 3)[0][1])//2), cv2.FONT_HERSHEY_DUPLEX, 2.0, (50, 50, 255), 3)
                                        hit_btn = op['val']
                                        break
                                # Check Numbers and DEL
                                if not hit_btn:
                                    for num in num_rects:
                                        x1, y1, x2, y2 = num['rect']
                                        if (x1 - 15) < cx < (x2 + 15) and (y1 - 15) < cy < (y2 + 15):
                                            if num['val'] in self.number_images:
                                                render_img = cv2.resize(self.number_images[num['val']], (int(80 * 1.2), int(80 * 1.2)))
                                                off_x = x1 - int(80 * 0.1)
                                                off_y = y1 - int(80 * 0.1)
                                                overlay_image_alpha(frame, render_img, off_x, off_y)
                                            else:
                                                cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 255, 200), -1)
                                            hit_btn = num['val']
                                            break
                                            
                                if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                    if self.quiz_feedback == 'CORRECT':
                                        # Pinch anywhere generates next equation
                                        self.generate_quiz(self.quiz_level, self.quiz_eq['op'])
                                        self.pinch_cooldown = 15
                                    elif hit_btn:
                                        self.pinch_cooldown = 15
                                        if hit_btn in ['+', '-', 'x', '/']:
                                            self.generate_quiz(self.quiz_level, hit_btn)
                                        elif hit_btn == 'DEL' and self.quiz_input:
                                            self.quiz_input = self.quiz_input[:-1]
                                            self.quiz_feedback = None
                                        elif hit_btn == 'CHECK':
                                            if self.quiz_eq is not None and self.quiz_input != "":
                                                try:
                                                    if int(self.quiz_input) == self.quiz_eq['ans']:
                                                        self.quiz_feedback = 'CORRECT'
                                                    else:
                                                        self.quiz_feedback = 'WRONG'
                                                        self.quiz_feedback_timer = 40 # Show RED briefly
                                                except ValueError:
                                                    self.quiz_feedback = 'WRONG'
                                                    self.quiz_feedback_timer = 40
                                        elif hit_btn.isdigit():
                                            if self.quiz_eq is not None and len(self.quiz_input) < 10:
                                                self.quiz_input += hit_btn
                                                self.quiz_feedback = None

                        
                        # ----- BUILDER MODE CLICKS -----
                        elif self.game_mode == 'BUILDER':
                            hit_btn = None
                            # Hover effects for numbers
                            num_width = 80
                            num_height = 80
                            for num in num_rects:
                                nx1, ny1, nx2, ny2 = num['rect']
                                if (nx1 - 15) < cx < (nx2 + 15) and (ny1 - 15) < cy < (ny2 + 15):
                                    if num['val'] in self.number_images:
                                        # pop out effect
                                        render_img = cv2.resize(self.number_images[num['val']], (int(num_width * 1.2), int(num_height * 1.2)))
                                        off_x = nx1 - int(num_width * 0.1)
                                        off_y = ny1 - int(num_height * 0.1)
                                        overlay_image_alpha(frame, render_img, off_x, off_y)
                                    else:
                                        # Fallback hover
                                        cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (150, 180, 150), -1)
                                        text_size = cv2.getTextSize(num['val'], cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
                                        tx = nx1 + (num_width - text_size[0]) // 2
                                        ty = ny1 + (num_height + text_size[1]) // 2
                                        cv2.putText(frame, num['val'], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 3)
                                    hit_btn = num['val']
                            
                            # Hover effects for operators
                            op_width = 100
                            op_height = 100
                            for op in op_rects:
                                ox1, oy1, ox2, oy2 = op['rect']
                                if (ox1 - 15) < cx < (ox2 + 15) and (oy1 - 15) < cy < (oy2 + 15):
                                    bg_color = (150, 200, 255)
                                    text_color = (0, 0, 150)
                                    if op['val'] == '=':
                                        bg_color = (150, 255, 150)
                                        text_color = (0, 150, 0)
                                    elif op['val'] == 'DEL':
                                        bg_color = (150, 150, 255)
                                        text_color = (0, 0, 200)
                                    
                                    cv2.rectangle(frame, (ox1, oy1), (ox2, oy2), bg_color, -1)
                                    
                                    f_scale = 1.2 if op['val'] == 'DEL' else 2.0
                                    thick = 3 if op['val'] == 'DEL' else 4
                                    text_size = cv2.getTextSize(op['val'], cv2.FONT_HERSHEY_DUPLEX, f_scale, thick)[0]
                                    tx = ox1 + (op_width - text_size[0]) // 2
                                    ty = oy1 + (op_height + text_size[1]) // 2
                                    
                                    cv2.putText(frame, op['val'], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, f_scale, text_color, thick)
                                    hit_btn = op['val']

                            # Handle Clicks
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                if self.anim_state == 'SHOW_RESULT':
                                    self.anim_state = 'IDLE'
                                    self.result = None
                                    self.equation = []
                                    self.pinch_cooldown = 15
                                elif hit_btn is not None:
                                    self.pinch_cooldown = 15
                                    if hit_btn == '=':
                                        has_op = any(op in ['+', '-', 'x', '/'] for op in self.equation)
                                        if self.equation and has_op and self.equation[-1] not in ['+', '-', 'x', '/']: 
                                            self.anim_state = 'SHRINKING'
                                            self.anim_scale = 1.0
                                    elif hit_btn == 'DEL':
                                        if self.equation:
                                            self.equation.pop()
                                    elif hit_btn in ['+', '-', 'x', '/']:
                                        has_op = any(op in ['+', '-', 'x', '/'] for op in self.equation)
                                        if not has_op and len(self.equation) > 0:
                                            self.equation.append(hit_btn)
                                    else:
                                        has_op = False
                                        num_before = 0
                                        num_after = 0
                                        for item in self.equation:
                                            if item in ['+', '-', 'x', '/']:
                                                has_op = True
                                            else:
                                                if has_op:
                                                    num_after += 1
                                                else:
                                                    num_before += 1
                                        if not has_op and num_before < 3:
                                            self.equation.append(hit_btn)
                                        elif has_op and num_after < 3:
                                            self.equation.append(hit_btn)

                        # ----- LEARN MODE CLICKS -----
                        elif self.game_mode == 'LEARN':
                            hit_btn = None
                            for num in num_rects:
                                nx1, ny1, nx2, ny2 = num['rect']
                                if (nx1 - 15) < cx < (nx2 + 15) and (ny1 - 15) < cy < (ny2 + 15):
                                    cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), (220, 255, 220), -1)
                                    text_size = cv2.getTextSize(num['val'], cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
                                    tx = nx1 + ((nx2-nx1) - text_size[0]) // 2
                                    ty = ny1 + ((ny2-ny1) + text_size[1]) // 2
                                    cv2.putText(frame, num['val'], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 100, 0), 3)
                                    hit_btn = num['val']
                                    break
                                    
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                if hit_btn:
                                    self.pinch_cooldown = 15
                                    if hit_btn.isdigit():
                                        self.learn_number = int(hit_btn)
                                    elif hit_btn == 'EN':
                                        if self.learn_number is not None:
                                            try:
                                                en_names = {0: "0", 1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09"}
                                                fname = f"en_num_{en_names[self.learn_number]}.mp3"
                                                base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'en_num', fname)
                                                
                                                from pygame import mixer
                                                if not mixer.get_init(): mixer.init()
                                                
                                                if os.path.exists(base_path):
                                                    mixer.music.load(base_path)
                                                    mixer.music.play()
                                                else:
                                                    print(f"File not found: {base_path}")
                                            except Exception as e:
                                                print(f"EN Audio Error: {e}")
                                    elif hit_btn == 'FR':
                                        if self.learn_number is not None:
                                            try:
                                                fr_names = {0: "Zero", 1: "Un", 2: "Deux", 3: "Trois", 4: "Quatre", 5: "Cinq", 6: "Six", 7: "Sept", 8: "Huit", 9: "Neuf"}
                                                fname = f"{fr_names[self.learn_number]}.mp3"
                                                base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fr_n', fname)
                                                
                                                from pygame import mixer
                                                if not mixer.get_init(): mixer.init()
                                                
                                                if os.path.exists(base_path):
                                                    mixer.music.load(base_path)
                                                    mixer.music.play()
                                                else:
                                                    print(f"File not found: {base_path}")
                                            except Exception as e:
                                                print(f"FR Audio Error: {e}")
                    # Draw hand landmarks
                    self.hand_detector.draw_landmarks(frame, hands_data)
                    
                    # Draw cursor
                    cv2.circle(frame, (cx, cy), 8, cursor_color, -1)
                    
                    self.was_pinching = is_pinching
                else:
                    # Draw hand landmarks even if no cursor
                    self.hand_detector.draw_landmarks(frame, hands_data)
                    self.was_pinching = False

                # Display frame
                cv2.imshow(self.window_name, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or exit_clicked:
                    print("\nExiting Mathic, returning to Hub...")
                    break
        
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up Mathic...")
        if not getattr(self, 'shared_resources', False):
            self.hand_detector.cleanup()
            self.camera.release()
            cv2.destroyAllWindows()
        print("Goodbye from Mathic!")

if __name__ == "__main__":
    app = Mathic()
    app.run()