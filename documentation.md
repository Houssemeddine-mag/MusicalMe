# MusicalMe — Technical Documentation

Complete technical reference for the **MusicalMe / Kids Play & Learn Hub** repository:
architecture, module APIs, data flow, gesture math, audio pipeline, asset inventory,
configuration reference, and known technical debt.

- **Repository:** `https://github.com/Houssemeddine-mag/TechGraden`
- **Branch:** `main`
- **Entry point:** `Home/hub.py` (via `run.bat`)
- **Language:** Python 3.10 (project targets Python 3.8+)
- **Platform:** Windows (primary), macOS/Linux possible with manual setup
- **License:** educational / creative use

---

## 1. What the project is

MusicalMe is a **camera-based, gesture-controlled educational suite for children**. It uses
MediaPipe hand tracking + OpenCV rendering + Pygame audio to turn hand movements into
interaction — no keyboard, mouse, or controller is required at runtime.

The repository is not a single app. It is a **hub** (`EducationalHub`) that hosts four
independent activities that share one camera and one hand-tracking pipeline:

| Module | Folder | Purpose |
| --- | --- | --- |
| **Hub** | `Home/` | Full-screen launcher grid; owns camera + tracking; starts/stops activities |
| **MusicalMe** | `MusicalMe_App/` | Gesture-controlled instrument (8 notes, chords, pitch zones, 4 instruments) |
| **Mathic** | `Mathic/` | Math learning: equation builder, 4-level quiz, number pronunciation |
| **YouDraw** | `YouDraw/` | Gesture painting app (brush, palette, eraser, clear) |

Everything runs **fully offline**. There are no network calls, no accounts, and no telemetry.

---

## 2. High-level architecture

```
                    ┌───────────────────────────────┐
                    │        Home/hub.py            │
                    │      EducationalHub           │
                    │  camera + HandDetector +      │
                    │  GestureRecognizer (shared)   │
                    └───────────────┬───────────────┘
                                    │ constructor injection
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     ┌────────────────┐   ┌──────────────────┐   ┌────────────────┐
     │ MusicalMe_App  │   │   Mathic         │   │   YouDraw      │
     │   MusicalMe    │   │   Mathic         │   │   YouDraw      │
     └───────┬────────┘   └────────┬─────────┘   └───────┬────────┘
             │                     │                     │
             └─────────┬───────────┴─────────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │  Shared vision layer             │
        │  hand_detector.py  (MediaPipe)   │
        │  gesture_recognizer.py (rules)   │
        └──────────────────────────────────┘
```

### Shared-resource injection

Every activity has the same constructor signature:

```python
def __init__(self, shared_camera=None, shared_hand_detector=None,
             shared_gesture_recognizer=None, shared_window_name=None)
```

- If `shared_camera` is not `None`, the activity sets `self.shared_resources = True`
  and **reuses** the hub's `cv2.VideoCapture`, `HandDetector`, and `GestureRecognizer`.
- In `cleanup()`, an activity only releases the camera, closes MediaPipe, and destroys
  windows when `shared_resources` is `False`. This prevents a child activity from killing
  the hub's hardware handles.
- This design makes app switching take ~0.1–0.5 s instead of a full camera + model
  re-initialization (which costs 1–3 s and can fail on some webcams).

Each activity can also run standalone (`python MusicalMe_App/main.py`,
`python Mathic/mathic_game.py`, `python YouDraw/youdraw_game.py`); in that case it
creates its own camera and detector.

### Module resolution

`Home/hub.py`, `Mathic/mathic_game.py`, and `YouDraw/youdraw_game.py` all prepend
`MusicalMe_App/` to `sys.path` so they can `from hand_detector import HandDetector`
without a package install. Imports are **flat module names**, so files must not be
renamed without updating every importer.

---

## 3. Repository structure

