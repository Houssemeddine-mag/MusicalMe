import os

filepath = r'c:\Users\DELL 7540\Desktop\MusicalMe\Mathic\mathic_game.py'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

learn_draw_replace = '''
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
'''

text = text.replace('''
                # Decrease cooldowns
''', learn_draw_replace)

learn_click_replace = '''
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
                                    elif hit_btn == 'EN' and self.has_audio:
                                        try:
                                            base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'en_n', f"{self.learn_number}.mp3")
                                            if os.path.exists(base_path):
                                                pygame.mixer.music.load(base_path)
                                                pygame.mixer.music.play()
                                        except Exception as e:
                                            print(e)
                                    elif hit_btn == 'FR' and self.has_audio:
                                        try:
                                            base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fr_n', f"{self.learn_number}.mp3")
                                            if os.path.exists(base_path):
                                                pygame.mixer.music.load(base_path)
                                                pygame.mixer.music.play()
                                        except Exception as e:
                                            print(e)

                    # Draw hand landmarks
'''

text = text.replace('''
                    # Draw hand landmarks
''', learn_click_replace)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

