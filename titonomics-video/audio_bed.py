"""
TITONOMICS — sound design bed generator (code only, no samples).
Builds: drone bed, pulse, whooshes on cuts, impacts, riser + sidechain duck under VO.
"""
import numpy as np, wave, subprocess, os, sys
import imageio_ffmpeg

SR = 48000
DUR = 30.0
N = int(SR * DUR)
FF = imageio_ffmpeg.get_ffmpeg_exe()

VO = "../assets/voiceover_shein.mp3"
OUT = "build/bed.wav"

# cut points (video beat boundaries)
CUTS = [1.40, 2.75, 4.05, 5.60, 7.69, 9.20, 11.03, 13.40, 16.06,
        19.24, 22.42, 24.60, 26.54, 28.31]
IMPACTS = [0.00, 7.69, 22.79, 28.31]
RISERS = [(21.85, 22.79), (27.55, 28.31)]

rng = np.random.default_rng(7)
t = np.arange(N) / SR


def env_ad(n, a, d, curve=3.0):
    a = max(1, int(a * SR)); d = max(1, int(d * SR))
    e = np.zeros(n)
    e[:min(a, n)] = np.linspace(0, 1, min(a, n)) ** 0.6
    if a < n:
        seg = n - a
        e[a:] = np.exp(-np.linspace(0, 1, seg) * curve * 2.5)
    return e


bed = np.zeros(N)

# ---------- 1. low drone (two detuned sines + slow LFO) ----------
lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.07 * t)
drone = (0.55 * np.sin(2 * np.pi * 55 * t)
         + 0.32 * np.sin(2 * np.pi * 82.41 * t + 0.4)
         + 0.18 * np.sin(2 * np.pi * 110 * t + 1.1))
bed += 0.055 * drone * lfo

# ---------- 2. heartbeat pulse (100 BPM, drops out at CTA) ----------
beat_t = 0.0
i = 0
while beat_t < DUR:
    if not (13.4 <= beat_t < 16.1):  # clear space for the CTA
        s = int(beat_t * SR); n = int(0.34 * SR)
        if s + n < N:
            tt = np.arange(n) / SR
            f = 62 * np.exp(-tt * 9) + 34
            k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11)
            bed[s:s + n] += 0.13 * k
    beat_t += 0.6

# ---------- 3. whooshes at cuts ----------
for c in CUTS:
    s = int((c - 0.30) * SR); n = int(0.55 * SR)
    if s < 0 or s + n >= N:
        continue
    noise = rng.normal(0, 1, n)
    # crude band-pass: one-pole lowpass of highpassed noise
    lp = np.zeros(n); a = 0.12
    for _ in range(2):
        acc = 0.0
        for j in range(n):
            acc += a * (noise[j] - acc)
            lp[j] = acc
    hp = noise - lp
    e = np.linspace(0, 1, n) ** 2 * np.exp(-np.linspace(0, 1, n) * 2.0)
    bed[s:s + n] += 0.055 * hp * e

# ---------- 4. impacts ----------
for h in IMPACTS:
    s = int(h * SR); n = int(1.4 * SR)
    if s + n >= N:
        n = N - s
    tt = np.arange(n) / SR
    f = 78 * np.exp(-tt * 6) + 30
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.0)
    click = rng.normal(0, 1, n) * np.exp(-tt * 45) * 0.6
    bed[s:s + n] += 0.30 * sub + 0.10 * click

# ---------- 5. risers ----------
for (a, b) in RISERS:
    s = int(a * SR); n = int((b - a) * SR)
    noise = rng.normal(0, 1, n)
    lp = np.zeros(n); acc = 0.0; k = 0.05
    for j in range(n):
        acc += k * (noise[j] - acc)
        lp[j] = acc
    e = np.linspace(0, 1, n) ** 2.2
    bed[s:s + n] += 0.10 * lp * e

# ---------- 6. tails ----------
fade = int(0.35 * SR)
bed[-fade:] *= np.linspace(1, 0, fade)

# ---------- 7. sidechain duck under narration ----------
raw = subprocess.run([FF, "-v", "quiet", "-i", VO, "-f", "f32le", "-ac", "1",
                      "-ar", str(SR), "-"], capture_output=True).stdout
vo = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
win = int(0.08 * SR)
env = np.convolve(np.abs(vo), np.ones(win) / win, mode="same")
env = np.clip(env / (np.percentile(env, 97) + 1e-9), 0, 1)
duck = 1.0 - 0.62 * env
bed *= np.convolve(duck, np.ones(2400) / 2400, mode="same")

mix = np.clip(bed, -1, 1)
pcm = (mix * 32767).astype(np.int16)
os.makedirs("build", exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", OUT, f"{DUR}s", "peak", float(np.abs(mix).max()))