```
MusicalMe/
├── Home/                       # Hub / launcher
│   ├── hub.py                  # EducationalHub: grid, hitboxes, launching, shared resources
│   ├── inject_quiz.py          # one-off dev patch script (hard-coded path, not runtime)
│   ├── patch1.py               # one-off dev patch script (adds Mathic LEARN mode)
│   ├── patch2.py               # one-off dev patch script (adds LEARN UI + clicks)
│   ├── patch_menu.py           # one-off dev patch script (rewrites Mathic menu)
│   └── test_paths.py           # diagnostic: verifies number-audio paths exist
│
├── MusicalMe_App/              # Music activity + shared vision engine
│   ├── main.py                 # MusicalMe class + loop (also the shared "app" entry)
│   ├── config.py               # ALL constants: camera, notes, colors, menus, paths
│   ├── hand_detector.py        # MediaPipe wrapper: landmarks, finger state, distances
│   ├── gesture_recognizer.py   # Rule-based gesture → notes/cursor/pinch/pinky
│   ├── audio_engine.py         # Pygame mixer, sample banks, pitch shift, synthesis
│   ├── ui_renderer.py          # Ring border, pitch-zone bands, note indicators
│   ├── menu_system.py          # Gesture-driven in-app menu (Instruments/Colors/Hub)
│   ├── files/                  # Piano samples: 1_DO.mp3 … 8_DO_high.mp3
│   └── guitare file/           # Guitar samples: DO.mp3 … DO HIGH.mp3
│
├── Mathic/
│   └── mathic_game.py          # Mathic class: BUILDER, QUIZ, LEARN modes
│
├── YouDraw/
│   └── youdraw_game.py         # YouDraw class: canvas, palette, brush, eraser
│
├── logos/                      # Hub background, app logos, loading + exit art
│   ├── BG.png                  # Hub background (1280×720)
│   ├── BG_Mathical.png         # Mathic background
│   ├── Loading.png             # Loading splash overlay (alpha)
│   ├── MusicalMe_logo.png, Mathic_logo.png, YouDraw_logo.png
│   ├── Alphabet_logo.png, TheZoo_logo.png, Carroad_logo.png  (placeholders, not wired)
│   └── Exit.png
│
├── numbers/                    # 0.png … 9.png — Mathic digit artwork (80×80 tiles)
├── en_num/                     # English digit pronunciations (en_num_0.mp3, en_num_01.mp3 …)
├── fr_n/                       # French digit pronunciations (Zero.mp3 … Neuf.mp3)
│
├── venv/                       # Committed virtual environment (see §11)
├── requirements.txt            # Pinned dependencies
├── setup_venv.bat              # Creates venv + installs pins (Windows)
├── run.bat                     # Activates venv and runs Home/hub.py
├── QUICK_START.txt             # Plain-text quick start
├── README.md                   # User-facing overview
└── documentation.md            # This file
```

---

## 4. Runtime data flow (one frame)

The same loop shape is used by the hub and by every activity:

```
camera.read()
   │  BGR frame (requested 1280×720 @30 FPS)
   ▼
HandDetector.detect_hands(frame)
   │  • cv2.flip(frame, 1)          # mirror BEFORE detection
   │  • BGR → RGB
   │  • MediaPipe Hands.process()
   ▼
hands_data: [ { landmarks[21]=(x,y,z) normalized,
                handedness: 'Left'|'Right',
                hand_center: (mean_x, mean_y),
                raw_landmarks } , ... ]        # max 2 hands
   ▼
GestureRecognizer.recognize_gestures(hands_data)
   ▼
gestures: { notes: [ {note, hand_y, hand} ],
            menu_open: bool,
            menu_close: bool,        # currently identical to menu_open
            cursor_pos: (x, y) | None,
            select: bool }           # pinch
   ▼
Activity logic  ──►  AudioEngine / Mathic state / YouDraw canvas
   ▼
Rendering: frame = cv2.flip(frame, 1)  # mirror for display
           activity UI → menu overlay → landmarks → cursor
   ▼
cv2.imshow(window_name, frame)
cv2.waitKey(1)   # 'q' quits
```

