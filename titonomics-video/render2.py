"""
TITONOMICS v2 — cinematic code-only renderer.
Palette per act, camera moves, particles, shockwaves, kinetic type, real animation.
"""
import os, sys, math, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H, FPS = 1080, 1920, 30
DUR = 30.0
NFRAMES = int(round(DUR * FPS))
FF = imageio_ffmpeg.get_ffmpeg_exe()
FD = "/usr/share/fonts/truetype/dejavu/"

# ---------------- palette ----------------
INK = (6, 8, 13)
NAVY = (10, 17, 32)
BLUE = (16, 34, 66)
CYAN = (58, 216, 255)
CYAN_D = (26, 96, 130)
RED = (238, 66, 52)
RED_D = (108, 28, 24)
AMBER = (255, 194, 75)
AMBER_D = (120, 82, 24)
WHITE = (246, 244, 239)
GREY = (146, 156, 174)
DIM = (78, 88, 106)


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):
    x = cl(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x)
    return 3 * x * x - 2 * x * x * x


def back(x, s=2.2):
    x = cl(x) - 1
    return x * x * ((s + 1) * x + s) + 1


@lru_cache(maxsize=512)
def F(size, bold=True):
    return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), max(6, int(size)))


def tlen(d, s, font, track=0.0):
    return d.textlength(s, font=font) + track * max(0, len(s) - 1)


def text(d, xy, s, font, fill, anchor="mm", track=0.0):
    if track == 0.0:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return
    total = tlen(d, s, font, track)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    va = "m" if anchor[1] == "m" else ("s" if anchor[1] == "s" else "a")
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill, anchor="l" + va)
        x += d.textlength(ch, font=font) + track


def pop(d, cx, cy, s, size, fill, p, track=0.0, ms=0.6, bold=True):
    sc = ms + (1 - ms) * back(p)
    text(d, (cx, cy), s, F(size * sc, bold), fill, anchor="mm", track=track * sc)


def slam(d, cx, cy, s, size, fill, p, track=0.0):
    sc = 1.55 - 0.55 * eo(p)
    text(d, (cx, cy), s, F(size * sc), fill, anchor="mm", track=track * sc)


