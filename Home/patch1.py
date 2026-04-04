import os

filepath = r'c:\Users\DELL 7540\Desktop\MusicalMe\Mathic\mathic_game.py'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Add Pygame init
init_replace = '''
        self.menu_open = False
        self.menu_cooldown = 0

        import pygame
        from pygame import mixer
        try:
            if not pygame.get_init(): pygame.init()
            if not mixer.get_init(): mixer.init()
            self.has_audio = True
        except Exception as e:
            print(f"Audio init error: {e}")
            self.has_audio = False
            
        self.learn_number = None
'''
text = text.replace('''
        self.menu_open = False
        self.menu_cooldown = 0
''', init_replace)

# Add LEARN mode in menu
menu_replace = '''
                    # Mode toggle button
                    mode_btn_text = "Play Builder"
                    if self.game_mode == 'BUILDER': mode_btn_text = "Play Quiz"
                    elif self.game_mode == 'QUIZ': mode_btn_text = "Play Learn"
                    elif self.game_mode == 'LEARN': mode_btn_text = "Play Builder"
                    
                    mbx1, mby1 = mx1 + 50, my1 + 100
'''
text = text.replace('''
                    # Mode toggle button
                    mode_btn_text = "Play Builder" if self.game_mode == 'QUIZ' else "Play Quiz"
                    mbx1, mby1 = mx1 + 50, my1 + 100
''', menu_replace)

menu_click_replace = '''
                        mbx1, mby1, mbx2, mby2 = mode_rect
                        if (mbx1 - 15) < cx < (mbx2 + 15) and (mby1 - 15) < cy < (mby2 + 15):
                            cv2.rectangle(frame, (mbx1, mby1), (mbx2, mby2), (180, 230, 180), -1)
                            cv2.putText(frame, mode_btn_text, (mbx1 + 30, mby1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                if self.game_mode == 'BUILDER':
                                    self.game_mode = 'QUIZ'
                                    self.quiz_state = 'SELECT_LEVEL'
                                elif self.game_mode == 'QUIZ':
                                    self.game_mode = 'LEARN'
                                    self.learn_number = None
                                    op_rects = []
                                    num_rects = []
                                elif self.game_mode == 'LEARN':
                                    self.game_mode = 'BUILDER'
                                self.menu_open = False
                                self.pinch_cooldown = 15
'''

text = text.replace('''
                        mbx1, mby1, mbx2, mby2 = mode_rect
                        if (mbx1 - 15) < cx < (mbx2 + 15) and (mby1 - 15) < cy < (mby2 + 15):
                            cv2.rectangle(frame, (mbx1, mby1), (mbx2, mby2), (180, 230, 180), -1)
                            cv2.putText(frame, mode_btn_text, (mbx1 + 30, mby1 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                            
                            if is_pinching and not self.was_pinching and self.pinch_cooldown == 0:
                                self.game_mode = 'QUIZ' if self.game_mode == 'BUILDER' else 'BUILDER'
                                self.quiz_state = 'SELECT_LEVEL'
                                self.menu_open = False
                                self.pinch_cooldown = 15
''', menu_click_replace)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

