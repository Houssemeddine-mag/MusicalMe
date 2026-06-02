import cv2
import sys
import os
import numpy as np

# Add the MusicalMe app directory to the system path so we can reuse the hand tracking engine natively
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MusicalMe_App'))

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer

class YouDraw:
    def __init__(self, shared_camera=None, shared_hand_detector=None, shared_gesture_recognizer=None, shared_window_name=None):
        """Initialize YouDraw application"""
        print("Initializing YouDraw...")
        
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

        if not self.camera.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)

        # Drawing Canvas
        self.canvas = None
        self.last_draw_pos = None

        # Menu toggle
        self.menu_open = False
        self.menu_cooldown = 0
        self.pinch_cooldown = 0
        self.was_pinching = False
        self.pinch_loss_forgiveness = 0  # To smooth out pinch detection for drawing

        # Colors
        self.current_color = (0, 0, 255) # Default Red in BGR
        self.colors_palette = [
            {'name': 'red', 'val': (0, 0, 255)},
            {'name': 'black', 'val': (0, 0, 0)},
            {'name': 'white', 'val': (255, 255, 255)},
            {'name': 'blue', 'val': (255, 0, 0)},
            {'name': 'green', 'val': (0, 255, 0)},
            {'name': 'brown', 'val': (42, 42, 165)},
            {'name': 'pink', 'val': (203, 192, 255)},
            {'name': 'yellow', 'val': (0, 255, 255)},
            {'name': 'purple', 'val': (128, 0, 128)},
            {'name': 'orange', 'val': (0, 165, 255)}
        ]
        
        # Brush size scale (1-5, default 3)
        self.brush_size = 3
        self.brush_scale = [8, 12, 16, 20, 24]  # Pixel sizes for scales 1-5

    def run(self):
        """Main application loop"""
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Detect hands FIRST (since hand_detector actually mirrors the frame internally for detection)
                hands_data = self.hand_detector.detect_hands(frame)
                gestures = self.gesture_recognizer.recognize_gestures(hands_data)

                # Flip frame for mirror effect (so drawing aligns with hands_data)
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape

                # Initialize canvas if None
                if self.canvas is None:
                    self.canvas = np.zeros_like(frame)

                # Check for pinky up (Menu toggle)
                is_pinky_up = gestures.get('menu_open', False)
                if is_pinky_up and self.menu_cooldown == 0:
                    self.menu_open = not self.menu_open
                    self.menu_cooldown = 15 # Delay to avoid rapidly opening/closing

                if self.menu_cooldown > 0:
                    self.menu_cooldown -= 1
                if self.pinch_cooldown > 0:
                    self.pinch_cooldown -= 1

                exit_clicked = False
                clear_clicked = False
                
                if self.menu_open:
                    menu_w, menu_h = 400, 300
                    mx1 = (w - menu_w) // 2
                    my1 = (h - menu_h) // 2
                    mx2 = mx1 + menu_w
                    my2 = my1 + menu_h
                    
                    # Darken background slightly
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (mx1, my1), (mx2, my2), (50, 50, 60), -1)
                    cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
                    cv2.rectangle(frame, (mx1, my1), (mx2, my2), (200, 200, 255), 4)
                    
                    cv2.putText(frame, "MENU", (mx1 + 140, my1 + 60), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)

                    # Clear canvas button
                    cx1, cy1 = mx1 + 50, my1 + 120
                    cx2, cy2 = mx2 - 50, my1 + 170
                    clear_rect = (cx1, cy1, cx2, cy2)
                    
                    cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (100, 150, 100), -1)
                    cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (255, 255, 255), 2)
                    cv2.putText(frame, "Clear Canvas", (cx1 + 50, cy1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                    # Exit button hitbox inside menu
                    bx1, by1 = mx1 + 50, my1 + 200
                    bx2, by2 = mx2 - 50, my1 + 250
                    exit_rect = (bx1, by1, bx2, by2)
                    
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (100, 100, 150), -1)
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
                    cv2.putText(frame, "Return to Hub", (bx1 + 50, by1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                # Merge canvas onto the frame
                # Where the canvas is not black, overwrite the frame
                canvas_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
                frame = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
                frame = cv2.bitwise_or(frame, self.canvas)

                # Draw color palette at the top (horizontal)
                color_rects = []
                palette_y = 10
                palette_x_start = 50
                box_size = 40
                spacing = 5
                
                for idx, color_info in enumerate(self.colors_palette):
                    rect_x = palette_x_start + idx * (box_size + spacing)
                    color_rects.append({
                        'color': color_info['val'],
                        'rect': (rect_x, palette_y, rect_x + box_size, palette_y + box_size)
                    })
                    # Draw filled rectangle
                    cv2.rectangle(frame, (rect_x, palette_y), (rect_x + box_size, palette_y + box_size), color_info['val'], -1)
                    # Draw outline
                    outline_color = (255, 255, 255) if color_info['name'] == 'black' else (0, 0, 0)
                    if self.current_color == color_info['val']:
                        cv2.rectangle(frame, (rect_x - 5, palette_y - 5), (rect_x + box_size + 5, palette_y + box_size + 5), (255, 255, 255), 3)
                        cv2.rectangle(frame, (rect_x - 5, palette_y - 5), (rect_x + box_size + 5, palette_y + box_size + 5), (0, 0, 0), 1)
                    cv2.rectangle(frame, (rect_x, palette_y), (rect_x + box_size, palette_y + box_size), outline_color, 2)

                # Draw brush size scale at the top right (simplified, child-friendly)
                brush_scale_rects = []
                brush_x_start = w - 300
                brush_y = 10
                btn_size = 35
                spacing = 8
                
                # Color progression for scale
                scale_colors = [(100, 100, 255), (100, 200, 255), (0, 255, 255), (255, 200, 0), (255, 0, 0)]
                current_color = scale_colors[self.brush_size - 1]
                
                # Draw minus button
                minus_rect = (brush_x_start, brush_y, brush_x_start + btn_size, brush_y + btn_size)
                brush_scale_rects.append({'action': 'minus', 'rect': minus_rect})
                cv2.rectangle(frame, (brush_x_start, brush_y), (brush_x_start + btn_size, brush_y + btn_size), (80, 80, 80), -1)
                cv2.rectangle(frame, (brush_x_start, brush_y), (brush_x_start + btn_size, brush_y + btn_size), (180, 180, 180), 2)
                cv2.putText(frame, "-", (brush_x_start + 8, brush_y + 25), cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2)
                
                # Draw single number display box
                display_x = brush_x_start + btn_size + spacing
                # Just display the colored number without a box
                cv2.putText(frame, str(self.brush_size), (display_x, brush_y + 28), cv2.FONT_HERSHEY_DUPLEX, 1.8, current_color, 3)
                cv2.putText(frame, str(self.brush_size), (display_x, brush_y + 28), cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 1)
                
                # Draw plus button
                plus_x = display_x + btn_size + spacing
                plus_rect = (plus_x, brush_y, plus_x + btn_size, brush_y + btn_size)
                brush_scale_rects.append({'action': 'plus', 'rect': plus_rect})
                cv2.rectangle(frame, (plus_x, brush_y), (plus_x + btn_size, brush_y + btn_size), (80, 80, 80), -1)
                cv2.rectangle(frame, (plus_x, brush_y), (plus_x + btn_size, brush_y + btn_size), (180, 180, 180), 2)
                cv2.putText(frame, "+", (plus_x + 8, brush_y + 25), cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2)
                
                # Draw elegant clear button
                clear_x = plus_x + btn_size + spacing
                clear_rect = (clear_x, brush_y, clear_x + btn_size + 5, brush_y + btn_size)
                brush_scale_rects.append({'action': 'clear', 'rect': clear_rect})
                # Gradient-like effect with red
                cv2.rectangle(frame, (clear_x, brush_y), (clear_x + btn_size + 5, brush_y + btn_size), (30, 100, 220), -1)  # Red/orange in BGR
                cv2.rectangle(frame, (clear_x, brush_y), (clear_x + btn_size + 5, brush_y + btn_size), (100, 200, 255), 3)  # Bright border
                # Draw simple "C" for clear
                cv2.putText(frame, "C", (clear_x + 5, brush_y + 27), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)

                cursor_pos_norm = gestures.get('cursor_pos')
                is_fist = False
                fist_pos = None
                is_drawing = False
                index_only_extended = False  # For color selection only

                # Detect hand gestures
                if hands_data:
                    for hand_data in hands_data:
                        landmarks = hand_data['landmarks']
                        idx_ext = self.hand_detector.is_finger_extended(landmarks, 'Index')
                        mid_ext = self.hand_detector.is_finger_extended(landmarks, 'Middle')
                        rng_ext = self.hand_detector.is_finger_extended(landmarks, 'Ring')
                        pnk_ext = self.hand_detector.is_finger_extended(landmarks, 'Pinky')
                        
                        if not idx_ext and not mid_ext and not rng_ext and not pnk_ext:
                            is_fist = True
                            fist_pos = (int(hand_data['hand_center'][0] * w), int(hand_data['hand_center'][1] * h))
                            break
                        
                        # Gesture 1: Index finger alone extended (color selection only, no drawing)
                        if idx_ext and not mid_ext and not rng_ext and not pnk_ext:
                            index_only_extended = True
                            break
                        
                        # Gesture 2: Index and Middle are both extended AND glued together (drawing enabled)
                        if idx_ext and mid_ext:
                            idx_tip = self.hand_detector.get_finger_tip(landmarks, 'Index')
                            mid_tip = self.hand_detector.get_finger_tip(landmarks, 'Middle')
                            dist = self.hand_detector.calculate_distance(idx_tip, mid_tip)
                            if dist < 0.035: # Fingers glued together
                                is_drawing = True
                            break

                if is_fist and fist_pos:
                    fcx, fcy = fist_pos
                    # Draw a white circle strictly on the display frame to represent the eraser
                    cv2.circle(frame, (fcx, fcy), 40, (255, 255, 255), 3)
                    cv2.circle(frame, (fcx, fcy), 40, (200, 200, 200), -1) # Slightly gray-white inside
                    # Erase by drawing black on the canvas
                    cv2.circle(self.canvas, (fcx, fcy), 40, (0, 0, 0), -1)
                    self.last_draw_pos = None

                elif cursor_pos_norm:
                    cx = int(cursor_pos_norm[0] * w)
                    cy = int(cursor_pos_norm[1] * h)
                    
                    cursor_color = (150, 0, 255) if is_drawing else (0, 0, 255)
                    
                    # Get pinch gesture for menu interactions
                    is_pinching = gestures.get('select', False)

                    if self.menu_open:
                        # Process Menu Hover/Click (still uses pinch for safety)
                        ex1, ey1, ex2, ey2 = exit_rect
                        if (ex1 - 15) < cx < (ex2 + 15) and (ey1 - 15) < cy < (ey2 + 15):
                            cv2.rectangle(frame, (ex1, ey1), (ex2, ey2), (150, 150, 200), -1)
                            cv2.putText(frame, "Return to Hub", (ex1 + 50, ey1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                exit_clicked = True
                                self.pinch_cooldown = 15

                        cx1, cy1, cx2, cy2 = clear_rect
                        if (cx1 - 15) < cx < (cx2 + 15) and (cy1 - 15) < cy < (cy2 + 15):
                            cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (150, 200, 150), -1)
                            cv2.putText(frame, "Clear Canvas", (cx1 + 50, cy1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.canvas = np.zeros_like(frame)
                                self.menu_open = False
                                self.pinch_cooldown = 15
                    else:
                        # Normal drawing mode
                        hit_palette = False
                        hit_brush_btn = False
                        
                        # Check brush size buttons first
                        for btn_rect in brush_scale_rects:
                            bx1, by1, bx2, by2 = btn_rect['rect']
                            if (bx1 - 10) < cx < (bx2 + 10) and (by1 - 10) < cy < (by2 + 10):
                                # Hover glow
                                cv2.rectangle(frame, (bx1 - 5, by1 - 5), (bx2 + 5, by2 + 5), (255, 200, 100), 2)
                                
                                # Handle clicks
                                if index_only_extended and self.pinch_cooldown == 0:
                                    if btn_rect['action'] == 'minus' and self.brush_size > 1:
                                        self.brush_size -= 1
                                        self.pinch_cooldown = 15
                                    elif btn_rect['action'] == 'plus' and self.brush_size < 5:
                                        self.brush_size += 1
                                        self.pinch_cooldown = 15
                                    elif btn_rect['action'] == 'clear':
                                        self.canvas = np.zeros_like(frame)
                                        self.pinch_cooldown = 15
                                hit_brush_btn = True
                                break
                        
                        # Check palette hovering
                        if not hit_brush_btn:
                            for col_rect in color_rects:
                                px1, py1, px2, py2 = col_rect['rect']
                                if (px1 - 15) < cx < (px2 + 15) and (py1 - 15) < cy < (py2 + 15):
                                    # Hover glow
                                    cv2.rectangle(frame, (px1 - 5, py1 - 5), (px2 + 5, py2 + 5), (200, 200, 200), 2)
                                    # Select color when index is extended (alone or glued) - just by hovering
                                    if (index_only_extended or is_drawing) and self.pinch_cooldown == 0:
                                        self.current_color = col_rect['color']
                                        self.pinch_cooldown = 15
                                    hit_palette = True
                                    break

                        if not hit_palette:
                            if is_drawing:
                                # Drawing logic - ONLY when both fingers are glued together
                                brush_width = self.brush_scale[self.brush_size - 1]  # Get size based on scale
                                
                                if self.last_draw_pos is not None:
                                    # For smooth drawing, interpolate between points when movement is fast
                                    dx = cx - self.last_draw_pos[0]
                                    dy = cy - self.last_draw_pos[1]
                                    distance = (dx**2 + dy**2) ** 0.5
                                    
                                    # If movement is large, add intermediate points
                                    if distance > 15:
                                        steps = int(distance / 10) + 1
                                        for i in range(1, steps + 1):
                                            t = i / (steps + 1)
                                            ix = int(self.last_draw_pos[0] + dx * t)
                                            iy = int(self.last_draw_pos[1] + dy * t)
                                            cv2.circle(self.canvas, (ix, iy), max(2, brush_width // 4), self.current_color, -1)
                                    
                                    # Draw main line with brush size
                                    cv2.line(self.canvas, self.last_draw_pos, (cx, cy), self.current_color, brush_width)
                                    # Add circles at both ends for smoothness
                                    cv2.circle(self.canvas, self.last_draw_pos, max(2, brush_width // 3), self.current_color, -1)
                                    cv2.circle(self.canvas, (cx, cy), max(2, brush_width // 3), self.current_color, -1)
                                else:
                                    # Just a dot when starting
                                    cv2.circle(self.canvas, (cx, cy), max(2, brush_width // 3), self.current_color, -1)
                                self.last_draw_pos = (cx, cy)
                            else:
                                self.last_draw_pos = None

                    # Draw hand landmarks
                    self.hand_detector.draw_landmarks(frame, hands_data)
                    
                    # Draw cursor
                    cv2.circle(frame, (cx, cy), 8, cursor_color, -1)
                    
                    self.was_pinching = is_pinching
                else:
                    self.last_draw_pos = None
                    self.hand_detector.draw_landmarks(frame, hands_data)
                    self.was_pinching = False

                cv2.imshow(self.window_name, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or exit_clicked:
                    print("\nExiting YouDraw, returning to Hub...")
                    break

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up YouDraw...")
        if not getattr(self, 'shared_resources', False):
            self.hand_detector.cleanup()
            self.camera.release()
            cv2.destroyAllWindows()
        print("Goodbye from YouDraw!")

if __name__ == "__main__":
    app = YouDraw()
    app.run()