# ---------------- sprites ----------------
@lru_cache(maxsize=96)
def glow(rad, color, strength=255):
    yy, xx = np.mgrid[-rad:rad, -rad:rad]
    r = np.sqrt(xx * xx + yy * yy) / rad
    a = np.clip(1 - r, 0, 1) ** 2.2 * strength
    arr = np.zeros((rad * 2, rad * 2, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr)


def pglow(img, cx, cy, rad, color, strength=200):
    g = glow(int(rad), color, strength)
    img.paste(g, (int(cx - rad), int(cy - rad)), g)


@lru_cache(maxsize=64)
def panel(w, h, r, fill, alpha, outline=None, ow=2):
    im = Image.new("RGBA", (max(2, int(w)), max(2, int(h))), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=fill + (alpha,),
                        outline=(outline + (255,)) if outline else None, width=ow)
    return im


# ---------------- backgrounds ----------------
BGS = {}


def bg(key, top, bot, glowc, gx=0.5, gy=0.45, grad=0.9, gstrength=1.0, grid=False):
    if key in BGS:
        return BGS[key]
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(0, 1, W)[None, :, None]
    top = np.array(top, np.float32)
    bot = np.array(bot, np.float32)
    base = top * (1 - yy) + bot * yy
    dx = (xx - gx) * 1.05
    dy = (yy - gy) * 0.85
    dd = np.sqrt(dx * dx + dy * dy) / grad
    haze = np.clip(1 - dd, 0, 1) ** 2.4 * gstrength
    base = base + haze * np.array(glowc, np.float32)
    v = np.clip(1 - (np.sqrt((xx - .5) ** 2 * 1.2 + (yy - .5) ** 2) / 0.78), 0, 1) ** 0.85
    base = base * (0.5 + 0.5 * v)
    if grid:
        g = ((np.arange(W)[None, :] % 72 == 0) | (np.arange(H)[:, None] % 72 == 0)).astype(np.float32)
        base = base + g[..., None] * np.array([9, 12, 18], np.float32)
    BGS[key] = np.clip(base, 0, 255).astype(np.float32)
    return BGS[key]


NOISE = [np.random.default_rng(s).integers(-4, 5, (H, W, 1), dtype=np.int16) for s in range(4)]

# ---------------- captions ----------------
CAPS = [
    (0.20, [("Shein shipped nearly ", WHITE), ("one million", AMBER)],
     [("packages a day into ", WHITE), ("America", AMBER)]),
    (4.05, [("Yet the FTC says that in", WHITE)], [("September 2025", AMBER)]),
    (7.45, [("it had just ", WHITE), ("five phone agents", RED)],
     [("for customer complaints", WHITE)]),
    (11.03, [("Like business stories", WHITE)], [("hiding in plain sight?", CYAN)]),
    (13.66, [("Tap like and subscribe", WHITE)], [("to ", WHITE), ("TITONOMICS", AMBER)]),
    (16.06, [("The agency also alleges Shein", WHITE)], [("filtered negative reviews", RED)]),
    (19.24, [("and misled shoppers about", WHITE)], [("shipping and cotton origins", RED)]),
    (22.79, [("Shein agreed to a proposed", WHITE)], [("$100 million settlement", AMBER)]),
    (26.54, [("without admitting liability", WHITE)]),
    (28.31, [("A judge must still approve it", WHITE)]),
]


def caption_at(t):
    idx = -1
    for i, c in enumerate(CAPS):
        if t >= c[0] - 1e-6:
            idx = i
    return CAPS[idx] if idx >= 0 else None


def draw_captions(d, img, t):
    c = caption_at(t)
    if not c:
        return
    lines = c[1:]
    y0 = 1476 - (len(lines) - 1) * 74
    sc = panel(900, 112 * len(lines) + 52, 26, (4, 6, 11), 150)
    img.paste(sc, (W // 2 - 450, y0 - 64 - (len(lines) - 1) * 37), sc)
    for i, ln in enumerate(lines):
        y = y0 + i * 74 - 42
        total = sum(tlen(d, s, F(50)) for s, _ in ln)
        x = W // 2 - total / 2
        for s, col in ln:
            d.text((x, y), s, font=F(50), fill=col, anchor="lm")
            x += d.textlength(s, font=F(50))


# ---------------- fx helpers ----------------
def ring_wave(d, cx, cy, t, color, n=3, speed=760, rmax=980, width=5):
    for i in range(n):
        r = (t * speed + i * 190) % rmax
        a = 1 - r / rmax
        if a <= 0:
            continue
        col = tuple(int(c * (0.35 + 0.65 * a)) for c in color)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width)


def speedlines(d, t, cx, cy, n, color, seed=3, rmin=260, rmax=980, speed=900, width=3):
    rng = np.random.default_rng(seed)
    ang = rng.random(n) * math.tau
    dly = rng.random(n)
    for i in range(n):
        r0 = (t * speed + dly[i] * rmax) % rmax
        r1 = r0 + 120 + 90 * dly[i]
        if r0 < rmin:
            continue
        a = 1 - r0 / rmax
        col = tuple(int(c * (0.15 + 0.85 * a)) for c in color)
        d.line([cx + r0 * math.cos(ang[i]), cy + r0 * math.sin(ang[i]),
                cx + r1 * math.cos(ang[i]), cy + r1 * math.sin(ang[i])], fill=col, width=width)


def dust(d, t, n, color, seed=5, speed=40, size=(1.5, 3.2), alpha=0.55):
    rng = np.random.default_rng(seed)
    xs = rng.random(n) * W
    ys = rng.random(n) * H
    sp = rng.random(n) * speed + speed * 0.4
    sz = rng.random(n) * (size[1] - size[0]) + size[0]
    for i in range(n):
        y = (ys[i] - t * sp[i]) % H
        c = tuple(int(v * alpha) for v in color)
        d.ellipse([xs[i] - sz[i], y - sz[i], xs[i] + sz[i], y + sz[i]], fill=c)


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def chip(d, cx, cy, label, size=30, fg=WHITE, border=None, fill=(8, 11, 18)):
    w = tlen(d, label, F(size)) + 54
    h = size + 28
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2,
                        fill=fill, outline=border, width=2)
    text(d, (cx, cy), label, F(size), fg, anchor="mm")


def box_iso(d, cx, cy, s, top, side, tape=None):
    d.polygon([(cx - s, cy), (cx, cy + s * .55), (cx, cy + s * 1.55), (cx - s, cy + s * 1.0)], fill=side)
    d.polygon([(cx + s, cy), (cx, cy + s * .55), (cx, cy + s * 1.55), (cx + s, cy + s * 1.0)], fill=tuple(int(c * .78) for c in side))
    d.polygon([(cx - s, cy), (cx, cy - s * .55), (cx + s, cy), (cx, cy + s * .55)], fill=top)
    if tape:
        d.line([cx, cy - s * .52, cx, cy + s * .5], fill=tape, width=3)


# ---------------- mascot ----------------
MASCOT = None


def mascot():
    global MASCOT
    if MASCOT is None:
        MASCOT = Image.open("build/mascot_rgba.png").convert("RGBA")
    return MASCOT


def put_mascot(img, cx, bottom, height, sy=1.0, sx=1.0, bob=0.0, angle=0.0):
    m = mascot()
    hh = int(height * sy)
    ww = int(m.width * height / m.height * sx)
    im = m.resize((max(2, ww), max(2, hh)), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(im, (int(cx - im.width / 2), int(bottom - im.height + bob)), im)


# ---------------- US map ----------------
US_POLY = [(0.04, .06), (.20, .03), (.40, .02), (.62, .02), (.67, .10), (.72, .04),
           (.86, .05), (.94, .16), (.88, .28), (.86, .38), (.89, .52), (.86, .56),
           (.83, .46), (.74, .42), (.62, .43), (.57, .52), (.53, .60), (.49, .49),
           (.34, .44), (.22, .40), (.11, .30), (.03, .14)]


def pts_in_poly(px, py, poly):
    inside = np.zeros(px.shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cond = ((y1 > py) != (y2 > py))
        with np.errstate(divide="ignore", invalid="ignore"):
            xin = (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1
        inside ^= cond & (px < xin)
    return inside


MAP = {}


def us_dots():
    if "us" in MAP:
        return MAP["us"]
    xs = np.arange(0, W, 26)
    ys = np.arange(0, H, 26)
    gx, gy = np.meshgrid(xs, ys)
    px = (gx - 40) / 1000.0
    py = (gy - 410) / 560.0
    m = pts_in_poly(px, py, US_POLY)
    MAP["us"] = (gx[m], gy[m])
    return MAP["us"]


# =========================================================
# BEATS
# =========================================================
def b1(d, img, lt, dur):  # 0-1.40 hook: counter + package storm
    dust(d, lt, 60, CYAN, 21, 90, (1.2, 2.6), 0.5)
    for layer, (sp, s, col, cy0) in enumerate([(560, 24, (13, 22, 38), 0),
                                               (380, 30, (16, 28, 48), 40),
                                               (220, 38, (20, 36, 60), 90)]):
        off = (lt * sp) % 150
        for c in range(5):
            cx = 120 + c * 210 + (layer % 2) * 52
            for r in range(-1, 14):
                y = r * 150 + off + cy0
                if y < -120 or y > H + 120:
                    continue
                for g in (0, 1, 2):  # motion trail
                    box_iso(d, cx, y + g * 16, s, col, tuple(int(v * (0.55 - g * 0.15)) for v in col),
                            CYAN if (r + c) % 7 == 0 and g == 0 else None)
    pglow(img, 540, 900, 470, (4, 8, 16), 235)
    pglow(img, 540, 900, 380, CYAN_D, 70)
    text(d, (540, 650), "PACKAGES SHIPPED PER", F(34), CYAN, track=9)
    v = int(1_000_000 * eo(lt / 1.02))
    sc = 1 + 0.05 * math.sin(lt * 4) * eo(lt / 0.9)
    text(d, (540, 870), f"{v:,}", F(176 * sc), WHITE, anchor="mm")
    text(d, (540, 1020), "EVERY SINGLE DAY", F(38), WHITE, track=8)
    d.line([290, 1072, 790, 1072], fill=CYAN_D, width=3)
    if lt > 0.9:
        speedlines(d, lt - 0.9, 540, 870, 22, CYAN, 8, 300, 1000, 1400, 2)


def b2(d, img, lt, dur):  # 1.40-2.75 AMERICA dot map
    xs, ys = us_dots()
    for i in range(len(xs)):
        if xs[i] < 40 + lt * 1500:
            hot = (i * 37) % 97 == 0
            r = 4.0 if hot else 3.1
            col = AMBER if hot else (CYAN if (i % 11) else (120, 190, 220))
            d.ellipse([xs[i] - r, ys[i] - r, xs[i] + r, ys[i] + r], fill=col)
    for i in range(7):  # inbound streaks
        p = cl(lt * 2.6 - i * 0.09)
        if p <= 0:
            continue
        yy = 480 + i * 108
        x = W - W * (1 - eo(p))
        d.line([x - 260, yy, x, yy], fill=CYAN_D, width=4)
        d.line([x - 90, yy, x, yy], fill=CYAN, width=4)
    text(d, (540, 330), "ONE MILLION PACKAGES A DAY LAND IN", F(26), CYAN, track=5)
    pop(d, 540, 1090, "AMERICA", 132, WHITE, lt / 0.3, track=5, ms=0.82)
    d.line([225, 1152, 225 + 630 * eo(lt / 0.5), 1152], fill=CYAN, width=4)
    text(d, (540, 1200), "7 DAYS A WEEK, EVERY WEEK", F(28), AMBER, track=8)


def b3(d, img, lt, dur):  # 2.75-4.05 24h ring
    cx, cy, R = 540, 880, 262
    p = eo(lt / 1.15)
    for i in range(60):
        a = -math.pi / 2 + i * math.tau / 60 + lt * 0.6
        r1 = R + 36
        r2 = R + (54 if i % 5 == 0 else 44)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(44, 74, 104), width=3)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(28, 56, 86), width=7)
    if p > 0.01:
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * p, fill=CYAN, width=12)
    ang = -math.pi / 2 + math.tau * p
    hx, hy = cx + R * math.cos(ang), cy + R * math.sin(ang)
    pglow(img, hx, hy, 70, CYAN, 190)
    d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=WHITE)
    text(d, (cx, cy - 40), "1,000,000", F(74), WHITE)
    text(d, (cx, cy + 46), "PER 24 HOURS", F(28), CYAN, track=7)
    text(d, (540, 500), "THEY KEEP COMING", F(30), CYAN, track=9)


