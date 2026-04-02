"""
Menu system with gesture-based navigation and smooth animations
"""
import cv2
import numpy as np
from config import (
    MENU_ITEMS, MENU_WIDTH, MENU_HEIGHT, CURSOR_RADIUS,
    CAMERA_WIDTH, CAMERA_HEIGHT
)


class MenuSystem:
    def __init__(self, ui_renderer, audio_engine):
        """
        Initialize menu system
        
        Args:
            ui_renderer: UIRenderer instance
            audio_engine: AudioEngine instance
        """
        self.ui_renderer = ui_renderer
        self.audio_engine = audio_engine
        self.is_open = False
        self.current_menu = 'main'
        self.selected_index = 0
        self.pinch_cooldown = 0  # Prevent multiple selections
        self.frame_cooldown = 0  # Prevent menu toggle spam
        
        # Animation state
        self.menu_alpha = 0.0  # For smooth fade in/out
        self.target_alpha = 0.0
        self.selected_y_offset = 0  # For smooth selection animation
        self.target_selected_index = 0
        
    def update(self, gestures):
        """
        Update menu state based on gestures
        
        Args:
            gestures: Dictionary from GestureRecognizer
        """
        # Decrease cooldowns
        if self.frame_cooldown > 0:
            self.frame_cooldown -= 1
        
        # Handle menu toggle with frame gesture (with cooldown)
        if gestures['menu_open'] and self.frame_cooldown == 0:
            if self.is_open:
                self.close_menu()
            else:
                self.open_menu()
            self.frame_cooldown = 30  # ~1 second cooldown at 30 FPS
        
        # Smooth animation for menu alpha
        if self.is_open and self.menu_alpha < 1.0:
            self.menu_alpha = min(1.0, self.menu_alpha + 0.15)  # Smooth fade in
        elif not self.is_open and self.menu_alpha > 0.0:
            self.menu_alpha = max(0.0, self.menu_alpha - 0.15)  # Smooth fade out
        
        # Handle menu interactions when open
        if self.is_open:
            # Update cursor position and selection
            if gestures['cursor_pos']:
                self._update_selection(gestures['cursor_pos'])
            
            # Handle selection with cooldown
            if self.pinch_cooldown > 0:
                self.pinch_cooldown -= 1
            
            if gestures['select'] and self.pinch_cooldown == 0:
                self._handle_selection()
                self.pinch_cooldown = 15  # ~0.5 second cooldown at 30 FPS
    
    def open_menu(self):
        """Open the menu with animation"""
        self.is_open = True
        self.current_menu = 'main'
        self.selected_index = 0
        self.target_alpha = 1.0
    
    def close_menu(self):
        """Close the menu with animation"""
        self.is_open = False
        self.target_alpha = 0.0
    
    def _update_selection(self, cursor_pos):
        """
        Update selected menu item based on cursor position
        
        Args:
            cursor_pos: (x, y) normalized position (0-1)
        """
        # Convert normalized position to screen coordinates
        x = int(cursor_pos[0] * CAMERA_WIDTH)
        y = int(cursor_pos[1] * CAMERA_HEIGHT)
        
        # Get menu position
        menu_x = (CAMERA_WIDTH - MENU_WIDTH) // 2
        menu_y = (CAMERA_HEIGHT - MENU_HEIGHT) // 2
        
        # Check if cursor is within menu bounds
        if (menu_x < x < menu_x + MENU_WIDTH and 
            menu_y < y < menu_y + MENU_HEIGHT):
            
            # Calculate which item is selected based on Y position
            items = MENU_ITEMS[self.current_menu]
            item_height = MENU_HEIGHT // (len(items) + 1)
            
            relative_y = y - menu_y
            item_index = relative_y // item_height - 1
            
            if 0 <= item_index < len(items):
                self.selected_index = item_index
    
    def _handle_selection(self):
        """Handle selection of current menu item"""
        items = MENU_ITEMS[self.current_menu]
        selected_item = items[self.selected_index]
        
        if self.current_menu == 'main':
            if selected_item == 'Instruments':
                self.current_menu = 'instruments'
                self.selected_index = 0
            elif selected_item == 'Colors':
                self.current_menu = 'colors'
                self.selected_index = 0
            elif selected_item == 'Exit':
                self.close_menu()
        
        elif self.current_menu == 'instruments':
            if selected_item == 'Back':
                self.current_menu = 'main'
                self.selected_index = 0
            else:
                self.audio_engine.set_instrument(selected_item)
        
        elif self.current_menu == 'colors':
            if selected_item == 'Back':
                self.current_menu = 'main'
                self.selected_index = 0
            else:
                self.ui_renderer.set_color_scheme(selected_item)
    
    def render(self, frame, cursor_pos=None):
        """
        Render the menu on the frame with smooth animations
        
        Args:
            frame: Frame to render on
            cursor_pos: (x, y) normalized cursor position
        """
        if self.menu_alpha <= 0.0:
            return
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        
        # Menu position (centered)
        menu_x = (CAMERA_WIDTH - MENU_WIDTH) // 2
        menu_y = (CAMERA_HEIGHT - MENU_HEIGHT) // 2
        
        # Draw rounded rectangle for menu background
        menu_bg_color = self.ui_renderer.colors['menu_bg'][:3]  # RGB only
        
        # Draw shadow for depth
        shadow_offset = 8
        cv2.rectangle(overlay,
                     (menu_x + shadow_offset, menu_y + shadow_offset),
                     (menu_x + MENU_WIDTH + shadow_offset, menu_y + MENU_HEIGHT + shadow_offset),
                     (0, 0, 0), -1)
        
        # Draw main menu background
        cv2.rectangle(overlay, 
                     (menu_x, menu_y),
                     (menu_x + MENU_WIDTH, menu_y + MENU_HEIGHT),
                     menu_bg_color, -1)
        
        # Blend with original frame using animated alpha
        alpha = 0.9 * self.menu_alpha
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw modern border with glow effect
        border_color = self.ui_renderer.colors['menu_highlight']
        for thickness in [6, 4, 2]:
            alpha_factor = (7 - thickness) / 7.0
            color = tuple(int(c * alpha_factor) for c in border_color)
            cv2.rectangle(frame,
                         (menu_x, menu_y),
                         (menu_x + MENU_WIDTH, menu_y + MENU_HEIGHT),
                         color, thickness)
        
        # Draw menu title with modern style
        title = self.current_menu.capitalize()
        title_y = menu_y + 60
        
        # Title shadow
        self.ui_renderer.draw_text(frame, title, 
                                   (menu_x + 22, title_y + 2),
                                   font_scale=1.5, 
                                   color=(0, 0, 0),
                                   thickness=3)
        # Title main
        self.ui_renderer.draw_text(frame, title, 
                                   (menu_x + 20, title_y),
                                   font_scale=1.5, 
                                   color=self.ui_renderer.colors['menu_highlight'],
                                   thickness=3)
        
        # Draw separator line
        sep_y = menu_y + 90
        cv2.line(frame,
                (menu_x + 20, sep_y),
                (menu_x + MENU_WIDTH - 20, sep_y),
                border_color, 2)
        
        # Draw menu items with smooth animations
        items = MENU_ITEMS[self.current_menu]
        item_height = (MENU_HEIGHT - 120) // (len(items) if len(items) > 0 else 1)
        
        for i, item in enumerate(items):
            item_y = menu_y + 120 + i * item_height
            
            # Smooth selection animation
            if i == self.selected_index:
                # Highlight with gradient effect
                highlight_color = self.ui_renderer.colors['menu_highlight']
                
                # Draw selection background with rounded corners effect
                padding = 15
                cv2.rectangle(frame,
                            (menu_x + padding, item_y - 35),
                            (menu_x + MENU_WIDTH - padding, item_y + 15),
                            highlight_color, -1)
                
                # Draw inner glow
                cv2.rectangle(frame,
                            (menu_x + padding + 2, item_y - 33),
                            (menu_x + MENU_WIDTH - padding - 2, item_y + 13),
                            tuple(min(255, c + 30) for c in highlight_color), 2)
                
                text_color = (255, 255, 255)
                font_scale = 0.9
            else:
                text_color = self.ui_renderer.colors['menu_text']
                font_scale = 0.75
            
            # Draw item text with shadow for depth
            # Shadow
            self.ui_renderer.draw_text(frame, item,
                                       (menu_x + 32, item_y + 2),
                                       font_scale=font_scale,
                                       color=(0, 0, 0),
                                       thickness=2)
            # Main text
            self.ui_renderer.draw_text(frame, item,
                                       (menu_x + 30, item_y),
                                       font_scale=font_scale,
                                       color=text_color,
                                       thickness=2)
        
        # Draw cursor if position is available
        if cursor_pos and self.is_open:
            cursor_x = int(cursor_pos[0] * CAMERA_WIDTH)
            cursor_y = int(cursor_pos[1] * CAMERA_HEIGHT)
            
            cursor_color = self.ui_renderer.colors['menu_highlight']
            
            # Outer glow
            cv2.circle(frame, (cursor_x, cursor_y), 
                      CURSOR_RADIUS + 4, cursor_color, 2)
            # Main cursor
            cv2.circle(frame, (cursor_x, cursor_y), 
                      CURSOR_RADIUS, cursor_color, -1)
            # Inner highlight
            cv2.circle(frame, (cursor_x, cursor_y), 
                      CURSOR_RADIUS - 3, (255, 255, 255), -1)