**Important detail:** `detect_hands()` already flips the frame internally for detection, but
returns coordinates in that flipped space. Activities therefore flip the raw frame again
before drawing, so the overlay aligns with the mirrored camera image the child sees.
Do not remove either flip independently.

---

## 5. Vision layer

### 5.1 `HandDetector` (`MusicalMe_App/hand_detector.py`)

| Method | Behavior |
| --- | --- |
| `__init__()` | Builds `mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=MAX_HANDS, min_detection_confidence, min_tracking_confidence)` |
| `detect_hands(frame)` | Flips frame, converts BGR→RGB, runs MediaPipe, returns list of hand dicts |
| `draw_landmarks(frame, hands_data)` | Draws the 21-point skeleton + connections |
| `get_finger_tip(landmarks, name)` | Tip indices: Thumb 4, Index 8, Middle 12, Ring 16, Pinky 20 |
| `get_thumb_tip(landmarks)` | Landmark 4 |
| `calculate_distance(p1, p2)` | 3D Euclidean distance in normalized space |
| `is_finger_extended(landmarks, name)` | See rule below |
| `cleanup()` | `hands.close()` |

**Finger extension rule**

- Thumb: distance(tip 4, base 2) > `0.1`.
- Other fingers: `tip_y < mid_y − threshold`, where `mid` is the PIP joint
  (Index 6, Middle 10, Ring 14, Pinky 18) and threshold is `0.06` for the pinky,
  `0.02` for the rest. The larger pinky threshold prevents accidental menu toggles.

### 5.2 `GestureRecognizer` (`MusicalMe_App/gesture_recognizer.py`)

| Gesture | Rule | Output |
| --- | --- | --- |
| Note | 3D distance(thumb tip, finger tip) < `FINGER_TOUCH_THRESHOLD` (0.05) → lookup `NOTE_GESTURES[(hand, finger)]` | `notes[]` with `hand_y` = palm center Y |
| Cursor | Index extended → index tip | `cursor_pos` (normalized) |
| Select | distance(thumb, index) < `PINCH_THRESHOLD` (0.04) | `select = True` |
| Menu toggle | Pinky extended **and** index/middle/ring all curled | `menu_open` |

**Note map** (`config.NOTE_GESTURES`)

| Hand | Finger | Note | Frequency |
| --- | --- | --- | --- |
| Left | Pinky | DO | 261.63 Hz (C4) |
| Left | Ring | RE | 293.66 Hz (D4) |
| Left | Middle | MI | 329.63 Hz (E4) |
| Left | Index | FA | 349.23 Hz (F4) |
| Right | Index | SOL | 392.00 Hz (G4) |
| Right | Middle | LA | 440.00 Hz (A4) |
| Right | Ring | SI | 493.88 Hz (B4) |
| Right | Pinky | DO_HIGH | 523.25 Hz (C5) |

Multiple notes can be active at once (one per hand per frame + sustain), giving chords.

**Pitch zones** (`get_pitch_zone`)

```
zone   = clamp(int(hand_y * 5), 0, 4)     # 0 = top of frame, 4 = bottom
semis  = 2 - zone                          # +2, +1, 0, -1, -2
factor = 2 ** (semis / 12)                 # equal-temperament ratio
```

`get_pitch_bend_factor()` (continuous ±2 semitone bend around a reference Y) still exists
but is **unused** — the discrete-zone model replaced it for predictability with children.

**Dead / legacy code:** `_detect_frame_gesture()` is defined but never called;
`menu_close` is assigned from `menu_open`.

---

## 6. Audio subsystem (`MusicalMe_App/audio_engine.py`)

### Initialization

```python
mixer.pre_init(SAMPLE_RATE=44100, -16, 2, AUDIO_BUFFER_SIZE=2048)
pygame.init(); mixer.init()
```

### Two sound paths

| Instrument | Source | Playback |
| --- | --- | --- |
| Piano | `MusicalMe_App/files/*.mp3` preloaded with `mixer.Sound` | Natural decay, **no loop** |
| Guitar | `MusicalMe_App/guitare file/*.mp3` preloaded | Natural decay, **no loop** |
| Synthesizer | `generate_waveform(..., 'square')` | 5 s buffer, `loops=-1` |
| Flute | `generate_waveform(..., 'flute')` | 5 s buffer, `loops=-1` |

