"""
TITONOMICS v2 — sound design: music bed + layered SFX (all synthesised).
"""
import numpy as np, wave, subprocess, os
import imageio_ffmpeg

SR = 48000
DUR = 30.0
N = int(SR * DUR)
FF = imageio_ffmpeg.get_ffmpeg_exe()
VO = "../assets/voiceover_shein.mp3"
OUT = "build/bed2.wav"

CUTS = [1.40, 2.75, 4.05, 5.60, 7.69, 9.20, 11.03, 13.40, 16.06,
        19.24, 22.42, 24.60, 26.54, 28.31]
BOOMS = [(0.00, 1.0), (7.69, 1.15), (22.42, 1.2), (28.31, 0.95)]
rng = np.random.default_rng(11)
t_all = np.arange(N) / SR

bed = np.zeros(N)


def add(sig, at, gain=1.0):
    s = int(at * SR)
    if s >= N:
        return
    n = min(len(sig), N - s)
    bed[s:s + n] += gain * sig[:n]


def env(n, a=0.005, d=0.3, curve=6.0):
    tt = np.arange(n) / SR
    e = np.exp(-tt * curve)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * np.cumsum(np.full(n, f)) / SR + phase)


def sweep(f0, f1, n):
    f = f0 * (f1 / f0) ** (np.arange(n) / max(1, n))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


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


def hp(x, k=0.02):
    return x - lp(x, k)


# ---------------------------------------------------------------- music bed
prog = [(0.0, 4.05, 55.0), (4.05, 11.03, 43.65), (11.03, 16.06, 65.41),
        (16.06, 22.42, 49.0), (22.42, 26.54, 55.0), (26.54, 30.0, 41.2)]
for (a, b, root) in prog:
    s, e = int(a * SR), int(b * SR)
    n = e - s
    tt = np.arange(n) / SR
    pad = (0.5 * np.sin(2 * np.pi * root * tt)
           + 0.3 * np.sin(2 * np.pi * root * 2 * tt + 0.7)
           + 0.18 * np.sin(2 * np.pi * root * 3 * tt + 1.9)
           + 0.12 * np.sin(2 * np.pi * root * 4.02 * tt))
    pad *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * tt)
    fade = np.minimum(1, np.minimum(np.arange(n) / (0.25 * SR), (n - np.arange(n)) / (0.25 * SR)))
    bed[s:e] += 0.085 * pad * fade

# kick + hat groove
beat = 0.0
while beat < DUR:
    if not (13.40 <= beat < 16.06):
        n = int(0.30 * SR)
        tt = np.arange(n) / SR
        f = 118 * np.exp(-tt * 34) + 44
        kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 13)
        add(kick, beat, 0.38 if beat < 22.5 else 0.26)
        # offbeat hat
        hn = int(0.06 * SR)
        hat = hp(noise(hn), 0.25) * np.exp(-np.arange(hn) / SR * 90)
        add(hat, beat + 0.25, 0.055)
    beat += 0.5

# bass stabs on the kick
for i in range(int(DUR / 0.5)):
    bt = i * 0.5
    if 13.40 <= bt < 16.06:
        continue
    root = [p for p in prog if p[0] <= bt < p[1]][0][2]
    n = int(0.24 * SR)
    tt = np.arange(n) / SR
    b = np.sin(2 * np.pi * root * 0.5 * tt) * np.exp(-tt * 9)
    add(b, bt, 0.17)

# ---------------------------------------------------------------- SFX
for c in CUTS:  # whoosh + click on every cut
    n = int(0.42 * SR)
    w = hp(noise(n), 0.06) * (np.linspace(0, 1, n) ** 3) * np.exp(-np.linspace(0, 1, n) * 3)
    add(w, c - 0.22, 0.20)
    cn = int(0.05 * SR)
    click = hp(noise(cn), 0.3) * np.exp(-np.arange(cn) / SR * 120)
    add(click, c, 0.16)