def b4(d, img, lt, dur):  # 4.05-5.60 FTC
    cx, cy, R = 540, 800, 238
    pglow(img, cx, cy, 400, (20, 60, 90), 90)
    for k in range(2):
        rr = R + k * 26 + (lt * 90 + k * 40) % 40
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(30, 62, 92), width=2)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=WHITE, width=5)
    d.ellipse([cx - R + 24, cy - R + 24, cx + R - 24, cy + R - 24], outline=CYAN, width=2)
    for i in range(56):
        a = -math.pi / 2 + i * math.tau / 56 + lt * 0.35
        r1, r2 = R - 16, R - 34
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(70, 110, 150), width=2)
    text(d, (cx, cy - 6), "FTC", F(150), WHITE, track=3)
    text(d, (cx, cy + 96), "EST. 1914", F(22), (96, 130, 160), track=5)
    # scan line
    sy = cy - R + (lt * 300) % (2 * R)
    d.line([cx - R + 10, sy, cx + R - 10, sy], fill=CYAN, width=3)
    text(d, (540, 1140), "FEDERAL TRADE", F(56), WHITE, track=5)
    text(d, (540, 1202), "COMMISSION", F(56), WHITE, track=5)
    if lt > 0.55:
        chip(d, 540, 480, "ALLEGES", 30, RED, RED)


