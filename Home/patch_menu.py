import os
import re

filepath = r'c:\Users\DELL 7540\Desktop\MusicalMe\Mathic\mathic_game.py'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

menu_draw = '''                    menu_w, menu_h = 400, 400
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
                    cv2.putText(frame, "Return to Hub", (bx1 + 30, by1 + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)'''

menu_click = '''                    if self.menu_open:
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
                                self.pinch_cooldown = 15'''

text = re.sub(r'                    menu_w, menu_h = 400, 300.*?cv2\.putText\(frame, "Return to Hub", \(bx1 \+ 30, by1 \+ 40\), cv2\.FONT_HERSHEY_DUPLEX, 0\.8, \(255, 255, 255\), 2\)', menu_draw, text, flags=re.DOTALL)
text = re.sub(r'                    if self\.menu_open:.*?self\.pinch_cooldown = 15', menu_click, text, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