for (bt, g) in BOOMS:
    n = int(1.8 * SR)
    tt = np.arange(n) / SR
    f = 92 * np.exp(-tt * 7) + 28
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    body = hp(noise(n), 0.02) * np.exp(-tt * 16) * 0.5
    add(sub, bt, 0.62 * g)
    add(body, bt, 0.20 * g)

# odometer ticks during the counter
for i in range(26):
    at = 0.06 + i * 0.038
    n = int(0.03 * SR)
    tk = np.sign(np.sin(2 * np.pi * 2400 * np.arange(n) / SR)) * np.exp(-np.arange(n) / SR * 300)
    add(tk, at, 0.045 + i * 0.004)

# money sparkle at 22.42 + 22.9
for at, base in [(22.45, 1568.0), (22.9, 2093.0)]:
    for mult, g in [(1.0, 0.10), (1.5, 0.06), (2.0, 0.04)]:
        n = int(0.9 * SR)
        add(np.sin(2 * np.pi * base * mult * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 4), at, g)

# CTA chime
for at, f0 in [(13.42, 1046.5), (13.62, 1568.0)]:
    n = int(1.1 * SR)
    tt = np.arange(n) / SR
    bell = (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2.01 * tt)
            + 0.25 * np.sin(2 * np.pi * f0 * 3.02 * tt)) * np.exp(-tt * 3.4)
    add(bell, at, 0.12)

# tension alarm during the allegations
at = 16.1
k = 0
while at < 19.2:
    n = int(0.16 * SR)
    f = 740 if k % 2 == 0 else 554
    a = np.sin(2 * np.pi * f * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 12)
    add(a, at, 0.075)
    at += 0.20
    k += 1

# glitch burst on the review redactions
for at in [16.6, 17.4, 18.2]:
    n = int(0.18 * SR)
    gl = np.sign(noise(n)) * np.exp(-np.arange(n) / SR * 18)
    add(gl, at, 0.07)

# paper + stamp
n = int(0.5 * SR)
add(hp(noise(n), 0.15) * np.exp(-np.arange(n) / SR * 10), 26.30, 0.10)
n = int(0.7 * SR)
tt = np.arange(n) / SR
thud = np.sin(2 * np.pi * 120 * np.exp(-tt * 9) * tt) * np.exp(-tt * 14)
add(thud, 28.52, 0.5)
add(hp(noise(n), 0.1) * np.exp(-tt * 25), 28.52, 0.16)

# risers
for (a, b) in [(21.4, 22.42), (27.2, 28.31), (6.9, 7.69)]:
    n = int((b - a) * SR)
    if n <= 0:
        continue
    nn = noise(n)
    body = lp(nn, 0.02, 1) * 0.6 + hp(nn, 0.2) * 0.4
    e = (np.linspace(0, 1, n) ** 2.6)
    add(body * e, a, 0.16)

# reverse swell into the mascot beat
n = int(0.7 * SR)
sw = lp(noise(n), 0.05, 1) * (np.linspace(0, 1, n) ** 3)
add(sw, 10.35, 0.15)

# ---------------------------------------------------------------- duck + write
raw = subprocess.run([FF, "-v", "quiet", "-i", VO, "-f", "f32le", "-ac", "1",
                      "-ar", str(SR), "-"], capture_output=True).stdout
vo = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
win = int(0.06 * SR)
envv = np.convolve(np.abs(vo), np.ones(win) / win, mode="same")
envv = np.clip(envv / (np.percentile(envv, 96) + 1e-9), 0, 1)
duck = 1.0 - 0.60 * envv
bed *= np.convolve(duck, np.ones(1600) / 1600, mode="same")

fade = int(0.4 * SR)
bed[-fade:] *= np.linspace(1, 0, fade)
bed[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))

peak = np.abs(bed).max()
bed = bed / max(1e-9, peak) * 0.62
os.makedirs("build", exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes())
print("wrote", OUT, "peak", float(np.abs(bed).max()))