def b5(d, img, lt, dur):  # 5.60-7.69 calendar
    text(d, (540, 470), "THE FTC SAYS", F(30), CYAN, track=9)
    cw, ch, gap = 96, 84, 14
    x0 = 540 - (7 * cw + 6 * gap) / 2
    y0 = 650
    for r in range(5):
        for c in range(7):
            app = cl(lt * 3.4 - (r * 7 + c) * 0.055)
            if app <= 0.02:
                continue
            x = x0 + c * (cw + gap)
            y = y0 + r * (ch + gap)
            sy = 0.3 + 0.7 * back(app)
            hh = ch * sy
            cy = y + ch / 2
            if r == 3 and c == 4:
                pglow(img, x + cw / 2, cy, 120, RED, 150)
                d.rounded_rectangle([x, cy - hh / 2, x + cw, cy + hh / 2], 9, fill=RED)
                if app > 0.8:
                    text(d, (x + cw / 2, cy), "SEP", F(30), (18, 6, 6))
            else:
                d.rounded_rectangle([x, cy - hh / 2, x + cw, cy + hh / 2], 9, fill=(16, 28, 46),
                                    outline=(34, 58, 84), width=2)
    pop(d, 540, 1200, "SEPTEMBER 2025", 84, WHITE, cl((lt - 0.55) / 0.3), track=2)
    if lt > 1.0:
        chip(d, 540, 1305, "THE DATE ON THE COMPLAINT", 26, GREY, (44, 60, 80))