Missing files degrade gracefully: a warning is printed and the engine falls back to a
generated waveform.

### Pitch shifting of samples

`_get_pitched_sound(note, multiplier)`:

1. If `|multiplier − 1| < 0.01`, return the original sound.
2. Cache key: `(instrument, note, round(multiplier, 3))`.
3. `pygame.sndarray.array(sound)` → new length `L / multiplier` →
   `np.interp` per channel → `int16` → `pygame.sndarray.make_sound`.
4. Errors fall back to the unshifted sound.

This is a tape-style resample (pitch and duration change together), which is musically
acceptable for ±2 semitones and cheap enough for 30 FPS interaction.

### Waveform synthesis

| Instrument | Recipe |
| --- | --- |
| Piano | 5 harmonics (1, 1/2, 1/4, 1/10, 1/20) + slight inharmonic 6th; 95% sustain envelope |
| Guitar | Harmonics 1..7 at `1/h`, +3‰ detuned chorus voice, exponential decay |
| Square | `sign(sin)` + detuned `sign(sin(×1.01))`, scaled 0.6, soft attack/release |
| Flute | Sine + 6 Hz vibrato + Gaussian breath noise, gentle envelope |

All buffers are normalized to ±1, scaled to `int16`, and duplicated to stereo.

### Note lifecycle

- `play_note(note, multiplier, hand_y)` — rejects unknown notes and enforces
  `MAX_ACTIVE_NOTES = 8`. Re-plays only when frequency actually changes (>0.01 Hz).
- `stop_note(note)` — removes tracking state but **intentionally does not cut the sound**
  (comment: "Removed fadeout so the single note completely finishes playing for kids").
- `stop_all_notes()` — clears tracking; used when the menu opens or instrument changes.
- `set_instrument(name)` — maps `Piano/Guitar/Synthesizer/Flute` → internal waveform key and
  stops all notes.

---

## 7. MusicalMe activity (`MusicalMe_App/main.py`)

- `_handle_note_playing(gestures)` diffs the current note set against
  `active_note_gestures`: new notes start with their zone-derived multiplier, vanished notes
  are removed from the active set.
- When the menu is open, all notes stop and note input is suppressed.
- `q` **or** `menu_system.should_exit_app` exits the loop. `should_exit_app` is reset to
  `False` before returning so the hub can relaunch the app later.
- `cleanup()` always quits audio; hardware is only released when resources are not shared.

### In-app menu (`menu_system.py`)

| Property | Value |
| --- | --- |
| Menu size | 400 × 500, centered |
| Toggle cooldown | 30 frames (~1 s) |
| Pinch cooldown | 15 frames (~0.5 s) |
| Fade speed | 0.15 alpha per frame |
| Structure | `main → Instruments / Colors / Return to Hub`; submenus have `Back` |
| Effects | drop shadow, triple-stroke glow border, highlight bar, cursor ring |

Menu navigation: index finger = cursor; pinch = click; pinky-only = open/close.

### UI renderer (`ui_renderer.py`)

- Mirror flip.
- Pitch-zone bands: 5 equal horizontal slices with labels `+2 … −2`; the middle line is
  thicker/white. Hidden while the menu is open.
- Decorative ring border: four filled rectangles of `RING_THICKNESS = 20` inset by
  `RING_MARGIN = 10`.
- Active-note pills: one circle + label per note across the top.
- Color schemes are **BGR** tuples (`blue`, `green`, `purple`, `red`).

---

## 8. Hub (`Home/hub.py`)

`EducationalHub` renders a 1280×720 launcher over `logos/BG.png` with 7 tiles:

| Tile | Position (x, y) | Size | Wired? |
| --- | --- | --- | --- |
| MusicalMe | 100, 140 | 360×240 | ✅ `launch_musical_me()` |
| Mathic | 460, 120 | 360×240 | ✅ `launch_mathic()` |
| Alphabet | 820, 140 | 360×240 | ❌ placeholder |
| YouDraw | 100, 420 | 360×240 | ✅ `launch_youdraw()` |
| TheZoo | 460, 440 | 360×240 | ❌ placeholder |
| CarRoad | 820, 420 | 360×240 | ❌ placeholder |
| Exit | 1150, 30 | 100×100 | ✅ breaks the loop |

Interaction details:

- Cursor from index tip; pinch selects.
- Hitbox padding is **30 px** and hovered logos scale to **110%** (child-friendly targets).
- `hub_cooldown = 45` frames (~1.5 s) after any click to prevent double launches.
- `overlay_image_alpha()` does per-channel alpha blending (handles 3- or 4-channel PNGs).
- Each `launch_*` shows a loading splash, starts the activity with shared resources, then
  sleeps 0.5 s, drains `cv2.waitKey`, and discards 5 camera frames so stale pinch gestures
  do not immediately re-trigger.
- `run.bat` starts this file, so the hub is the true application entry point.

---

## 9. Mathic (`Mathic/mathic_game.py`)

Three modes, switchable from the pinky-triggered menu:

### BUILDER

- Number strip 0–9 at the top, operators `+ − x /` on the right, `=` and `DEL` on the left.
- Max 3 digits before and 3 after the operator; only one operator per equation.
- `=` triggers a shrink animation (`SHRINKING` → `SHOW_RESULT`), then shows the result
  growing in green. Next pinch clears the equation.
- Evaluation: joins tokens, maps `x → *`, strips leading zeros with a regex, then `eval()`
  (the input alphabet is restricted by the UI to digits/operators, so injection surface is
  limited, but a tokenizer would be safer — see §11).

### QUIZ

- Level select (L1–L4) → play screen with operator row, digit row, `DEL`, `Check`.
- Level ranges: L1 `0–9 op 0–9`, L2 `10–99 op 0–9`, L3 `10–99 op 10–99`,
  L4 `100–999 op 0–9`.
- Subtraction swaps operands so `n1 ≥ n2`; division forces `n1 = n1 × n2` so answers are
  integers.
- Correct answer turns green and any pinch generates the next equation; wrong answers turn
  red for 40 frames with "ooh, Try again".

### LEARN

- Digits 0–9 in two columns; selecting one shows a 200×200 card.
- `English` plays `en_num/en_num_XX.mp3`; `Francais` plays `fr_n/<Name>.mp3`.
- Audio uses `mixer.music` (single streaming channel), initialized lazily.

Menu (`MENU`, 400×400) contains **Play Builder / Play Quiz / Play Learn / Return to Hub**;
pinch to activate, `q` to quit.

---

## 10. YouDraw (`YouDraw/youdraw_game.py`)

| Element | Behavior |
| --- | --- |
| Canvas | `np.zeros_like(frame)`; composited with a binary mask (threshold gray > 1) |
| Draw gesture | Index **and** middle extended, tips within `0.035` (fingers "glued") |
| Eraser | Fist (index/middle/ring/pinky all curled); erases a 40 px circle on the canvas |
| Palette | 10 colors (red, black, white, blue, green, brown, pink, yellow, purple, orange) at the top |
| Brush sizes | 1–5 → 8/12/16/20/24 px; `−`/`+`/`C` buttons top-right |
| Color/brush click | Index-only gesture while hovering (no pinch needed) |
| Menu | Pinky toggles 400×300 panel: **Clear Canvas**, **Return to Hub** (pinch) |
| Smoothing | Points interpolated every ~10 px when the hand moves faster than 15 px/frame |
| Cooldowns | 15 frames for menu toggle, pinch, palette and brush clicks |

Drawing is deliberately restricted to the two-finger "glued" pose so that pointing at the
palette does not paint. The index-only pose is the selection pose.

---

## 11. Configuration reference (`MusicalMe_App/config.py`)

