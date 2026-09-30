"""Scene 2 sonar section: every length, cue time and relay spec in one place.

build.py, sound.py and the HTML templates all read from here, so sound and picture share the same numbers.
All times are in seconds from the start of each segment. 30 fps, 1920x1080.
"""
FPS = 30
W, H = 1920, 1080

SEG_LEN = {'sonar_a': 7.0, 'relay_1': 6.0, 'relay_2': 6.0, 'relay_3': 6.0, 'sonar_b': 6.0}
ORDER = ['sonar_a', 'relay_1', 'relay_2', 'relay_3', 'sonar_b']

# ------------------------------------------------------------------ sonar_a
SONAR_A = {
    'fade_in': (0.0, 1.4),              # from black
    'pulses': [                          # (origin point key or [px,py], start time, speed in map px / s)
        ([470, 640], 0.35, 230.0),
        ([470, 640], 2.25, 260.0),
        ('V', 4.30, 300.0),
    ],
    'points_on': {'V': 3.00, 'R1': 3.14, 'R2': 3.28, 'R3': 3.42, 'Y': 3.56},   # each point lights up
    'labels_on': 3.35,                   # "Vachana" / "Yash" labels fade in
    'cam_settle': 6.2,                   # camera reaches the overview framing and holds
    'narration': [(0.0, 3.5)],           # step 9 line plays over this; keep calm
}

# ------------------------------------------------------------------ relay segments (shared shape)
RELAY_SHAPE = {
    'dive': (0.0, 0.8),          # sonar camera dives into the point
    'clip_in': (0.5, 0.85),      # live clip fades up under the flare
    'plate_start': 0.5,          # the prepared plate (live -> freeze -> live) starts here
    'freeze': 2.0,               # live 0.5-2.0 (fully visible from 0.8: 1.2 s of live clip)
    'resume': 5.3,               # clip carries on 5.3-6.0
    'push': (2.0, 6.0, 1.075),   # slow push-in about the phone, scale 1 -> 1.075
    'drain': (2.05, 2.55),       # colour drains except around the phone
    'glow': (2.35, 2.85),        # faint blue glow on the phone
    'slant': (2.45, 2.80),       # callout line: slant up
    'flat': (2.80, 3.00),        # then flat
    'tick': 3.00,                # soft tick as the line lands
    'text_in': (3.00, 3.35),     # text fades in at the end of the line; fully visible 3.35-5.15 (1.8 s)
    'text_out': (5.15, 5.40),
    'undrain': (5.10, 5.60),     # colour returns
    'whoosh_peak': 0.65,
}

# Freeze time F is in source-clip seconds. Phone position, callout path and text are in 1920x1080 frame pixels
# at the freeze frame. `side` = which way the flat part of the line runs. `island` = [cx, cy, rx, ry] of the soft area
# that keeps its colour during the drain (kept tight so the red/pink shirts in relay_2/3 stay grey: red is for SOS).
# `dive_to` = where the person is when the clip fades up (the sonar point's flare lands there).
RELAYS = {
    'relay_1': {
        'point': 'R1', 'who': 'Vaishnavi', 'clip': 'Video/normalpart5.mp4', 'F': 3.0,
        'phone': [1022, 705], 'glow_r': 80, 'island': [1022, 705, 64, 64],
        'dive_to': [1000, 612],
        'path': [[1052, 688], [1212, 440], [1302, 440]], 'side': 'right',
        'text': ['Her phone passes the message on.', 'She just keeps walking.'],
    },
    'relay_2': {
        'point': 'R2', 'who': 'Utkarsh', 'clip': 'Video/normalpart4.mp4', 'F': 2.2,
        'phone': [936, 498], 'glow_r': 78, 'island': [938, 492, 46, 46],
        'dive_to': [936, 498],
        'path': [[912, 486], [806, 352], [716, 352]], 'side': 'left',
        'text': ['His phone relays it in the background.', 'His call carries on.'],
    },
    'relay_3': {
        'point': 'R3', 'who': 'Thrisha', 'clip': 'Video/normalpart3.mp4', 'F': 6.5,
        'phone': [672, 828], 'glow_r': 72, 'island': [668, 842, 40, 36],
        'dive_to': [110, 760],
        'path': [[652, 810], [548, 648], [458, 648]], 'side': 'left',
        'text': ['Her phone hands it forward.', 'She keeps going.'],
    },
}

# ------------------------------------------------------------------ sonar_b
SONAR_B = {
    'pulses': [('V', -3.0, 300.0), ('V', 0.15, 300.0)],
    'hops': [                     # packet leaves `a` at t0 and lands on `b` at t1
        ('V', 'R1', 0.55, 1.10),
        ('R1', 'R2', 1.22, 1.72),
        ('R2', 'R3', 1.84, 2.42),
        ('R3', 'Y', 2.54, 3.12),
    ],
    'arrive': 3.12,               # Y pulses, soft chime
    'still_from': 5.2,            # nothing moves after this: clean still to cut out on
    'narration': [(4.0, 5.8)],    # "And that's how it gets there."
}

COLOURS = {'relay': '#2EA8FF', 'ink': '#F3F5F8'}


def music_narration_zones():
    """Narration zones in music-stem time (the stem runs sonar_a..sonar_b back to back, 31 s)."""
    off, zones = 0.0, []
    for seg in ORDER:
        src = SONAR_A if seg == 'sonar_a' else SONAR_B if seg == 'sonar_b' else {}
        for a, b in src.get('narration', []):
            zones.append((round(off + a, 3), round(off + b, 3), seg))
        off += SEG_LEN[seg]
    return zones


def seg_offset(seg):
    return sum(SEG_LEN[s] for s in ORDER[:ORDER.index(seg)])