def b6(d, img, lt, dur):  # 7.69-9.20 the 5
    shake = max(0, 1 - lt / 0.35) * 10
    text(d, (540 + shake * 0.6, 540), "JUST", F(44), CYAN, track=15)
    ring_wave(d, 540, 860, lt, (140, 40, 34), 2, 620, 690, 4)
    pglow(img, 540, 860, 420, RED_D, 220)
    pop(d, 540, 860, "5", 470, WHITE, lt / 0.34, ms=0.45)
    text(d, (540, 1150), "PHONE AGENTS", F(76), WHITE, track=9)
    text(d, (540, 1240), "FOR CUSTOMER COMPLAINTS", F(30), RED, track=7)


def b7(d, img, lt, dur):  # 9.20-11.03 comparison
    text(d, (540, 470), "PACKAGES PER DAY", F(34), CYAN, track=8)
    p = eo(lt / 0.55)
    pglow(img, 120 + 840 * p / 2, 585, 300, AMBER_D, 120)
    d.rounded_rectangle([120, 545, 120 + 840 * p, 625], 10, fill=AMBER)
    v = int(1_000_000 * eo(lt / 0.6))
    text(d, (540, 700), f"{v:,}", F(66), AMBER)
    text(d, (540, 900), "PHONE AGENTS", F(34), CYAN, track=8)
    d.rounded_rectangle([120, 965, 960, 1045], 10, fill=(16, 28, 46))
    d.rounded_rectangle([120, 965, 139, 1045], 4, fill=RED)
    if lt > 0.5:
        text(d, (540, 1110), "5", F(66), RED)
    # magnifier over the invisible bar
    mx = 139 + 60 + math.sin(lt * 3) * 30
    my = 1005 + math.cos(lt * 2.4) * 10
    d.ellipse([mx - 52, my - 52, mx + 52, my + 52], outline=WHITE, width=7)
    d.line([mx + 38, my + 38, mx + 88, my + 88], fill=WHITE, width=11)
    text(d, (540, 1250), "ONE AGENT PER 200,000 PACKAGES", F(28), WHITE, track=4)


def b8(d, img, lt, dur):  # 11.03-13.40 mascot
    # spotlight cone
    pglow(img, 762, 1030, 420, (30, 90, 120), 120)
    speedlines(d, lt, 762, 1040, 26, CYAN, 13, 260, 900, 520, 2)
    rr = 240 + (lt * 70) % 60
    d.ellipse([762 - rr, 1010 - rr, 762 + rr, 1010 + rr], outline=(52, 96, 128), width=3)
    p = cl(lt / 0.34)
    sy = 0.55 + 0.5 * back(p) - 0.05 * math.cos(lt * 7) * p
    put_mascot(img, 762, 1310, 700, sy=sy, bob=math.sin(lt * 4.4) * 9)
    text(d, (80, 520), "HIDING IN", F(66), WHITE, anchor="lm", track=3)
    text(d, (80, 610), "PLAIN", F(66), WHITE, anchor="lm", track=3)
    q = cl((lt - 0.3) / 0.45)
    if q > 0:
        text(d, (80, 700), "SIGHT?", F(66), CYAN, anchor="lm", track=3)
        d.line([80, 750, 80 + 290 * eo(q), 750], fill=CYAN, width=6)
    if lt > 0.9:
        chip(d, 206, 830, "SHEIN", 28, WHITE, CYAN)


def b9(d, img, lt, dur):  # 13.40-16.06 CTA
    pulse = 1 + 0.025 * math.sin(lt * 8)
    pglow(img, 540, 830, 430, AMBER_D, 150)
    for i in range(10):
        a = lt * 1.6 + i * math.tau / 10
        r = 300 + 40 * math.sin(lt * 2 + i)
        x, y = 540 + r * math.cos(a), 830 + r * math.sin(a) * 1.2
        star(d, x, y, 6 + 4 * abs(math.sin(lt * 3 + i)), AMBER_D)
    w, h = 830 * pulse, 480 * pulse
    pn = panel(w, h, 36, (12, 20, 34), 240, AMBER, 4)
    img.paste(pn, (int(540 - w / 2), int(830 - h / 2)), pn)
    text(d, (540, 715), "TAP", F(32), CYAN, track=13)
    text(d, (540, 815), "LIKE &", F(94), WHITE, track=4)
    text(d, (540, 920), "SUBSCRIBE", F(94), AMBER, track=4)
    for i in range(5):
        star(d, 383 + i * 78, 1005, 14, AMBER_D)
    chip(d, 540, 1110, "@TITONOMICS", 30, WHITE, AMBER)