| Constant | Value | Notes |
| --- | --- | --- |
| `CAMERA_INDEX` | 0 | Try 1/2 if the wrong webcam opens |
| `CAMERA_WIDTH/HEIGHT` | 1280 × 720 | Hub/Mathic/YouDraw hardcode 1280×720 layout too |
| `FPS` | 30 | Only applied as a camera property; the loop is not frame-capped |
| `DETECTION_CONFIDENCE` | 0.7 | MediaPipe |
| `TRACKING_CONFIDENCE` | 0.7 | MediaPipe |
| `MAX_HANDS` | 2 | Two-hand chords |
| `FINGER_TOUCH_THRESHOLD` | 0.05 | Note gesture |
| `PINCH_THRESHOLD` | 0.04 | Select gesture |
| `SAMPLE_RATE` | 44100 | Mixer |
| `AUDIO_BUFFER_SIZE` | 2048 | Latency vs. stability trade-off |
| `MAX_ACTIVE_NOTES` | 8 | Polyphony cap |
| `NUM_PITCH_ZONES` | 5 | +2 … −2 semitones |
| `PITCH_BEND_SEMITONES` | 2 | Range for the legacy continuous bend |
| `RING_THICKNESS` / `RING_MARGIN` | 20 / 10 | Frame border |
| `MENU_WIDTH` / `MENU_HEIGHT` | 400 / 500 | MusicalMe menu |
| `CURSOR_RADIUS` | 15 | Menu cursor |
| `MENU_ITEMS` | main/instruments/colors | Menu tree |
| `COLOR_SCHEMES` | blue/green/purple/red | BGR tuples |
| `NOTE_FREQUENCIES` | C4–C5 | Equal temperament |
| `INSTRUMENT_FILES` | piano + guitar paths | Declared but unused (audio engine hardcodes) |

---

## 12. Setup, run, and dependencies

### Pinned dependencies (`requirements.txt`)

```
opencv-python==4.8.1.78
mediapipe==0.10.8
pygame==2.5.2
numpy==1.24.3
protobuf==3.20.3
```

`protobuf` is pinned because MediaPipe 0.10.8 breaks with newer protobuf builds.

### Windows flow

1. `setup_venv.bat` — deletes any existing `venv`, creates a new one, upgrades pip, installs
   protobuf → numpy → opencv → mediapipe → pygame in that order.
2. `run.bat` — verifies `venv\Scripts\activate.bat` exists, activates, runs
   `python Home/hub.py`, then deactivates.

### Manual flow

```bash
python -m venv venv
venv\Scripts\activate.bat          # Windows
source venv/bin/activate           # macOS/Linux
pip install -r requirements.txt
python Home/hub.py                 # full hub
python MusicalMe_App/main.py       # music activity only
```

### Runtime requirements

Webcam, audio output, a desktop session (OpenCV high-GUI windows), and a display capable of
full-screen 1280×720. Linux users may need `libgl1` and `portaudio`/`sdl2` packages.

---

## 13. Assets

| Folder | Contents | Used by |
| --- | --- | --- |
| `MusicalMe_App/files/` | 8 piano MP3s (~20 KB each) | Piano bank |
| `MusicalMe_App/guitare file/` | 8 guitar MP3s (~80–110 KB each) | Guitar bank |
| `en_num/` | 10 English digit MP3s (`en_num_0.mp3`, `en_num_01.mp3` …) | Mathic LEARN |
| `fr_n/` | 10 French digit MP3s (`Zero.mp3` … `Neuf.mp3`) | Mathic LEARN |
| `numbers/` | `0.png`–`9.png`, loaded and resized to 80×80 | Mathic digits |
| `logos/` | backgrounds, logos, loading splash, exit icon | Hub, Mathic, loading |

All asset lookups are relative to the source file (`os.path.dirname(os.path.abspath(__file__))`)
or to the repository root, so the app does not depend on the current working directory.

---

## 14. Tuning guide

