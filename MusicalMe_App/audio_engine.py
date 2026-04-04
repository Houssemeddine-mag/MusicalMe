"""
Audio synthesis engine with high-quality instrument sounds
"""
import os
import pygame
import numpy as np
from pygame import mixer
from config import (
    SAMPLE_RATE, NOTE_FREQUENCIES, INSTRUMENTS, 
    MAX_ACTIVE_NOTES, AUDIO_BUFFER_SIZE
)


class AudioEngine:
    def __init__(self):
        """Initialize pygame mixer and audio engine"""
        mixer.pre_init(SAMPLE_RATE, -16, 2, AUDIO_BUFFER_SIZE)
        pygame.init()
        mixer.init()
        
        self.current_instrument = 'piano'
        self.active_notes = {}  # key: note_name, value: {'sound': Sound, 'channel': Channel, 'base_freq': float}
        self.note_reference_y = {}  # Track initial Y position for each note
        
        # Pre-load piano and guitar mp3 files
        self.piano_sounds = {}
        self.guitar_sounds = {}
        self.pitched_sounds_cache = {}  # Cache for pitch-shifted notes
        
        # Get absolute path of this file to construct correct relative paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load Piano
        piano_files = {
            'DO': os.path.join(base_dir, 'files', '1_DO.mp3'),
            'RE': os.path.join(base_dir, 'files', '2_RE.mp3'),
            'MI': os.path.join(base_dir, 'files', '3_MI.mp3'),
            'FA': os.path.join(base_dir, 'files', '4_FA.mp3'),
            'SOL': os.path.join(base_dir, 'files', '5_SOL.mp3'),
            'LA': os.path.join(base_dir, 'files', '6_LA.mp3'),
            'SI': os.path.join(base_dir, 'files', '7_SI.mp3'),
            'DO_HIGH': os.path.join(base_dir, 'files', '8_DO_high.mp3')
        }
        for note, filename in piano_files.items():
            if os.path.exists(filename):
                self.piano_sounds[note] = mixer.Sound(filename)
            else:
                print(f"Warning: Piano sound file not found: {filename}")

        # Load Guitar
        guitar_files = {
            'DO': os.path.join(base_dir, 'guitare file', 'DO.mp3'),
            'RE': os.path.join(base_dir, 'guitare file', 'RE.mp3'),
            'MI': os.path.join(base_dir, 'guitare file', 'MI.mp3'),
            'FA': os.path.join(base_dir, 'guitare file', 'FA.mp3'),
            'SOL': os.path.join(base_dir, 'guitare file', 'SOL.mp3'),
            'LA': os.path.join(base_dir, 'guitare file', 'LA.mp3'),
            'SI': os.path.join(base_dir, 'guitare file', 'SI.mp3'),
            'DO_HIGH': os.path.join(base_dir, 'guitare file', 'DO HIGH.mp3')
        }
        for note, filename in guitar_files.items():
            if os.path.exists(filename):
                self.guitar_sounds[note] = mixer.Sound(filename)
            else:
                print(f"Warning: Guitar sound file not found: {filename}")
                
    def _get_pitched_sound(self, note_name, multiplier):
        """Get a pitch-shifted version of a pre-loaded sound. Caches results for performance."""
        import numpy as np
        import pygame
        
        # Select active sample bank based on current instrument
        sounds_bank = self.guitar_sounds if self.current_instrument == 'guitar' else self.piano_sounds
        
        if note_name not in sounds_bank:
            return None
        
        # Don't shift if multiplier is exactly 1.0 (or very close)
        if abs(multiplier - 1.0) < 0.01:
            return sounds_bank[note_name]
            
        # Check cache
        cache_key = (self.current_instrument, note_name, round(multiplier, 3))
        if cache_key in self.pitched_sounds_cache:
            return self.pitched_sounds_cache[cache_key]
            
        base_sound = sounds_bank[note_name]
        try:
            snd_array = pygame.sndarray.array(base_sound)
            L = len(snd_array)
            new_L = int(L / multiplier)
            
            old_indices = np.arange(L)
            new_indices = np.linspace(0, L - 1, new_L)
            
            # Resample keeping length dynamic (changes pitch as if speeding up tape)
            if len(snd_array.shape) == 2:
                new_left = np.interp(new_indices, old_indices, snd_array[:, 0])
                new_right = np.interp(new_indices, old_indices, snd_array[:, 1])
                resampled = np.column_stack((new_left, new_right))
            else:
                new_mono = np.interp(new_indices, old_indices, snd_array)
                resampled = np.column_stack((new_mono, new_mono))
                
            resampled = resampled.astype(np.int16)
            new_sound = pygame.sndarray.make_sound(resampled)
            
            self.pitched_sounds_cache[cache_key] = new_sound
            return new_sound
        except Exception as e:
            print(f"Error pitch-shifting {note_name}: {e}")
            return base_sound
        
    def generate_waveform(self, frequency, duration=1.0, instrument='piano'):
        """
        Generate a waveform for a specific frequency and instrument
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            instrument: Instrument type ('piano', 'guitar', 'square', 'flute')
            
        Returns:
            numpy array of audio samples
        """
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
        
        if instrument == 'piano':
            # Piano: Rich harmonic structure with realistic overtones
            wave = np.sin(2 * np.pi * frequency * t)  # Fundamental
            wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)  # 2nd harmonic
            wave += 0.25 * np.sin(2 * np.pi * frequency * 3 * t)  # 3rd harmonic
            wave += 0.1 * np.sin(2 * np.pi * frequency * 4 * t)  # 4th harmonic
            wave += 0.05 * np.sin(2 * np.pi * frequency * 5 * t)  # 5th harmonic
            
            # Add slight inharmonicity
            inharmonicity = 1.0002
            wave += 0.05 * np.sin(2 * np.pi * frequency * 6 * inharmonicity * t)
            
            # Smooth envelope for continuous play
            envelope = self._create_piano_envelope(len(t))
            wave = wave * envelope
            
        elif instrument == 'guitar':
            # Guitar: Synth-plucked approximation
            wave = np.zeros(len(t))
            for h in range(1, 8):
                wave += (1.0 / h) * np.sin(2 * np.pi * frequency * h * t)
            
            # Decay envelope and slight chorus
            wave += 0.2 * np.sin(2 * np.pi * (frequency * 1.003) * t)
            
            envelope = self._create_guitar_envelope(len(t))
            wave = wave * envelope
            
        elif instrument == 'square':
            # Synthesizer: Fat square wave with detune
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
            wave += 0.5 * np.sign(np.sin(2 * np.pi * frequency * 1.01 * t))
            
            # Smooth envelope
            envelope = self._create_synth_envelope(len(t))
            wave = wave * envelope * 0.6  # Scale down to avoid clipping
            
        elif instrument == 'flute':
            # Flute: Sine wave with vibrato and noise breath
            vibrato = 0.03 * np.sin(2 * np.pi * 6 * t)  # 6Hz vibrato
            wave = np.sin(2 * np.pi * frequency * t * (1 + vibrato))
            
            # Breath noise
            noise = np.random.normal(0, 0.05, len(t))
            wave += noise
            
            # Gentle envelope
            envelope = self._create_flute_envelope(len(t))
            wave = wave * envelope
        
        else:
            # Default: simple sine wave
            wave = np.sin(2 * np.pi * frequency * t)
        
        # Normalize to 16-bit range
        wave = wave / np.max(np.abs(wave))  # Normalize to -1 to 1
        wave = (wave * 32767).astype(np.int16)
        
        # Convert to stereo
        stereo_wave = np.column_stack((wave, wave))
        
        return stereo_wave
    
    def _create_piano_envelope(self, length):
        """Create smooth envelope for piano sound with very high sustain"""
        attack = int(0.01 * length)  # 1% quick attack
        sustain_level = 0.95  # Very high sustain level for continuous play
        
        envelope = np.ones(length) * sustain_level
        
        # Very quick attack
        if attack > 0:
            envelope[:attack] = np.linspace(0, sustain_level, attack)
        
        # Minimal release at the end for seamless looping
        release = int(0.05 * length)
        if release > 0:
            envelope[-release:] *= np.linspace(1, 0.9, release)
        
        return envelope
    
    def _create_guitar_envelope(self, length):
        """Create decay envelope for continuous guitar sound"""
        attack = int(0.01 * length)
        
        # Decay slowly
        decay_time = np.linspace(0, 3, length)
        envelope = np.exp(-1.5 * decay_time)
        
        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
            
        return envelope
    
    def _create_synth_envelope(self, length):
        """Create envelope for synthesizer sound"""
        attack = int(0.05 * length)
        release = int(0.2 * length)
        
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] *= np.linspace(1, 0, release)
        
        return envelope
    
    def _create_flute_envelope(self, length):
        """Create envelope for flute sound"""
        attack = int(0.1 * length)
        release = int(0.15 * length)
        
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] *= np.linspace(1, 0, release)
        
        return envelope
    
    def play_note(self, note_name, pitch_multiplier=1.0, hand_y=0.5):
        """
        Play or update a musical note with pitch bending support
        
        Args:
            note_name: Name of the note (e.g., 'DO', 'RE', 'MI')
            pitch_multiplier: Multiplier for pitch bending
            hand_y: Vertical position of hand (for tracking reference)
        """
        if note_name not in NOTE_FREQUENCIES:
            return
            
        # Get base frequency
        base_freq = NOTE_FREQUENCIES[note_name]
        
        # Apply pitch bending
        freq = base_freq * pitch_multiplier
        
        # Limit active notes
        if len(self.active_notes) >= MAX_ACTIVE_NOTES and note_name not in self.active_notes:
            return
            
        # Check if note is already playing
        if note_name in self.active_notes:
            # If pitch hasn't changed, keep playing
            current_freq = self.active_notes[note_name].get('current_freq', base_freq)
            
            # For zone-based pitch, only update if frequency actually changed
            if abs(freq - current_freq) < 0.01:
                return
            
            # Stop current note instantly for immediate response
            if self.active_notes[note_name]['channel']:
                self.active_notes[note_name]['channel'].stop()
        
        # Check if we should use sample banks
        is_sample_instrument = self.current_instrument in ['piano', 'guitar']
        active_bank = self.guitar_sounds if self.current_instrument == 'guitar' else self.piano_sounds
        
        if is_sample_instrument and note_name in active_bank:
            # Use pre-loaded MP3 file with automatic pitch shifting
            sound = self._get_pitched_sound(note_name, pitch_multiplier)
            if sound:
                sound.set_volume(0.5)
                # We don't loop indefinitely, the mp3 has its natural decay
                channel = sound.play()
            else:
                # Fallback to generated if get_pitched_sound fails
                import numpy as np
                duration = 5.0
                wave = self.generate_waveform(freq, duration, self.current_instrument)
                sound = mixer.Sound(wave)
                sound.set_volume(0.5)
                channel = sound.play(loops=-1)
        else:
            # Revert to generated waveform for other instruments or missing files
            import numpy as np
            duration = 5.0  # Very long for seamless looping
            wave = self.generate_waveform(freq, duration, self.current_instrument)
            sound = mixer.Sound(wave)
            sound.set_volume(0.5)
            channel = sound.play(loops=-1)

        self.active_notes[note_name] = {
            'sound': sound,
            'channel': channel,
            'base_freq': base_freq,
            'current_freq': freq
        }
        self.note_reference_y[note_name] = hand_y
    
    def stop_note(self, note_name):
        """
        Stop playing a specific note
        
        Args:
            note_name: Name of the note to stop
        """
        if note_name in self.active_notes:
            # Removed fadeout so the single note completely finishes playing for kids
            del self.active_notes[note_name]
            if note_name in self.note_reference_y:
                del self.note_reference_y[note_name]
    
    def stop_all_notes(self):
        """Stop all currently playing notes"""
        for note_name in list(self.active_notes.keys()):
            self.stop_note(note_name)
    
    def set_instrument(self, instrument_name):
        """
        Change the current instrument
        
        Args:
            instrument_name: Name of instrument ('Piano', 'Guitar', 'Synthesizer', 'Flute')
        """
        if instrument_name in INSTRUMENTS:
            self.current_instrument = INSTRUMENTS[instrument_name]
            # Stop all notes when changing instrument
            self.stop_all_notes()
    
    def get_reference_y(self, note_name):
        """Get the reference Y position for a note (for pitch bending)"""
        return self.note_reference_y.get(note_name, 0.5)
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_all_notes()
        mixer.quit()
