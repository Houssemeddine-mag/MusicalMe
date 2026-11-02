# MusicalMe 🎵

**A gesture-controlled learning suite for kids — play music, practice math, and draw, all with your hands.**

MusicalMe turns a webcam into the only controller a child needs. Wave, point, pinch, and
draw in the air; MediaPipe reads your hands, OpenCV draws the world, and Pygame makes the
sound. No keyboard, no mouse, no touchscreen — and no internet connection.

> 📘 For the full architecture, module APIs, tuning guide, and technical debt, see
> **[documentation.md](documentation.md)**.

---

## Table of contents

- [What's inside](#whats-inside)
- [Quick start](#quick-start)
- [Gesture cheat sheet](#gesture-cheat-sheet)
- [App descriptions](#app-descriptions)
- [Why this project is good](#why-this-project-is-good)
- [Future perspectives](#future-perspectives)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## What's inside

`run.bat` opens the **Kids Play & Learn Hub** — a full-screen launcher with big, friendly
tiles. Point at a tile and pinch to open it; pinch the exit icon (or press `q`) to leave.

| Activity | What it teaches | Highlights |
| --- | --- | --- |
| 🎹 **MusicalMe** | Music, rhythm, coordination | 8 notes, chords, 5 pitch zones, 4 instruments, 4 color themes |
| ➗ **Mathic** | Arithmetic and number recognition | Equation builder, 4-level quiz, English/French pronunciation |
| 🎨 **YouDraw** | Creativity and fine motor control | 10-color palette, 5 brush sizes, fist eraser, clear canvas |
| 🏠 **Hub** | Independence and navigation | Gesture-only app switching with one shared camera |

Three of the hub tiles — Alphabet, TheZoo, and CarRoad — are visible placeholders for
future activities.

---

## Quick start

### Windows (recommended)

1. **Double-click `setup_venv.bat`** — creates an isolated environment and installs all
   pinned dependencies (about 2–3 minutes).
2. **Double-click `run.bat`** — launches the hub.

That's it. 🎉

> Always use `run.bat` rather than `python main.py` directly: it guarantees the isolated
> environment, which avoids conflicts with globally installed TensorFlow/MediaPipe builds.

### Manual installation

```bash
python -m venv venv
venv\Scripts\activate.bat        # Windows
source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
python Home/hub.py               # full hub
```

**Requirements:** Python 3.8+, a webcam, speakers, and a desktop session for OpenCV windows.

### Run a single activity

```bash
python MusicalMe_App/main.py     # music only
python Mathic/mathic_game.py     # math only
python YouDraw/youdraw_game.py   # drawing only
```

---

## Gesture cheat sheet

### Playing notes (MusicalMe)

| Left hand | Note | Right hand | Note |
| --- | --- | --- | --- |
| Thumb + Pinky | **DO** (C4) | Thumb + Index | **SOL** (G4) |
| Thumb + Ring | **RE** (D4) | Thumb + Middle | **LA** (A4) |
| Thumb + Middle | **MI** (E4) | Thumb + Ring | **SI** (B4) |
| Thumb + Index | **FA** (F4) | Thumb + Pinky | **DO** (C5) |

- **Sustain** — keep the two fingers touching.
- **Chords** — use both hands at the same time (up to 8 notes).
- **Pitch** — the screen is split into 5 bands: hand high = **+2** semitones, hand low =
  **−2** semitones, middle = no shift.

### Everywhere

| Gesture | Action |
| --- | --- |
| Point with index finger | Move the cursor |
| Touch thumb + index (pinch) | Select / click |
| Pinky up, other fingers curled | Open or close the menu |
| Press `q` | Quit the current app |

### Mathic and YouDraw extras

| Gesture | Mathic | YouDraw |
| --- | --- | --- |
| Pinch | Tap buttons, enter digits, check answers | Tap palette, brush buttons, menu |
| Index + middle glued together | — | Draw |
| Closed fist | — | Erase (40 px circle) |
| Index only | — | Choose color or brush size |

---

## App descriptions

### 🏠 The Hub

A single full-screen launcher built on one camera feed and one hand-tracking model.
Hovered tiles pop out to 110% and use generous 30 px hitboxes, because small hands are not
precise. Every activity receives the hub's live camera and detector, so switching apps is
nearly instant instead of restarting the webcam and MediaPipe model. The hub flushes stale
frames on return so a lingering pinch cannot re-open the app you just left.

### 🎹 MusicalMe

The flagship activity. Eight notes are mapped to thumb-to-fingertip touches, split across
both hands, so chords are natural. Vertical hand position selects one of five discrete pitch
zones (±2 semitones, equal temperament) — discrete zones were chosen over continuous bending
because they are far more predictable for children. Four instruments are available:

- **Piano** — real MP3 samples with rich sustain
- **Guitar** — real MP3 samples with natural decay
- **Synthesizer** — detuned square wave
- **Flute** — sine wave with vibrato and breath noise

Pitch changes are produced by resampling the samples with NumPy and caching the result, so
even ±2 semitones stay responsive. The in-app menu (Instruments, Colors, Return to Hub) is
driven by the same index-finger cursor and pinch used everywhere else.

### ➗ Mathic

Three distinct learning modes behind one gesture menu:

- **Builder** — assemble an equation from digits and `+ − x /`, then watch it shrink and the
  answer pop in green.
- **Quiz** — four difficulty levels with clean, integer-friendly questions; correct answers
  turn green, wrong ones turn red, and a pinch brings the next equation.
- **Learn** — a large number card for each digit 0–9, with **English** and **Français**
  pronunciation buttons.

Digit artwork (`numbers/*.png`) and recorded pronunciations (`en_num/`, `fr_n/`) make the
mode usable by pre-readers.

### 🎨 YouDraw

A gesture painting app with a real canvas model: strokes are composited through a mask, so
drawings sit cleanly over the camera image. The draw pose is index + middle fingers held
together — pointing with one finger selects colors and brush sizes without painting by
accident. Fast motion is interpolated so lines stay smooth, brush width is applied as both a
line and end-caps, and a closed fist becomes a 40 px eraser. The pinky menu offers
**Clear Canvas** and **Return to Hub**.

---

## Why this project is good

**For children**

- **No physical controller** — accessible for kids who struggle with mice, keyboards, or
  gamepads, and motivating for kids who do not.
- **Large targets and forgiving hitboxes** — 30 px padding, 110% hover pop-outs, and
  cooldowns tuned for imprecise movement.
- **Immediate feedback** — sound on touch, color on hover, green/red quiz feedback, live
  drawing.
- **Multiple intelligences** — music, logic, and art in one place, with bilingual number
  audio.
- **Safe and offline** — no accounts, no ads, no network traffic, no data leaves the machine.

**For developers and educators**

- **Clean separation of concerns** — vision, gesture rules, audio, UI, menus, and activities
  live in separate modules with narrow interfaces.
- **One shared camera pipeline** — the hub injects camera + detector + recognizer into each
  activity, cutting startup cost and hardware contention.
- **No model training** — gestures are geometric rules over 21 landmarks, so behavior is
  inspectable, debuggable, and tunable with a single constant.
- **Graceful degradation** — missing audio files fall back to synthesized waveforms; missing
  logos fall back to drawn rectangles. The app still runs.
- **Easy to extend** — a new activity is one class plus one hub registry entry; a new
  instrument or note is a dictionary edit.
- **Reproducible setup** — pinned dependencies and a one-click environment bootstrap.

**Engineering choices worth noting**

- Discrete pitch zones over continuous bending (predictability for kids).
- Tape-style resampling with a pitch cache (cheap, responsive, musically acceptable at
  ±2 semitones).
- Notes are allowed to ring out after the gesture ends, which feels musical rather than
  robotic.
- Pinch and menu toggles use frame-based cooldowns plus edge detection
  (`is_pinching and not was_pinching`) to avoid double clicks.
- Handedness is computed on a pre-mirrored frame, then the display is mirrored again, so the
  on-screen hand matches the child's real hand.

---

## Future perspectives

**Packaging and distribution**

- Ship a standalone Windows build with PyInstaller (or an installer) so families do not need
  Python at all.
- Add a macOS/Linux launcher (`run.sh`) and CI that verifies imports and asset presence.

**Repository hygiene**

- Add `.gitignore`, remove `venv/` and `__pycache__` from tracking, and move large media to
  Git LFS. This alone would shrink the repository from ~400 MB to a few MB.
- Retire the one-off `Home/patch*.py` scripts (hard-coded paths) or move them to `tools/`.

**Smoother interaction**

- Add One Euro / Kalman smoothing to the cursor for steadier pointing.
- Add a short calibration step (hand size, lighting, dominant hand) and a left-handed mode.
- Support dynamic resolutions instead of fixed 1280×720 coordinates.
- Replace frame-count cooldowns with time-based cooldowns so behavior is consistent on
  faster or slower machines.

**More learning content**

- Complete the **Alphabet**, **TheZoo**, and **CarRoad** tiles.
- Add solfège/note-reading lessons, rhythm exercises, and a "follow the melody" mode.
- Expand Mathic with multiplication tables, fractions, and progress tracking for teachers.
- Add more languages to the number pronunciation system.

**Musical depth**

- Record and replay performances; export to MIDI or WAV.
- Add more instruments and velocity control (hand distance → volume).
- Visualize chords and note history on screen.

**Accessibility**

- Voice prompts and audio cues for every button.
- High-contrast and large-text UI modes.
- Support for single-hand use and reduced-motion settings.
- Optional keyboard fallback so the suite is usable without a camera.

**Robustness**

- Unit tests for gesture geometry, pitch mapping, and quiz generation.
- Safe arithmetic parsing in Mathic instead of `eval()`.
- Structured logging and a startup self-check for camera, audio, and assets.
- Frame pacing and optional threaded camera capture to reduce latency.

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Hand tracking | MediaPipe Hands (21 landmarks, 2 hands) |
| Video I/O and drawing | OpenCV (`opencv-python`) |
| Audio | Pygame mixer + NumPy synthesis/resampling |
| Numerics | NumPy |
| Language | Python 3.8+ |

Pinned versions:

```
opencv-python==4.8.1.78
mediapipe==0.10.8
pygame==2.5.2
numpy==1.24.3
protobuf==3.20.3
```

---

## Project structure

```
MusicalMe/
├── Home/                  # Hub launcher (entry point: hub.py)
├── MusicalMe_App/         # Music activity + shared vision engine
│   ├── main.py            # MusicalMe app loop
│   ├── hand_detector.py   # MediaPipe wrapper
│   ├── gesture_recognizer.py
│   ├── audio_engine.py
│   ├── ui_renderer.py
│   ├── menu_system.py
│   ├── config.py
│   ├── files/             # Piano samples
│   └── guitare file/      # Guitar samples
├── Mathic/                # Math activity (Builder / Quiz / Learn)
├── YouDraw/               # Drawing activity
├── logos/                 # Hub + Mathic backgrounds, app logos, loading art
├── numbers/               # 0–9 digit artwork
├── en_num/                # English digit audio
├── fr_n/                  # French digit audio
├── requirements.txt
├── setup_venv.bat
├── run.bat
├── QUICK_START.txt
├── README.md
└── documentation.md       # Full technical reference
```

---

## Tips for best results

1. **Lighting** — face a window or lamp; avoid strong backlight.
2. **Distance** — sit 1–2 feet from the camera with both hands in frame.
3. **Background** — a plain wall helps MediaPipe hold tracking.
4. **Deliberate gestures** — touch thumb and finger clearly; hold the pinky pose briefly.
5. **Camera choice** — if the wrong webcam opens, change `CAMERA_INDEX` in
   `MusicalMe_App/config.py` to `1` or `2`.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Virtual environment not found` | Run `setup_venv.bat` first |
| Dependency conflicts | Never run `python main.py` globally; use `run.bat` |
| Camera not detected | Close other camera apps; try `CAMERA_INDEX` 1 or 2 |
| Hand not detected | Improve lighting; lower `DETECTION_CONFIDENCE` to 0.6 |
| Notes trigger accidentally | Lower `FINGER_TOUCH_THRESHOLD` to 0.04 |
| Menu opens by itself | Raise the pinky threshold in `hand_detector.is_finger_extended` |
| No sound | Check output device and volume; verify the MP3 folders exist |
| Audio crackles | Raise `AUDIO_BUFFER_SIZE` to 4096 |
| Windows do not appear (Linux) | Install `libgl1`, SDL2, and PortAudio packages |

More detail is in **[documentation.md](documentation.md)** §14–§15.

---

## License

Created for educational and creative purposes.

## Enjoy making music! 🎶
