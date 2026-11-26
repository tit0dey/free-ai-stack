"""
TITONOMICS — paper-doodle soundtrack: plucked music bed + marker/stamp/ding SFX.
Cue times come from build/timeline.json (real TTS timings).
"""
import json, os, wave, subprocess
import numpy as np
import imageio_ffmpeg

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.load(open("build/timeline.json"))
DUR = TL["total"] + 0.35
N = int(SR * DUR)
S = TL["sentences"]
BEAT_CUES = [max(0.0, s["start"] - 0.42) for s in S]
rng = np.random.default_rng(23)
out = np.zeros(N)


def add(sig, at, gain=1.0):
    s = int(at * SR)
    if s >= N:
        return
    n = min(len(sig), N - s)
    out[s:s + n] += gain * sig[:n]


def noise(n):
    return rng.normal(0, 1, n)


def lp(x, k=0.1, times=2):
    for _ in range(times):
        y = np.zeros_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += k * (x[i] - acc)
            y[i] = acc
        x = y
    return x


def hp(x, k=0.05):
    return x - lp(x, k)


def env(n, dec=8.0):
    return np.exp(-np.arange(n) / SR * dec)


def tone(f, n, dec=8.0, harm=(1.0,), detune=0.0):
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for i, h in enumerate(harm):
        sig += h * np.sin(2 * np.pi * f * (i + 1) * (1 + detune) * t)
    return sig * env(n, dec)


# ---------------------------------------------------------------- music
# soft plucked arpeggio, 100 BPM, D minor-ish
BPM = 100
B = 60 / BPM
chords = [(146.83, 174.61, 220.0), (130.81, 164.81, 196.0), (110.0, 130.81, 164.81), (98.0, 123.47, 146.83)]
i = 0
at = 0.0
while at < DUR:
    ch = chords[(int(at / (B * 8))) % len(chords)]
    f = ch[i % 3]
    n = int(0.5 * SR)
    add(tone(f * 2, n, 7.0, (1.0, 0.35, 0.12)), at, 0.075)
    if i % 4 == 0:  # soft kick
        n2 = int(0.28 * SR)
        tt = np.arange(n2) / SR
        fk = 105 * np.exp(-tt * 30) + 42
        add(np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tt * 15), at, 0.22)
    if i % 2 == 1:  # shaker
        n3 = int(0.05 * SR)
        add(hp(noise(n3), 0.3) * np.exp(-np.arange(n3) / SR * 110), at, 0.035)
    at += B / 2
    i += 1

# pad under the second half
s0 = int(0.5 * DUR * SR)
pad_n = N - s0
tt = np.arange(pad_n) / SR
pad = (np.sin(2 * np.pi * 98 * tt) + 0.6 * np.sin(2 * np.pi * 146.83 * tt + 1.2)) * 0.5
ramp = np.minimum(1, np.arange(pad_n) / (2 * SR))
out[s0:] += 0.05 * pad * ramp

# ---------------------------------------------------------------- SFX
for c in BEAT_CUES:  # marker squeak + paper flip
    n = int(0.16 * SR)
    sq = hp(noise(n), 0.25) * np.exp(-np.arange(n) / SR * 22)
    add(sq, c, 0.055)
    n2 = int(0.26 * SR)
    fl = hp(noise(n2), 0.08) * np.exp(-np.arange(n2) / SR * 18) * np.linspace(0.2, 1, n2)
    add(fl, c + 0.02, 0.075)

# stamps / thumps (beats with stamped words)
for idx in [1, 6, 9, 13]:
    if idx < len(BEAT_CUES):
        c = BEAT_CUES[idx] + 0.55
        n = int(0.45 * SR)
        tt2 = np.arange(n) / SR
        th = np.sin(2 * np.pi * (90 * np.exp(-tt2 * 8) + 38) * tt2) * np.exp(-tt2 * 16)
        add(th, c, 0.42)
        add(hp(noise(int(0.06 * SR)), 0.2) * np.exp(-np.arange(int(0.06 * SR)) / SR * 90), c, 0.16)

# dings on money numbers
for (c, f) in [(BEAT_CUES[0] + 0.55, 1318.5), (BEAT_CUES[6] + 0.4, 1568.0), (BEAT_CUES[12] + 0.6, 1760.0)]:
    for mult, g in [(1.0, 0.12), (2.01, 0.05)]:
        n = int(1.0 * SR)
        add(np.sin(2 * np.pi * f * mult * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 4.5), c, g)

# ticking while the counter rolls
for k in range(14):
    n = int(0.02 * SR)
    tk = np.sign(np.sin(2 * np.pi * 2200 * np.arange(n) / SR)) * np.exp(-np.arange(n) / SR * 400)
    add(tk, BEAT_CUES[6] + 0.05 + k * 0.035, 0.03)

# riser into hook and into the ending
for (a, b) in [(0.0, BEAT_CUES[0] + 0.35), (BEAT_CUES[16] - 0.6, BEAT_CUES[16])]:
    n = int(max(0.1, b - a) * SR)
    r = lp(noise(n), 0.03, 1) * (np.linspace(0, 1, n) ** 2.4)
    add(r, a, 0.10)

# final hit + fade
n = int(1.2 * SR)
tt3 = np.arange(n) / SR
add(np.sin(2 * np.pi * (80 * np.exp(-tt3 * 6) + 34) * tt3) * np.exp(-tt3 * 4), BEAT_CUES[17], 0.5)
tail = int(0.5 * SR)
out[-tail:] *= np.linspace(1, 0, tail)

# ---------------------------------------------------------------- duck under VO
raw = subprocess.run([FF, "-v", "quiet", "-i", "vo/g1.mp3", "-f", "f32le", "-"], capture_output=True)
_ = raw
vo_all = np.zeros(N)
for g in TL["clips"]:
    st = TL["groups"][int(g[1:]) - 1]["start"]
    data = subprocess.run([FF, "-v", "quiet", "-i", f"vo/{g}.mp3", "-f", "f32le", "-ac", "1",
                           "-ar", str(SR), "-"], capture_output=True).stdout
    v = np.frombuffer(data, dtype=np.float32).astype(np.float64)
    s = int(st * SR)
    vo_all[s:s + min(len(v), N - s)] += v[:max(0, N - s)]

win = int(0.06 * SR)
ev = np.convolve(np.abs(vo_all), np.ones(win) / win, mode="same")
ev = np.clip(ev / (np.percentile(ev, 96) + 1e-9), 0, 1)
duck = 1.0 - 0.55 * ev
out *= np.convolve(duck, np.ones(1600) / 1600, mode="same")

peak = np.abs(out).max()
out = out / max(1e-9, peak) * 0.55
os.makedirs("build", exist_ok=True)
with wave.open("build/bed3.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print("bed3 ok, dur", DUR, "peak", float(np.abs(out).max()), "beats", len(BEAT_CUES))
