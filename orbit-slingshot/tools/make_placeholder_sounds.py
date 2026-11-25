"""Generates placeholder sound effects + a music loop into assets/ (no extra libraries needed).

    python tools/make_placeholder_sounds.py            # only creates files that don't exist yet
    python tools/make_placeholder_sounds.py --force    # overwrite everything

Replace any of them with real sounds whenever you like - just keep the same file name
(e.g. assets/sfx/launch.wav). Real sounds should NOT be overwritten unless you use --force.
"""
import math
import os
import random
import struct
import sys
import wave

RATE = 22050                    # 22 kHz mono keeps the files small; fine for retro sfx
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
FORCE = '--force' in sys.argv


# ------------------------------------------------------------------ building blocks
def silence(length):
    return [0.0] * int(RATE * length)


def osc(freq_start, freq_end, length, shape='sine', curve=1.0):
    """A tone that slides from freq_start to freq_end. curve > 1 = slide happens late."""
    out, phase = [], 0.0
    n = int(RATE * length)
    for i in range(n):
        t = (i / n) ** curve
        phase += 2 * math.pi * (freq_start + (freq_end - freq_start) * t) / RATE
        if shape == 'sine':
            s = math.sin(phase)
        elif shape == 'square':
            s = 1.0 if math.sin(phase) > 0 else -1.0
        elif shape == 'saw':
            s = 2 * ((phase / (2 * math.pi)) % 1) - 1
        else:                                       # triangle
            s = 2 * abs(2 * ((phase / (2 * math.pi)) % 1) - 1) - 1
        out.append(s)
    return out


def noise(length, smooth=0.0):
    """White noise. smooth 0..0.99 = low-pass it (higher = duller, more 'rumble')."""
    out, last = [], 0.0
    for _ in range(int(RATE * length)):
        last = last * smooth + random.uniform(-1, 1) * (1 - smooth)
        out.append(last)
    return out


def envelope(samples, attack=0.005, decay_power=2.0, hold=0.0):
    """Quick fade in, then fade out. decay_power bigger = dies away faster."""
    n = len(samples)
    a = max(1, int(RATE * attack))
    h = int(n * hold)
    out = []
    for i, s in enumerate(samples):
        if i < a:
            g = i / a
        elif i < h:
            g = 1.0
        else:
            g = (1 - (i - h) / max(1, n - h)) ** decay_power
        out.append(s * g)
    return out


def mix(*tracks):
    n = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(n)]


def gain(samples, g):
    return [s * g for s in samples]


def normalize(samples, peak=0.85):
    top = max(abs(s) for s in samples) or 1
    return [s / top * peak for s in samples]


def save(path, samples):
    path = os.path.join(BASE, path)
    if os.path.exists(path) and not FORCE:
        print('skip (already exists):', path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32000)) for s in samples))
    print('wrote', path)


# ------------------------------------------------------------------ the sounds
def launch():           # whoosh: rising tone + airy noise
    tone = envelope(osc(180, 820, 0.4, 'triangle', curve=0.7), 0.01, 1.6)
    air = envelope(noise(0.4, 0.55), 0.03, 1.4)
    return normalize(mix(gain(tone, 0.6), gain(air, 0.5)), 0.7)


def crash():            # low boom + crunchy debris
    boom = envelope(osc(110, 30, 0.75, 'sine', curve=0.5), 0.002, 2.2)
    rumble = envelope(noise(0.75, 0.93), 0.002, 1.8)
    crunch = envelope(noise(0.18, 0.2), 0.001, 3.0)
    return normalize(mix(gain(boom, 1.0), gain(rumble, 1.6), gain(crunch, 0.35)), 0.85)


def star():             # bright double blip
    a = envelope(mix(osc(1320, 1400, 0.09), gain(osc(2640, 2800, 0.09), 0.25)), 0.002, 2.0)
    b = envelope(mix(osc(1760, 1900, 0.16), gain(osc(3520, 3800, 0.16), 0.25)), 0.002, 2.0)
    return normalize(a + b, 0.55)


