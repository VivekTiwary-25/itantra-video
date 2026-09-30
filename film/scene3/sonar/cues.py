"""Scene 3 SOS sonar section: every length, cue time and position in one place.

build.py, sound.py and the page template all read from here. Times are seconds from the start of each segment.
"Sonar time" T is shared by the three segments so the waves and the camera run continuously across the cuts:
sos_in t  -> T = t - 2.0      sos_sonar t -> T = t      sos_dive t -> T = t + 9.0
"""
FPS = 30
SEG_LEN = {'sos_in': 2.0, 'sos_sonar': 9.0, 'sos_dive': 1.5}
ORDER = ['sos_in', 'sos_sonar', 'sos_dive']
T_OFFSET = {'sos_in': -2.0, 'sos_sonar': 0.0, 'sos_dive': 9.0}

# Map points in the stitched z18 pixel frame of film/scene2/geo/campus_outlines.json. Illustrative, not measured.
V = [330, 598]                  # Vachana (same point as scene 2)
VIVEK = [350, 722]              # inside the courtyard block south of V ("block_d"): stands in for the chemistry lab

# Red SOS waves from V, in sonar time. Each wave: start T0, and the radius (map px) at which it has faded out.
# Every wave travels at the same calm speed. The reach grows a little with each wave (the search keeps going);
# only the last wave reaches Vivek, at T = 8.0.
WAVE_SPEED = 62.0               # map px / s   (125.6 px from V to Vivek)
WAVES = [(-0.9, 82.0), (0.9, 90.0), (2.7, 102.0), (4.45, 114.0), (5.975, 175.0)]
ARRIVE = 8.0                    # last wave reaches Vivek's point; his point lights red

# Cameras (map px target, distance, pitch). sos_sonar drifts slowly from SONAR_START to SONAR_END.
CAM_CLOSE = {'tx': V[0], 'tz': V[1], 'D': 95, 'pitch': 80, 'yaw': 0}      # sos_in: the pull-back starts here
SONAR_START = {'tx': 350, 'tz': 660, 'D': 640, 'pitch': 57, 'yaw': -2}
SONAR_END = {'tx': 346, 'tz': 668, 'D': 590, 'pitch': 58, 'yaw': 0}
DIVE_TO = {'tx': VIVEK[0], 'tz': VIVEK[1], 'D': 38, 'pitch': 82, 'yaw': 0}

SOS_IN = {
    'app_pulses': [0.15, 0.55],     # red rings grow out of the searching indicator on the phone
    'phone_out': (0.75, 1.20),      # phone and sides shrink into V and fade
    'sonar_in': (0.85, 1.15),       # sonar fades up, camera close on V
    'pull_back': (0.85, 2.0),       # camera pulls back to the sonar framing (ends exactly on sos_sonar's first frame)
}
SOS_SONAR = {
    'narration': [(1.0, 7.5)],      # N6 "iTantra searches nearby for help..."
}
SOS_DIVE = {
    'dive': (0.0, 0.95),
    'clip_in': (0.62, 1.0),
    'plate_start': 0.4,             # sospart2 plays from here so the LAST frame is src 2.967; lab_a continues at src 3.0
    'src_end': 3.0,
    'glow': (1.2, 1.5),             # soft red glow at his phone, fading in over the last 0.3 s
    'phone': [616, 638],            # phone in sospart2 around src 2.9-3.0 (1920x1080)
    'whoosh_peak': 0.8,
}

APP_STILL = {
    'input': 'RENDERS:scene3/app/vachana_sos_last.png',   # the slot's last frame, the searching state (portrait)
    'crop_top': 110,                                       # same status-bar crop as the scene 2 slots
    'search_xy': [0.5, 0.5],        # where the pulsing "Searching for nearby help..." sits, as a fraction of the cropped still
}
SIDES_SRC = ('Video/sospart1.mp4', 10.5)   # blurred, darkened sospart1 behind the phone (its last frames)

COLOURS = {'ring': '#E65A63', 'glow': '#D62F40', 'wake': '#A52936'}


def music_quiet_zones():
    """Zones where the music steps back, in music-stem time (the stem runs sos_in..sos_dive, 12.5 s)."""
    off = SEG_LEN['sos_in']
    return [(off + a, off + b, 'sos_sonar') for a, b in SOS_SONAR['narration']]
