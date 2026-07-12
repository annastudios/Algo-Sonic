import numpy as np
import pygame

SAMPLE_RATE = 44100

# 3 octaves of a C major pentatonic scale - picking notes from this set
# instead of a raw linear Hz mapping is what keeps rapid comparisons from
# sounding like noise.
_ROOT = 130.81  # C3
_STEPS = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3]  # C D E G A ratios within an octave
SCALE = [_ROOT * ratio * (2 ** octave) for octave in range(3) for ratio in _STEPS]

# (duration_ms, volume, waveform) per event type
_EVENT_PROFILE = {
    "compare": (40, 0.25, "sine"),
    "swap": (90, 0.5, "sine"),
    "visit": (70, 0.4, "square"),
    "set": (60, 0.35, "sine"),
}

_cache = {}


def _make_wave(freq, duration_ms, volume, waveform):
    n = int(SAMPLE_RATE * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n, endpoint=False)
    if waveform == "square":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    else:
        wave = np.sin(2 * np.pi * freq * t)

    # fade in/out over the first and last ~5ms to avoid clicks
    fade_len = min(n // 4, int(SAMPLE_RATE * 0.005))
    if fade_len > 0:
        ramp = np.linspace(0, 1, fade_len)
        wave[:fade_len] *= ramp
        wave[-fade_len:] *= ramp[::-1]

    wave = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack([wave, wave])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


def play_event(event_type, note_index):
    """note_index is an index into SCALE (clamped)."""
    note_index = max(0, min(len(SCALE) - 1, note_index))
    key = (event_type, note_index)

    sound = _cache.get(key)
    if sound is None:
        duration_ms, volume, waveform = _EVENT_PROFILE.get(event_type, _EVENT_PROFILE["compare"])
        sound = _make_wave(SCALE[note_index], duration_ms, volume, waveform)
        _cache[key] = sound

    sound.play()


def note_index_for_value(value, lo, hi):
    """Map a value's position in [lo, hi] to an index into SCALE."""
    if hi <= lo:
        return 0
    frac = (value - lo) / (hi - lo)
    return round(frac * (len(SCALE) - 1))
