"""Build the five selected iTantra cues as deterministic 48 kHz stereo WAVs.

Run from any directory:
    python film/sound/make_set.py
    python film/sound/make_set.py --out path/to/output

The default output is RENDERS:sound/. The four established cues use the
recommended T0024 designs. No source audio, network access, or randomness.
"""

import argparse
import json
import math
import os
import struct
import wave


RATE = 48000
TARGET_PEAK = 10 ** (-12.0 / 20.0)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

SELECTED = (
    ("notify.wav", "message_a"),
    ("sent.wav", "sent_a"),
    ("sos_notify.wav", "sos_notice_a"),
    ("tick.wav", "tick_b"),
)

# A is the production selection: a deliberate descending two-note response.
# B is a round single gesture; C is a measured three-step descent. All stay
# short and tonal, avoiding sirens, impacts, and cinematic low-frequency booms.
SOS_SEND = (
    {"id": "sos_send_a", "duration": 0.72, "attack": 0.008,
     "release": 0.105, "notes": [
         [0.016, 0.32, 440, 428, 0.72, 0.07],
         [0.250, 0.39, 330, 316, 0.70, 0.05]]},
    {"id": "sos_send_b", "duration": 0.68, "attack": 0.018,
     "release": 0.145, "notes": [
         [0.018, 0.57, 370, 335, 0.77, 0.08],
         [0.053, 0.40, 555, 502, 0.22, 0.03]]},
    {"id": "sos_send_c", "duration": 0.82, "attack": 0.007,
     "release": 0.105, "notes": [
         [0.018, 0.24, 494, 481, 0.67, 0.06],
         [0.238, 0.25, 392, 379, 0.65, 0.05],
         [0.463, 0.28, 294, 283, 0.64, 0.04]]},
)


def sample_count(seconds):
    return int(seconds * RATE + 0.5)


def default_output():
    with open(os.path.join(REPO, "machine.local.json"), "r") as source:
        machine = json.load(source)
    return os.path.join(machine["renders_dir"], "sound")


def synthesize(spec):
    count = sample_count(spec["duration"])
    mono = [0.0] * count
    for start, duration, low, high, level, harmonic in spec["notes"]:
        first = sample_count(start)
        length = min(sample_count(duration), count - first)
        if length <= 0:
            continue
        attack = min(spec["attack"], duration / 3.0)
        release = min(spec["release"], duration / 2.0)
        for i in range(length):
            t = float(i) / RATE
            phase = 2.0 * math.pi * (low * t +
                    (high - low) * t * t / (2.0 * duration))
            fade_in = min(t / attack, 1.0)
            fade_out = min((duration - t) / release, 1.0)
            envelope = (math.sin(fade_in * math.pi / 2.0) ** 2 *
                        math.sin(fade_out * math.pi / 2.0) ** 2 *
                        math.exp(-1.2 * t / duration))
            mono[first + i] += level * envelope * (
                math.sin(phase) + harmonic * math.sin(2.0 * phase))

    peak = max(abs(value) for value in mono)
    if peak == 0.0:
        raise ValueError("Silent sound: " + spec["id"])
    scale = TARGET_PEAK / peak
    pcm = bytearray()
    for i in range(count):
        left = int(round(mono[i] * scale * 32767.0))
        right = int(round(mono[i - 9] * scale * 32767.0)) if i >= 9 else 0
        pcm.extend(struct.pack("<hh", left, right))
    return pcm, count


def write_wave(path, spec):
    pcm, count = synthesize(spec)
    output = wave.open(path, "wb")
    try:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm)
    finally:
        output.close()
    print("{}: {:.3f} s".format(os.path.basename(path), float(count) / RATE))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="Override the default RENDERS:sound/ directory")
    parser.add_argument("--sos-options", action="store_true",
                        help="Also write all three SOS Send options for review")
    args = parser.parse_args()
    destination = args.out if args.out else default_output()
    if not os.path.isdir(destination):
        os.makedirs(destination)

    with open(os.path.join(HERE, "designs.json"), "r") as source:
        designs = dict((spec["id"], spec) for spec in json.load(source))
    for name, design_id in SELECTED:
        write_wave(os.path.join(destination, name), designs[design_id])
    write_wave(os.path.join(destination, "sos_send.wav"), SOS_SEND[0])

    if args.sos_options:
        option_dir = os.path.join(destination, "sos_send_options")
        if not os.path.isdir(option_dir):
            os.makedirs(option_dir)
        for spec in SOS_SEND:
            write_wave(os.path.join(option_dir, spec["id"] + ".wav"), spec)


if __name__ == "__main__":
    main()
