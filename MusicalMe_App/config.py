"""
Configuration and constants for the Hand Gesture Music System
"""

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS = 30

# Hand detection settings
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7
MAX_HANDS = 2

# Gesture detection thresholds
FINGER_TOUCH_THRESHOLD = 0.05  # Normalized distance for finger touching
PINCH_THRESHOLD = 0.04  # Threshold for pinch gesture (lowered to require actual touch/pinch)

# Musical note frequencies (Hz)
NOTE_FREQUENCIES = {
    'DO': 261.63,   # C4
    'RE': 293.66,   # D4
    'MI': 329.63,   # E4
    'FA': 349.23,   # F4
    'SOL': 392.00,  # G4
    'LA': 440.00,   # A4
    'SI': 493.88,   # B4
    'DO_HIGH': 523.25  # C5
}

# Note gesture mapping
# Format: (hand, finger) -> note_name
# hand: 'Left' or 'Right'
# finger: 'Index', 'Middle', 'Ring', 'Pinky'
NOTE_GESTURES = {
    ('Left', 'Pinky'): 'DO',
    ('Left', 'Ring'): 'RE',
    ('Left', 'Middle'): 'MI',
    ('Left', 'Index'): 'FA',
    ('Right', 'Index'): 'SOL',
    ('Right', 'Middle'): 'LA',
    ('Right', 'Ring'): 'SI',
    ('Right', 'Pinky'): 'DO_HIGH'
}

# Audio settings
SAMPLE_RATE = 44100
AUDIO_BUFFER_SIZE = 2048
MAX_ACTIVE_NOTES = 8

# Pitch zone settings
NUM_PITCH_ZONES = 5  # Number of discrete pitch zones
PITCH_ZONE_LABELS = ['+2', '+1', '0', '-1', '-2']  # Semitone offsets
PITCH_ZONE_COLORS = [
    (150, 255, 150),  # Soft Green (+2) (BGR format)
    (180, 255, 180),  # Light Mint (+1)
    (240, 240, 240),  # Soft White (0)
    (170, 210, 255),  # Light Peach/Orange (-1)
    (130, 170, 255)   # Coral/Orange (-2)
]
PITCH_BEND_SEMITONES = 2  # ±2 semitones for pitch bending

# Instrument waveform types
INSTRUMENTS = {
    'Piano': 'piano',
    'Guitar': 'guitar',
    'Synthesizer': 'square',
    'Flute': 'flute'
}

import os

# Base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Instrument file paths
INSTRUMENT_FILES = {
    'Piano': {
        'DO': os.path.join(BASE_DIR, 'files', '1_DO.mp3'),
        'RE': os.path.join(BASE_DIR, 'files', '2_RE.mp3'),
        'MI': os.path.join(BASE_DIR, 'files', '3_MI.mp3'),
        'FA': os.path.join(BASE_DIR, 'files', '4_FA.mp3'),
        'SOL': os.path.join(BASE_DIR, 'files', '5_SOL.mp3'),
        'LA': os.path.join(BASE_DIR, 'files', '6_LA.mp3'),
        'SI': os.path.join(BASE_DIR, 'files', '7_SI.mp3'),
        'DO_HIGH': os.path.join(BASE_DIR, 'files', '8_DO_high.mp3')
    },
    'Guitar': {
        'DO': os.path.join(BASE_DIR, 'guitare file', 'DO.mp3'),
        'RE': os.path.join(BASE_DIR, 'guitare file', 'RE.mp3'),
        'MI': os.path.join(BASE_DIR, 'guitare file', 'MI.mp3'),
        'FA': os.path.join(BASE_DIR, 'guitare file', 'FA.mp3'),
        'SOL': os.path.join(BASE_DIR, 'guitare file', 'SOL.mp3'),
        'LA': os.path.join(BASE_DIR, 'guitare file', 'LA.mp3'),
        'SI': os.path.join(BASE_DIR, 'guitare file', 'SI.mp3'),
        'DO_HIGH': os.path.join(BASE_DIR, 'guitare file', 'DO HIGH.mp3')
    }
}

# Default settings
DEFAULT_INSTRUMENT = 'Piano'
DEFAULT_COLOR_SCHEME = 'blue'

# UI color schemes (OpenCV uses BGR format)
COLOR_SCHEMES = {
    'blue': {
        'ring': (255, 180, 100),       # Soft Sky Blue
        'menu_bg': (120, 80, 50, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (255, 200, 150),
        'note_indicator': (255, 220, 180)
    },
    'green': {
        'ring': (150, 220, 150),       # Soft Mint Green
        'menu_bg': (70, 110, 70, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (180, 240, 180),
        'note_indicator': (200, 255, 200)
    },
    'purple': {
        'ring': (230, 150, 200),       # Soft Lavender
        'menu_bg': (110, 60, 90, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (240, 180, 220),
        'note_indicator': (255, 200, 240)
    },
    'red': {
        'ring': (120, 120, 240),       # Soft Coral / Pastel Red
        'menu_bg': (50, 50, 120, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (150, 150, 255),
        'note_indicator': (180, 180, 255)
    }
}

# UI settings
RING_THICKNESS = 20
RING_MARGIN = 10
MENU_WIDTH = 400
MENU_HEIGHT = 500
CURSOR_RADIUS = 15

# Menu items
MENU_ITEMS = {
    'main': ['Instruments', 'Colors', 'Return to Hub'],
    'instruments': ['Piano', 'Guitar', 'Synthesizer', 'Flute', 'Back'],
    'colors': ['Blue', 'Green', 'Purple', 'Red', 'Back']
}
