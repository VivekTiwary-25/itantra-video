# Soft "doorway" sound for the panel -> phone morph: an airy filtered-noise swell plus a quiet two-note glass tone.
# Deterministic (fixed seed). Writes film/scene1/assets/doorway.wav (48 kHz stereo, peak about -16 dBFS).
import numpy as np, wave
from scipy.signal import butter, sosfilt
sr = 48000; d = 2.4; t = np.arange(int(sr*d))/sr
rng = np.random.default_rng(7)
n = rng.standard_normal(len(t))
sweep = np.zeros_like(n)
# band-passed noise whose centre rises 600 -> 2400 Hz (processed in blocks)
blk = 2400
for i in range(0, len(n), blk):
    f = 600 + 1800*min(1, i/(sr*0.9))
    sos = butter(2, [f*0.6, f*1.6], 'band', fs=sr, output='sos')
    sweep[i:i+blk] = sosfilt(sos, n[max(0,i-blk):i+blk])[-len(n[i:i+blk]):]
env = np.clip(t/0.55, 0, 1)**2 * np.exp(-np.clip(t-0.55, 0, None)*5.0)
air = sweep*env*0.22
# glass tone: E6 + B6, soft attack at 0.5 s, long decay
tt = np.clip(t-0.5, 0, None); on = (t >= 0.5)
tone = on*(np.sin(2*np.pi*1318.5*tt)*0.6 + np.sin(2*np.pi*1975.5*tt)*0.3 + np.sin(2*np.pi*2637*tt)*0.08)
tone *= np.clip(tt/0.02, 0, 1)*np.exp(-tt*2.6)*0.16
x = air + tone
x = sosfilt(butter(2, 180, 'high', fs=sr, output='sos'), x)
x *= 10**(-16/20)/np.abs(x).max()
fade = np.ones_like(x); fade[-int(0.2*sr):] = np.linspace(1, 0, int(0.2*sr)); x *= fade
# slight stereo width: right channel delayed 6 ms
L = x; R = np.concatenate([np.zeros(int(0.006*sr)), x[:-int(0.006*sr)]])
pcm = (np.stack([L, R], 1)*32767).astype('<i2')
with wave.open('film/scene1/assets/doorway.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
print('ok', len(x)/sr, 's')