def b10(d, img, lt, dur):  # 16.06-19.24 reviews
    text(d, (540, 470), "REVIEWS THAT", F(30), RED, track=9)
    pop(d, 540, 560, "DISAPPEARED", 84, WHITE, lt / 0.35, track=4)
    for i in range(3):
        p = cl((lt * 3.0) - i * 0.3)
        if p <= 0:
            continue
        y = 700 + i * 212
        gx = 12 * math.sin(lt * 40 + i) * (1 if (lt - 0.55 - i * 0.22) > 0 else 0)
        x0 = 110 + (1 - eo(p)) * -60 + gx
        d.rounded_rectangle([x0, y, x0 + 860, y + 176], 16, fill=(18, 24, 36),
                            outline=(38, 50, 68), width=2)
        for s in range(5):
            star(d, x0 + 46 + s * 40, y + 50, 14, RED if s < 1 else (40, 50, 66))
        d.rounded_rectangle([x0 + 30, y + 92, x0 + 640, y + 112], 8, fill=(44, 56, 74))
        d.rounded_rectangle([x0 + 30, y + 130, x0 + 480, y + 150], 8, fill=(34, 44, 60))
        wp = cl((lt - 0.55 - i * 0.22) / 0.3)
        if wp > 0:
            d.rectangle([x0 + 24, y + 80, x0 + 24 + 662 * eo(wp), y + 158], fill=(6, 8, 13))
        if wp > 0.92:
            d.line([x0 + 620, y + 24, x0 + 700, y + 60], fill=RED, width=8)
            d.line([x0 + 700, y + 24, x0 + 620, y + 60], fill=RED, width=8)
    chip(d, 540, 1350, "FTC ALLEGATION", 26, (240, 140, 130), RED)


def b11(d, img, lt, dur):  # 19.24-22.42 globe
    cx, cy, rx, ry = 540, 810, 300, 330
    pglow(img, cx, cy, 380, (24, 72, 104), 110)
    for k in range(1, 6):  # longitudes
        w = rx * math.cos(lt * 0.5 + k * 0.6)
        d.ellipse([cx - abs(w), cy - ry, cx + abs(w), cy + ry], outline=(34, 62, 88), width=2)
    for k in range(-3, 4):  # latitudes
        yy = cy + k * ry / 3.4
        hw = rx * math.sqrt(max(0.02, 1 - (k / 3.4) ** 2))
        d.arc([cx - hw, yy - 46, cx + hw, yy + 46], 0, 180, fill=(34, 62, 88), width=2)
    p = cl(lt / 1.3)
    if p > 0:
        pts = []
        for k in range(0, 121):
            a = math.radians(200 + 130 * (k / 120))
            pts.append((cx + rx * 0.92 * math.cos(a), cy + ry * 0.92 * math.sin(a)))
        cut = max(2, int(len(pts) * p))
        d.line(pts[:cut], fill=RED, width=6, joint="curve")
        tx, ty = pts[cut - 1]
        pglow(img, tx, ty, 60, RED, 200)
        d.ellipse([tx - 9, ty - 9, tx + 9, ty + 9], fill=WHITE)
    if lt > 0.5:
        chip(d, 236, 460, "SHIPPING", 28, WHITE, CYAN)
    if lt > 1.35:
        chip(d, 830, 460, "COTTON ORIGIN", 28, WHITE, AMBER)
    if lt > 2.0:
        text(d, (540, 1235), "ALLEGEDLY MISLED", F(38), RED, track=6)


def b12(d, img, lt, dur):  # 22.42-24.60 $100M
    ring_wave(d, 540, 860, lt, AMBER, 3, 1100, 1000, 5)
    pglow(img, 540, 860, 430, AMBER_D, 210)
    if lt < 0.5:
        speedlines(d, lt, 540, 860, 20, AMBER, 17, 200, 900, 1500, 2)
    v = int(100_000_000 * eo(lt / 0.8))
    text(d, (540, 700), "PROPOSED SETTLEMENT", F(30), CYAN, track=8)
    text(d, (540, 870), f"${v:,}", F(112), AMBER, anchor="mm")
    text(d, (540, 1010), "ONE HUNDRED MILLION DOLLARS", F(26), WHITE, track=4)


