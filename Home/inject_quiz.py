import sys

def main():
    path = r'c:\Users\DELL 7540\Desktop\MusicalMe\Mathic\mathic_game.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the menu to have mode toggle
    menu_old = '''                    # Exit button hitbox inside menu
                    bx1, by1 = mx1 + 50, my1 + 120
                    bx2, by2 = mx2 - 50, my1 + 220
                    exit_rect = (bx1, by1, bx2, by2)
                    
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (100, 100, 150), -1)
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
                    cv2.putText(frame, "Return to Hub", (bx1 + 10, by1 + 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)'''

    menu_new = '''                    # Mode toggle button
                    mode_btn_text = "Play Builder" if self.game_mode == 'QUIZ' else "Play Quiz"
                    mbx1, mby1 = mx1 + 50, my1 + 100
                    mbx2, mby2 = mx2 - 50, my1 + 160
                    mode_rect = (mbx1, mby1, mbx2, mby2)
                    
                    cv2.rectangle(frame, (mbx1, mby1), (mbx2, mby2), (150, 200, 150), -1)
                    cv2.rectangle(frame, (mbx1, mby1), (mbx2, mby2), (255, 255, 255), 2)
                    cv2.putText(frame, mode_btn_text, (mbx1 + 30, mby1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

                    # Exit button hitbox inside menu
                    bx1, by1 = mx1 + 50, my1 + 180
                    bx2, by2 = mx2 - 50, my1 + 240
                    exit_rect = (bx1, by1, bx2, by2)
                    
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (100, 100, 150), -1)
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 2)
                    cv2.putText(frame, "Return to Hub", (bx1 + 30, by1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)'''
    content = content.replace(menu_old, menu_new)

    # 2. Process menu hover/click updates for mode toggle
    menu_click_old = '''                        if (ex1 - 15) < cx < (ex2 + 15) and (ey1 - 15) < cy < (ey2 + 15):
                            cv2.rectangle(frame, (ex1, ey1), (ex2, ey2), (150, 150, 200), -1)
                            cv2.putText(frame, "Return to Hub", (ex1 + 10, ey1 + 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                exit_clicked = True'''

    menu_click_new = '''                        if (ex1 - 15) < cx < (ex2 + 15) and (ey1 - 15) < cy < (ey2 + 15):
                            cv2.rectangle(frame, (ex1, ey1), (ex2, ey2), (150, 150, 200), -1)
                            cv2.putText(frame, "Return to Hub", (ex1 + 30, ey1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                exit_clicked = True
                                
                        mbx1, mby1, mbx2, mby2 = mode_rect
                        if (mbx1 - 15) < cx < (mbx2 + 15) and (mby1 - 15) < cy < (mby2 + 15):
                            cv2.rectangle(frame, (mbx1, mby1), (mbx2, mby2), (180, 230, 180), -1)
                            cv2.putText(frame, mode_btn_text, (mbx1 + 30, mby1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.game_mode = 'QUIZ' if self.game_mode == 'BUILDER' else 'BUILDER'
                                self.quiz_state = 'SELECT_LEVEL'
                                self.menu_open = False
                                self.pinch_cooldown = 15'''
    content = content.replace(menu_click_old, menu_click_new)

    # 3. Add Quiz UI inside "Process normal Game UI Hover/Click"
    # Actually, we should branch earlier:
    drawing_branch_old = '''                # --- Draw UI ---
                
                # 1. Numbers 0-9 at the top (small)'''

    drawing_branch_new = '''                # --- Draw UI ---
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
                                cv2.putText(frame, "Correct! Pinch numbers for the next equation", (w//2 - 250, h//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 150, 100), 2)

                elif self.game_mode == 'BUILDER':
                    # 1. Numbers 0-9 at the top (small)'''
    content = content.replace(drawing_branch_old, drawing_branch_new)


    builder_process_old = '''                    else:
                        # Process normal Game UI Hover/Click
                        hit_btn = None
                        
                        # Hover effects for numbers'''

    builder_process_new = '''                    else:
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
                                        if hit_btn:
                                            # Pinch anywhere generates next equation
                                            self.generate_quiz(self.quiz_level, self.quiz_eq['op'])
                                            self.pinch_cooldown = 15
                                    elif hit_btn:
                                        self.pinch_cooldown = 15
                                        if hit_btn in ['+', '-', 'x', '/']:
                                            self.generate_quiz(self.quiz_level, hit_btn)
                                        elif hit_btn == 'DEL' and self.quiz_input:
                                            self.quiz_input = self.quiz_input[:-1]
                                        elif hit_btn.isdigit():
                                            if self.quiz_eq is not None and len(self.quiz_input) < 10:
                                                self.quiz_input += hit_btn
                                                
                                                # Auto check answer if length matches the expected answer length
                                                if len(self.quiz_input) >= len(str(self.quiz_eq['ans'])):
                                                    if int(self.quiz_input) == self.quiz_eq['ans']:
                                                        self.quiz_feedback = 'CORRECT'
                                                    else:
                                                        self.quiz_feedback = 'WRONG'
                                                        self.quiz_feedback_timer = 40 # Show RED briefly
                                                        self.quiz_input = ""

                        # ----- BUILDER MODE CLICKS -----
                        elif self.game_mode == 'BUILDER':
                            hit_btn = None
                            # Hover effects for numbers'''
  
    content = content.replace(builder_process_old, builder_process_new)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()