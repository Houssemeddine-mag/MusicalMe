"""
UI rendering for camera feed, decorative elements, and visual feedback
"""
import cv2
import numpy as np
from config import (
    CAMERA_WIDTH, CAMERA_HEIGHT, RING_THICKNESS, RING_MARGIN,
    COLOR_SCHEMES, DEFAULT_COLOR_SCHEME, NUM_PITCH_ZONES,
    PITCH_ZONE_LABELS, PITCH_ZONE_COLORS
)


class UIRenderer:
    def __init__(self):
        """Initialize UI renderer"""
        self.color_scheme = DEFAULT_COLOR_SCHEME
        self.colors = COLOR_SCHEMES[self.color_scheme]
        
    def render_frame(self, frame, hands_data, active_notes, menu_visible=False):
        """
        Render the main UI frame with camera feed and decorative elements
        
        Args:
            frame: Camera frame (BGR)
            hands_data: List of detected hands
            active_notes: List of currently playing notes
            menu_visible: Boolean indicating if menu is open
            
        Returns:
            Rendered frame
        """
        # Flip frame horizontally for mirror effect (easier to use)
        frame = cv2.flip(frame, 1)
        
        # Draw pitch zone lines (only when not in menu)
        if not menu_visible:
            self._draw_pitch_zones(frame)
        
        # Draw decorative ring border
        self._draw_ring_border(frame)
        
        # Draw active note indicators
        if active_notes:
            self._draw_note_indicators(frame, active_notes)
        
        return frame
    
    def _draw_ring_border(self, frame):
        """
        Draw decorative ring border around the screen
        
        Args:
            frame: Frame to draw on
        """
        h, w = frame.shape[:2]
        color = self.colors['ring']
        
        # Draw border as hollow rectangle (just the outline, not filled!)
        # Top border
        cv2.rectangle(frame, 
                     (RING_MARGIN, RING_MARGIN),
                     (w - RING_MARGIN, RING_MARGIN + RING_THICKNESS),
                     color, -1)
        
        # Bottom border
        cv2.rectangle(frame,
                     (RING_MARGIN, h - RING_MARGIN - RING_THICKNESS),
                     (w - RING_MARGIN, h - RING_MARGIN),
                     color, -1)
        
        # Left border
        cv2.rectangle(frame,
                     (RING_MARGIN, RING_MARGIN),
                     (RING_MARGIN + RING_THICKNESS, h - RING_MARGIN),
                     color, -1)
        
        # Right border
        cv2.rectangle(frame,
                     (w - RING_MARGIN - RING_THICKNESS, RING_MARGIN),
                     (w - RING_MARGIN, h - RING_MARGIN),
                     color, -1)
    
    def _draw_pitch_zones(self, frame):
        """
        Draw horizontal pitch zone lines
        
        Args:
            frame: Frame to draw on
        """
        h, w = frame.shape[:2]
        
        # Calculate zone height
        zone_height = h / NUM_PITCH_ZONES
        
        # Draw horizontal lines for each zone
        for i in range(NUM_PITCH_ZONES + 1):
            y = int(i * zone_height)
            
            color = (255, 255, 255) if i == NUM_PITCH_ZONES // 2 else (200, 200, 200)
            thickness = 2 if i == NUM_PITCH_ZONES // 2 else 1
            
            # Draw solid visible line
            cv2.line(frame, (RING_MARGIN + RING_THICKNESS + 10, y), 
                    (w - RING_MARGIN - RING_THICKNESS - 10, y), 
                    color, thickness)
        
        # Draw zone labels on the right side
        for i in range(NUM_PITCH_ZONES):
            y = int(i * zone_height + zone_height / 2)
            label = PITCH_ZONE_LABELS[i]
            zone_color = PITCH_ZONE_COLORS[i]
            
            # Background for label
            label_x = w - RING_MARGIN - RING_THICKNESS - 80
            cv2.rectangle(frame, 
                         (label_x, y - 15),
                         (label_x + 60, y + 15),
                         zone_color, -1)
            
            # Label text
            cv2.putText(frame, label, (label_x + 10, y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    def _draw_note_indicators(self, frame, active_notes):
        """
        Draw visual indicators for active notes
        
        Args:
            frame: Frame to draw on
            active_notes: List of note names being played
        """
        h, w = frame.shape[:2]
        color = self.colors['note_indicator']
        
        # Display notes at the top of screen
        y_pos = 50
        x_start = w // 2 - 100
        
        for i, note in enumerate(active_notes):
            x_pos = x_start + i * 50
            
            # Draw circle for each note
            cv2.circle(frame, (x_pos, y_pos), 20, color, -1)
            
            # Draw note name
            cv2.putText(frame, note, (x_pos - 15, y_pos + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    def set_color_scheme(self, scheme_name):
        """
        Change the color scheme
        
        Args:
            scheme_name: Name of color scheme ('blue', 'green', 'purple', 'red')
        """
        scheme_lower = scheme_name.lower()
        if scheme_lower in COLOR_SCHEMES:
            self.color_scheme = scheme_lower
            self.colors = COLOR_SCHEMES[scheme_lower]
    
    def draw_text(self, frame, text, position, font_scale=1.0, color=None, thickness=2):
        """
        Draw text on frame with proper styling
        
        Args:
            frame: Frame to draw on
            text: Text string
            position: (x, y) tuple
            font_scale: Size of text
            color: BGR color tuple (uses menu_text color if None)
            thickness: Line thickness
        """
        if color is None:
            color = self.colors['menu_text']
        
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, color, thickness, cv2.LINE_AA)