def win():              # little victory fanfare: C E G C, then a held chord
    notes = [523.25, 659.25, 783.99]
    out = []
    for f in notes:
        out += envelope(mix(osc(f, f, 0.12, 'square'), gain(osc(f * 2, f * 2, 0.12), 0.3)), 0.004, 1.2)
    chord = mix(*[gain(osc(f, f, 0.9, 'triangle'), 0.4) for f in (523.25, 659.25, 783.99, 1046.5)])
    out += envelope(chord, 0.01, 1.8)
    return normalize(out, 0.6)


def boss_hit():         # meaty thump + squelch
    thump = envelope(osc(260, 60, 0.35, 'sine', curve=0.6), 0.001, 2.0)
    squelch = envelope(osc(700, 180, 0.25, 'saw'), 0.001, 2.5)
    hit = envelope(noise(0.08, 0.3), 0.001, 2.0)
    return normalize(mix(gain(thump, 1.0), gain(squelch, 0.35), gain(hit, 0.5)), 0.85)


def boss_attack():      # three quick claw swipes + growl
    out = []
    for i in range(3):
        swipe = envelope(mix(noise(0.13, 0.15 + i * 0.1), gain(osc(900 - i * 150, 300, 0.13, 'saw'), 0.4)), 0.003, 1.5)
        out += swipe + silence(0.03)
    growl = envelope(mix(osc(85, 60, 0.5, 'saw'), gain(noise(0.5, 0.9), 1.5)), 0.02, 1.3)
    return normalize(mix(out, gain(growl, 0.7)), 0.85)


def claw_glow():        # rising shimmer with a wobble - "warning!"
    n = int(RATE * 0.55)
    base = osc(500, 1150, 0.55, 'triangle', curve=0.8)
    trem = [0.6 + 0.4 * math.sin(2 * math.pi * 18 * i / RATE) for i in range(n)]
    shimmer = [b * t for b, t in zip(base, trem)]
    return normalize(envelope(shimmer, 0.05, 1.2, hold=0.4), 0.55)


def music():            # 24 second ambient space loop: soft pads + gentle plinks
    random.seed(7)
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63),     # Am, F
              (196.0, 246.94, 293.66), (164.81, 207.65, 246.94)]    # G, E
    bar = 6.0
    total = int(RATE * bar * len(chords))
    out = [0.0] * total
    for c, chord in enumerate(chords):
        start = int(RATE * bar * c)
        for f in chord:
            for detune in (1.0, 1.003):             # two slightly detuned voices = 'chorus'
                pad = osc(f * detune, f * detune, bar + 1.5, 'sine')
                pad = envelope(pad, attack=1.5, decay_power=1.0, hold=0.55)
                for i, s in enumerate(pad):
                    out[(start + i) % total] += s * 0.07   # wrap the tail round = seamless loop
        bass = envelope(osc(chord[0] / 2, chord[0] / 2, bar, 'sine'), 0.8, 1.0, hold=0.6)
        for i, s in enumerate(bass):
            out[(start + i) % total] += s * 0.12
        for k in range(4):                          # sparse twinkly notes from the chord
            f = random.choice(chord) * random.choice((2, 4))
            when = start + int(RATE * (k * bar / 4 + random.uniform(0, 0.6)))
            pl = envelope(mix(osc(f, f, 1.2), gain(osc(f * 2.01, f * 2.01, 1.2), 0.2)), 0.003, 3.0)
            for i, s in enumerate(pl):
                out[(when + i) % total] += s * 0.05
    return normalize(out, 0.5)


if __name__ == '__main__':
    random.seed(1)
    save('sfx/launch.wav', launch())
    save('sfx/crash.wav', crash())
    save('sfx/star.wav', star())
    save('sfx/win.wav', win())
    save('sfx/boss_hit.wav', boss_hit())
    save('sfx/boss_attack.wav', boss_attack())
    save('sfx/claw_glow.wav', claw_glow())
    save('music.wav', music())