def b13(d, img, lt, dur):  # 24.60-26.54 settlement doc
    p = cl((lt - 0.05) / 0.45)
    doc = Image.new("RGBA", (760, 700), (0, 0, 0, 0))
    dd = ImageDraw.Draw(doc)
    dd.rounded_rectangle([0, 0, 760, 700], 16, fill=(238, 235, 226, 255))
    dd.rectangle([60, 70, 520, 104], fill=(176, 170, 156))
    for i in range(6):
        dd.rectangle([60, 150 + i * 46, 700 - (i % 3) * 90, 172 + i * 46], fill=(198, 192, 178))
    dd.rounded_rectangle([60, 470, 700, 620], 12, fill=(214, 208, 194))
    dd.text((96, 508), "$100,000,000", font=F(64), fill=(24, 24, 28))
    doc = doc.rotate(-4, expand=True, resample=Image.BICUBIC)
    if p > 0:
        drop = (1 - eo(p)) * -420
        hh = int(doc.height * 1.16 * (0.7 + 0.3 * eo(p)))
        sc = doc.resize((int(doc.width * hh / doc.height), hh), Image.LANCZOS)
        pglow(img, 540, 880, 360, (30, 40, 60), 120)
        img.paste(sc, (540 - sc.width // 2, int(860 - sc.height / 2 + drop)), sc)
    if lt > 0.45:
        chip(d, 540, 420, "AGREED — NOT ADMITTED", 28, WHITE, RED)
    text(d, (540, 1210), "SHEIN · FTC", F(26), GREY, track=10)


def b14(d, img, lt, dur):  # 26.54-28.31
    # diagonal red beam
    for i in range(6):
        x = -420 + i * 300 + (lt * 40)
        d.line([x, 0, x + 260, H], fill=(20, 15, 17), width=2)
    for i, (s, col, dly) in enumerate([("WITHOUT", WHITE, 0.0), ("ADMITTING", WHITE, 0.22),
                                      ("LIABILITY", RED, 0.44)]):
        p = cl((lt - dly) / 0.22)
        if p <= 0:
            continue
        sx = 14 * math.sin((lt - dly) * 90) * (1 - p)
        slam(d, 540 + sx, 660 + i * 142, s, 96, col, p, track=4)
    if lt > 0.95:
        sc = 1.0 + 0.1 * (1 - eo(cl((lt - 0.95) / 0.18)))
        st = stamp("NO ADMISSION", 56, RED, -9, 255, sc)
        img.paste(st, (540 - st.width // 2, 1160 - st.height // 2), st)


def stamp(label, size, color, angle, alpha, scale=1.0):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(label, font=F(size))
    w, h = int(tw + 108), int(size + 52)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([4, 4, w - 5, h - 5], 8, outline=color + (alpha,), width=7)
    dd.rounded_rectangle([18, 18, w - 19, h - 19], 4, outline=color + (alpha // 2,), width=2)
    dd.text((w // 2, h // 2), label, font=F(size), fill=color + (alpha,), anchor="mm")
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if scale != 1.0:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.LANCZOS)
    return im


def b15(d, img, lt, dur):  # 28.31-30.00
    pglow(img, 540, 900, 400, (40, 16, 14), 140)
    text(d, (540, 470), "A JUDGE MUST", F(64), WHITE, track=4)
    text(d, (540, 558), "STILL APPROVE IT", F(64), WHITE, track=4)
    d.line([290, 640, 790, 640], fill=(70, 76, 92), width=2)
    if lt > 0.2:
        p = cl((lt - 0.2) / 0.24)
        sc = 2.3 - 1.3 * eo(p)
        st = stamp("PENDING", 96, RED, -8, int(255 * cl(p * 1.7)), sc)
        img.paste(st, (540 - st.width // 2, 900 - st.height // 2), st)
    if lt > 0.55:
        ring_wave(d, 540, 900, lt - 0.55, (90, 30, 26), 2, 700, 800, 4)
        text(d, (540, 1110), "NO VERDICT. NO REFUNDS. NOT YET.", F(24), GREY, track=4)
        chip(d, 540, 1175, "THE CASE IS STILL OPEN", 26, WHITE, (70, 80, 100))


BEATS = [
    (0.00, b1, "CASE 001 — SHEIN", "k1"),
    (1.40, b2, "", "k1"),
    (2.75, b3, "", "k1"),
    (4.05, b4, "THE REGULATOR", "k2"),
    (5.60, b5, "", "k2"),
    (7.69, b6, "THE NUMBER", "k2"),
    (9.20, b7, "", "k2"),
    (11.03, b8, "", "k2"),
    (13.40, b9, "", "k3"),
    (16.06, b10, "THE ALLEGATIONS", "k4"),
    (19.24, b11, "", "k4"),
    (22.42, b12, "THE SETTLEMENT", "k5"),
    (24.60, b13, "", "k5"),
    (26.54, b14, "", "k5"),
    (28.31, b15, "", "k5"),
]
CUTS = [b[0] for b in BEATS][1:]

BGKEYS = {
    "k1": bg("k1", (12, 24, 46), (4, 7, 14), (10, 40, 62), 0.5, 0.48),
    "k2": bg("k2", (8, 20, 40), (3, 5, 11), (8, 44, 64), 0.5, 0.42),
    "k3": bg("k3", (28, 20, 12), (6, 5, 8), (58, 40, 14), 0.5, 0.45),
    "k4": bg("k4", (30, 10, 14), (7, 4, 8), (66, 14, 18), 0.5, 0.44),
    "k5": bg("k5", (18, 16, 26), (5, 4, 8), (48, 32, 16), 0.5, 0.46),
}
ACCENT = {"k1": CYAN, "k2": CYAN, "k3": AMBER, "k4": RED, "k5": AMBER}

SHAKES = [(0.00, 16, 5.0), (7.69, 20, 4.0), (22.42, 22, 4.0), (28.52, 18, 3.4), (26.9, 8, 6.0)]


def shake_at(t):
    x = y = 0.0
    for (st, amp, dec) in SHAKES:
        dt = t - st
        if 0 <= dt < 0.7:
            a = amp * math.exp(-dt * dec)
            x += a * math.sin(dt * 70)
            y += a * math.cos(dt * 93)
    return x, y


def camera(img, zoom, dx, dy):
    if abs(zoom - 1) < 0.002 and abs(dx) < 0.6 and abs(dy) < 0.6:
        return img
    w, h = W / zoom, H / zoom
    x0 = (W - w) / 2 + dx
    y0 = (H - h) / 2 + dy
    x0 = cl(x0, 0, W - w)
    y0 = cl(y0, 0, H - h)
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)


def chrome(img, d, t, kicker, accent):
    d.rectangle([0, 0, W, 6], fill=(18, 22, 32))
    d.rectangle([0, 0, int(W * (t / DUR)), 6], fill=accent)
    text(d, (W // 2, 92), "T I T O N O M I C S", F(32), (176, 172, 162), track=2)
    d.line([W // 2 - 116, 122, W // 2 + 116, 122], fill=(52, 50, 46), width=2)
    if kicker:
        kw = tlen(d, kicker.upper(), F(26), 6)
        pn = panel(kw + 56, 50, 25, (4, 6, 11), 170)
        img.paste(pn, (int(W // 2 - pn.width / 2), 150), pn)
        text(d, (W // 2, 175), kicker.upper(), F(26), (166, 174, 190), track=6)


def render_frame(t):
    i = 0
    for k, b in enumerate(BEATS):
        if t >= b[0] - 1e-9:
            i = k
    st, fn, kick, key = BEATS[i]
    end = BEATS[i + 1][0] if i + 1 < len(BEATS) else DUR
    lt = t - st
    dur = end - st
    img = Image.fromarray(BGKEYS[key].astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    fn(d, img, lt, dur)

    # camera: slow push + impact shake + whip on cut
    zoom = 1.03 + 0.05 * (lt / max(0.2, dur))
    if lt < 0.12:
        zoom += 0.06 * (1 - lt / 0.12)
    sx, sy = shake_at(t)
    img = camera(img, zoom, sx, sy)
    d = ImageDraw.Draw(img)

    # cut flash
    for c in CUTS:
        dt = t - c
        if 0 <= dt < 0.08:
            a = 1 - dt / 0.08
            lay = Image.new("RGBA", (W, H), (255, 255, 255, int(26 * a)))
            img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
            d = ImageDraw.Draw(img)

    chrome(img, d, t, kick, ACCENT[key])
    draw_captions(d, img, t)

    arr = np.asarray(img, np.int16) + NOISE[(int(t * FPS) // 2) % 4]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def main():
    os.makedirs("build", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        for ts in [float(x) for x in sys.argv[2:]]:
            render_frame(ts).save(f"build/v2_{ts:05.2f}.png")
        print("previews done")
        return
    out = "build/video2_silent.mp4"
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        p.stdin.write(render_frame(f / FPS).tobytes())
        if f % 120 == 0:
            print(f"frame {f}/{NFRAMES}", flush=True)
    p.stdin.close()
    p.wait()
    print("done", p.returncode)


if __name__ == "__main__":
    main()
