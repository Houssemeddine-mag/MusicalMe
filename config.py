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
PINCH_THRESHOLD = 0.04  # Threshold for pinch gesture

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
    (100, 255, 100),  # Green (+2)
    (150, 255, 150),  # Light green (+1)
    (255, 255, 255),  # White (0)
    (255, 200, 150),  # Light orange (-1)
    (255, 150, 100)   # Orange (-2)
]
PITCH_BEND_SEMITONES = 2  # ±2 semitones for pitch bending

# Instrument waveform types
INSTRUMENTS = {
    'Piano': 'piano',
    'Guitar': 'guitar',
    'Synthesizer': 'square',
    'Flute': 'flute'
}

# Default settings
DEFAULT_INSTRUMENT = 'Piano'
DEFAULT_COLOR_SCHEME = 'blue'

# UI color schemes
COLOR_SCHEMES = {
    'blue': {
        'ring': (100, 150, 255),
        'menu_bg': (20, 30, 60, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (100, 150, 255),
        'note_indicator': (100, 200, 255)
    },
    'green': {
        'ring': (100, 255, 150),
        'menu_bg': (20, 60, 30, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (100, 255, 150),
        'note_indicator': (100, 255, 200)
    },
    'purple': {
        'ring': (200, 100, 255),
        'menu_bg': (40, 20, 60, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (200, 100, 255),
        'note_indicator': (220, 150, 255)
    },
    'red': {
        'ring': (255, 100, 100),
        'menu_bg': (60, 20, 20, 200),
        'menu_text': (255, 255, 255),
        'menu_highlight': (255, 100, 100),
        'note_indicator': (255, 150, 150)
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
    'main': ['Instruments', 'Colors', 'Exit'],
    'instruments': ['Piano', 'Guitar', 'Synthesizer', 'Flute', 'Back'],
    'colors': ['Blue', 'Green', 'Purple', 'Red', 'Back']
}