| Goal | Change |
| --- | --- |
| Notes trigger too easily | Lower `FINGER_TOUCH_THRESHOLD` (e.g. 0.04) |
| Notes feel unresponsive | Raise it (e.g. 0.06) |
| Pinch clicks accidentally | Lower `PINCH_THRESHOLD` |
| Menu opens by accident | Increase the pinky threshold in `is_finger_extended` (0.06 → 0.08) |
| Hand lost in dim light | Lower `DETECTION_CONFIDENCE` to 0.5–0.6 |
| Reduce audio latency | Lower `AUDIO_BUFFER_SIZE` to 1024 (may crackle) |
| Change pitch range | Edit `NUM_PITCH_ZONES` and the `2 - zone_index` mapping |
| Bigger hitboxes | Increase the 30/15 px padding in the hub / activities |
| Different palette | Edit `colors_palette` in `youdraw_game.py` |
| Faster menus | Lower `frame_cooldown` / `pinch_cooldown` |

---

## 15. Known issues and technical debt

1. **`venv/` is committed.** 7,164 of 7,256 tracked files (~400 MB of the repository) are a
   virtual environment. There is no `.gitignore`, so `__pycache__` is tracked too. This
   bloats clones and causes spurious diffs such as `youdraw_game.cpython-310.pyc`.
2. **One-off patch scripts in `Home/`.** `patch1.py`, `patch2.py`, `patch_menu.py`, and
   `inject_quiz.py` are development-time text replacements with hard-coded absolute paths
   (`c:\Users\DELL 7540\...`). They are not imported at runtime and will fail on any other
   machine. They should be deleted or moved to a `tools/` archive.
3. **Dead code.** `_detect_frame_gesture`, `get_pitch_bend_factor`, `menu_close`,
   `config.INSTRUMENT_FILES`, and `AudioEngine.get_reference_y` are unused.
4. **Hard-coded 1280×720 geometry.** Hub tiles, menus, and pitch bands assume this
   resolution; changing the camera size breaks hitboxes.
5. **`eval()` in Mathic.** Input is UI-constrained, but a safe arithmetic parser would
   remove the risk entirely.
6. **Duplicated loading-screen code.** `launch_musical_me`, `launch_youdraw`, and
   `launch_mathic` repeat ~30 identical lines.
7. **No automated tests.** Correctness of gesture thresholds is verified manually.
8. **Unused hub tiles.** Alphabet, TheZoo, and CarRoad render but do nothing when selected.
9. **Left-handed users** see handedness mirrored relative to the physical hand mapping.
10. **No frame pacing.** The loop runs as fast as the camera delivers; `FPS` is advisory.

---

## 16. Extending the project

**Add a new activity**

1. Create `MyApp/myapp.py` with a class exposing
   `__init__(shared_camera, shared_hand_detector, shared_gesture_recognizer, shared_window_name)`,
   `run()`, and `cleanup()`.
2. `sys.path.append` the `MusicalMe_App` folder and import `HandDetector` / `GestureRecognizer`.
3. Follow the shared-resource pattern: do not release hardware when `shared_resources` is true.
4. In `Home/hub.py`, add the module to `sys.path`, import it, add a logo entry to `self.games`,
   and add a `launch_*` branch in `run()`.

**Add an instrument**

- Add a sample folder, extend `INSTRUMENTS` and the loader in `AudioEngine.__init__`, or add
  a `generate_waveform` branch for a synthesized timbre.

**Add a note or remap gestures**

- Edit `NOTE_GESTURES` and `NOTE_FREQUENCIES` in `config.py`. Nothing else is hard-coded.

**Add a language to Mathic LEARN**

- Drop MP3s in a new folder, then add a name map and a `mixer.music.load` branch next to the
  existing EN/FR handlers.

---

## 17. Repository history

```
4c5fca1 Update YouDraw bytecode
718a94b YouDraw fixed
bb5544e Version: musicalMe, YouDraw, Hub, Mathic works
50555b1 Upgrade gesture controls, UI pitch zones, and audio synthesis
```

The project evolved from a single music app into a hub, then added Mathic and YouDraw while
keeping the shared vision layer unchanged.
