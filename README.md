# MusicalMe 🎵

Hand Gesture Controlled Music System

## Overview

MusicalMe is an interactive music system that uses your camera to detect hand gestures and play musical notes. Create music with simple hand movements - no physical instruments required!

## Features

- **8 Musical Notes**: Control notes using thumb + finger combinations
- **Pitch Bending**: Move your hand up/down while playing to change pitch
- **Multi-Note Support**: Play multiple notes simultaneously for chords
- **4 Instruments**: Piano (default), Guitar, Synthesizer, and Flute
- **Customizable UI**: Choose from 4 color schemes
- **Gesture-Based Menu**: Navigate menus using hand gestures

## Installation

### Requirements

- Python 3.8 or higher
- Webcam
- Windows, macOS, or Linux

### Quick Start (Windows)

**IMPORTANT: Use the virtual environment to avoid dependency conflicts!**

1. **Double-click `setup_venv.bat`** - This creates an isolated environment and installs all dependencies (takes 2-3 minutes)
2. **Double-click `run.bat`** - This launches MusicalMe

That's it! 🎉

### Manual Installation (Advanced Users)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Gesture Controls

### Playing Notes

**Left Hand:**

- Thumb + Pinky = **DO** (C)
- Thumb + Ring Finger = **RE** (D)
- Thumb + Middle Finger = **MI** (E)
- Thumb + Index Finger = **FA** (F)

**Right Hand:**

- Thumb + Index Finger = **SOL** (G)
- Thumb + Middle Finger = **LA** (A)
- Thumb + Ring Finger = **SI** (B)
- Thumb + Pinky = **DO** (C - higher octave)

### Advanced Features

- **Sustain**: Keep fingers touching to sustain the note
- **Pitch Bend**: Move your hand up (higher pitch) or down (lower pitch) while playing
- **Chords**: Use both hands to play multiple notes together

### Menu Navigation

- **Open/Close Menu**: Raise both pinkies (both hands with pinky finger extended)
- **Move Cursor**: Point with your index finger
- **Select Item**: Touch thumb and index finger together (pinch gesture)

## Menu Options

### Instruments

- Piano (warm, harmonic sound)
- Guitar (bright, percussive sound)
- Synthesizer (electronic, square wave)
- Flute (soft, pure tone with vibrato)

### Colors

- Blue (default)
- Green
- Purple
- Red

## Controls

- **Q key**: Quit the application

## Technical Details

- **Hand Tracking**: MediaPipe (detects 21 landmarks per hand)
- **Audio Synthesis**: Pygame with NumPy for real-time waveform generation
- **Video Processing**: OpenCV for camera feed
- **Frame Rate**: 30 FPS for smooth gesture detection
- **Isolated Environment**: Virtual environment prevents conflicts with other Python packages

## Project Structure

```
MusicalMe/
├── main.py                 # Main application
├── hand_detector.py        # Hand tracking with MediaPipe
├── gesture_recognizer.py   # Gesture classification
├── audio_engine.py         # Sound synthesis
├── ui_renderer.py          # UI rendering
├── menu_system.py          # Menu logic
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── setup_venv.bat          # Virtual environment installer (RUN THIS FIRST!)
├── run.bat                 # Application launcher
└── README.md               # This file
```

## Tips for Best Results

1. **Lighting**: Use good lighting for better hand detection
2. **Camera Position**: Position yourself 1-2 feet from the camera
3. **Background**: Plain backgrounds work best
4. **Gestures**: Make clear, deliberate gestures
5. **Calibration**: The system adapts to your hand size automatically

## Troubleshooting

**Dependency conflicts:**

- Always use `setup_venv.bat` and `run.bat` instead of running `python main.py` directly
- This creates an isolated environment that won't interfere with TensorFlow or other packages

**Camera not detected:**

- Check if another application is using the camera
- Update `CAMERA_INDEX` in `config.py` (try 0, 1, or 2)

**Hand detection issues:**

- Ensure good lighting
- Try adjusting `DETECTION_CONFIDENCE` in `config.py`

**Audio issues:**

- Make sure your audio drivers are up to date
- Check volume settings

**"Virtual environment not found" error:**

- Run `setup_venv.bat` first before using `run.bat`

## Why Virtual Environment?

If you have TensorFlow or other packages installed globally, they may conflict with MediaPipe's requirements. The virtual environment (venv) creates an isolated space for MusicalMe's dependencies, so:

- ✅ MusicalMe works perfectly
- ✅ Your other Python projects remain unaffected
- ✅ No version conflicts

## License

Created for educational and creative purposes.

## Enjoy Making Music! 🎶
