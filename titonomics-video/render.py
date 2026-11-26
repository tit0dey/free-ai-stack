"""
TITONOMICS — code-only cinematic short renderer.
1080x1920 / 30fps / H.264. No stock footage: every visual is drawn in code.
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
NAVY = (11, 17, 30)
NAVY2 = (16, 25, 43)
CHAR = (19, 21, 27)
STEEL = (138, 147, 165)
DIM = (86, 96, 114)
GOLD = (198, 160, 42)
GOLD_L = (236, 205, 118)
WHITE = (243, 241, 235)
RED = (190, 68, 58)


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):  # ease out cubic
    x = cl(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x)
    return 3 * x * x - 2 * x * x * x


def back_out(x, s=1.9):
    x = cl(x) - 1
    return x * x * ((s + 1) * x + s) + 1


@lru_cache(maxsize=512)
def F(size, bold=True):
    size = max(6, int(size))
    return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


# ---------------- text ----------------
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


def fit_text(d, xy, s, fill, size, maxw=880, track=0.0, bold=True, anchor="mm"):
    while size > 20 and tlen(d, s, F(size, bold), track) > maxw:
        size -= 2
    text(d, xy, s, F(size, bold), fill, anchor=anchor, track=track)


def pop_text(d, cx, cy, s, size, fill, p, track=0.0, ms=0.70, bold=True):
    sc = ms + (1 - ms) * back_out(p)
    f = F(size * sc, bold)
    text(d, (cx, cy), s, f, fill, anchor="mm", track=track * sc)


# ---------------- sprites ----------------
@lru_cache(maxsize=64)
def glow(rad, color, strength=255):
    s = rad * 2
    y, x = np.mgrid[-rad:rad, -rad:rad]
    r = np.sqrt(x * x + y * y) / rad
    a = np.clip(1 - r, 0, 1) ** 2.4 * strength
    arr = np.zeros((s, s, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr)


@lru_cache(maxsize=64)
def panel(w, h, r, fill, alpha, outline=None, ow=2):
    im = Image.new("RGBA", (max(2, int(w)), max(2, int(h))), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], r,
                        fill=fill + (alpha,), outline=(outline + (255,)) if outline else None, width=ow)
    return im


def paste_glow(img, cx, cy, rad, color, strength=200):
    g = glow(rad, color, strength)
    img.paste(g, (int(cx - rad), int(cy - rad)), g)


# ---------------- mascot ----------------
def mascot():
    return Image.open("build/mascot_rgba.png").convert("RGBA")


MASCOT = None


def put_mascot(img, cx, bottom, height, scale=1.0, bob=0.0, flip=False, alpha=1.0):
    global MASCOT
    if MASCOT is None:
        MASCOT = mascot()
    hh = int(height * scale)
    ww = int(MASCOT.width * hh / MASCOT.height)
    m = MASCOT.resize((max(2, ww), max(2, hh)), Image.LANCZOS)
    if flip:
        m = m.transpose(Image.FLIP_LEFT_RIGHT)
    if alpha < 1.0:
        a = m.getchannel("A").point(lambda v: int(v * alpha))
        m.putalpha(a)
    img.paste(m, (int(cx - ww / 2), int(bottom - hh + bob)), m)


# ---------------- background ----------------
def build_bg():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    top = np.array([12, 18, 33], np.float32)
    bot = np.array([7, 9, 16], np.float32)
    base = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    # warm gold haze low-center
    cx, cy, rr = 0.5, 0.52, 0.75
    d = np.sqrt(((x - cx) * 1.1) ** 2 + ((y - cy) * 0.85) ** 2) / rr
    haze = np.clip(1 - d, 0, 1) ** 2.6
    base = base + haze[..., None] * np.array([26, 20, 6], np.float32)
    # vignette
    v = np.clip(1 - (np.sqrt(((x - .5) * 1.25) ** 2 + ((y - .5) * 1.0) ** 2) / 0.78), 0, 1) ** 0.9
    base = base * (0.55 + 0.45 * v[..., None])
    return base.astype(np.float32)


BG = build_bg()
NOISE = [np.random.default_rng(s).integers(-4, 5, (H, W, 1), dtype=np.int16) for s in range(5)]

# ---------------- captions ----------------
CAPS = [
    (0.20, [("Shein shipped nearly ", WHITE), ("one million", GOLD_L)],
     [("packages a day into ", WHITE), ("America", GOLD_L)]),
    (4.05, [("Yet the FTC says that in", WHITE)], [("September 2025", GOLD_L)]),
    (7.45, [("it had just ", WHITE), ("five phone agents", GOLD_L)],
     [("for customer complaints", WHITE)]),
    (11.03, [("Like business stories", WHITE)], [("hiding in plain sight?", WHITE)]),
    (13.66, [("Tap like and subscribe", WHITE)], [("to ", WHITE), ("TITONOMICS", GOLD_L)]),
    (16.06, [("The agency also alleges Shein", WHITE)], [("filtered negative reviews", GOLD_L)]),
    (19.24, [("and misled shoppers about", WHITE)], [("shipping and cotton origins", GOLD_L)]),
    (22.79, [("Shein agreed to a proposed", WHITE)], [("$100 million settlement", GOLD_L)]),
    (26.54, [("without admitting liability", WHITE)]),
    (28.31, [("A judge must still approve it", WHITE)]),
]


def caption_at(t):
    starts = [c[0] for c in CAPS]
    idx = -1
    for i, s in enumerate(starts):
        if t >= s - 1e-6:
            idx = i
    return CAPS[idx] if idx >= 0 else None


def draw_captions(d, img, t):
    c = caption_at(t)
    if not c:
        return
    lines = c[1:]
    y0 = 1470 - (len(lines) - 1) * 76
    scrim = panel(880, 118 * len(lines) + 54, 26, (6, 9, 16), 128)
    img.paste(scrim, (W // 2 - scrim.width // 2, y0 - 62 - (len(lines) - 1) * 38), scrim)
    for i, ln in enumerate(lines):
        y = y0 + i * 76 - 40
        total = sum(tlen(d, s, F(50)) for s, _ in ln)
        x = W // 2 - total / 2
        for s, col in ln:
            d.text((x, y), s, font=F(50), fill=col, anchor="lm")
            x += d.textlength(s, font=F(50))


# ---------------- chrome ----------------
def chrome(img, d, t, kicker=None):
    # progress bar
    d.rectangle([0, 0, W, 7], fill=(24, 30, 44))
    d.rectangle([0, 0, int(W * (t / DUR)), 7], fill=GOLD)
    # brand
    text(d, (W // 2, 96), "T I T O N O M I C S", F(33), (188, 180, 160), track=2)
    d.line([W // 2 - 120, 128, W // 2 + 120, 128], fill=(70, 62, 40), width=2)
    if kicker:
        kw = tlen(d, kicker.upper(), F(26), 6)
        pn = panel(kw + 56, 50, 25, (6, 9, 16), 150)
        img.paste(pn, (int(W // 2 - pn.width / 2), 157), pn)
        text(d, (W // 2, 182), kicker.upper(), F(26), (150, 158, 176), track=6)


# ---------------- small shapes ----------------
def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def chip(d, cx, cy, label, size=30, fg=GOLD_L, border=GOLD, pad=(26, 14), fill=(14, 20, 34)):
    w = tlen(d, label, F(size)) + pad[0] * 2
    h = size + pad[1] * 2
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2,
                        fill=fill, outline=border, width=2)
    text(d, (cx, cy), label, F(size), fg, anchor="mm")


# =========================================================
# BEATS
# =========================================================
def b1(d, img, lt, dur):  # 0.00-1.40  counter + package columns
    off = (lt * 300) % 112
    for c in range(7):
        cx = 54 + c * 162
        for r in range(-1, 18):
            y = r * 112 + off - 60
            if y < -70 or y > H + 70:
                continue
            d.rounded_rectangle([cx - 33, y - 33, cx + 33, y + 33], 9, fill=(19, 25, 37))
            d.line([cx - 24, y - 22, cx + 24, y - 22], fill=(44, 53, 70), width=3)
            if (r + c) % 5 == 0:
                d.line([cx, y - 33, cx, y + 33], fill=(76, 63, 28), width=4)
    v = int(1_000_000 * eo(lt / 1.05))
    paste_glow(img, 540, 880, 460, (5, 8, 14), 235)
    paste_glow(img, 540, 880, 430, GOLD, 78)
    text(d, (540, 640), "PACKAGES SHIPPED PER", F(34), STEEL, track=8)
    pop_text(d, 540, 860, f"{v:,}", 172, GOLD_L, lt / 0.45)
    text(d, (540, 1010), "EVERY SINGLE DAY", F(38), WHITE, track=7)
    d.line([300, 1060, 780, 1060], fill=(92, 78, 38), width=3)


def b2(d, img, lt, dur):  # 1.40-2.75 AMERICA
    for iy in range(0, 24):
        for ix in range(0, 21):
            x = 30 + ix * 51
            y = 300 + iy * 51
            dist = math.hypot(x - 540, (y - 830) * 0.62)
            if dist < lt * 1500:
                col = GOLD if (ix * 7 + iy * 3) % 11 == 0 else (50, 62, 84)
                r = 3.4 if (ix * 7 + iy * 3) % 11 == 0 else 2.6
                d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # inbound streaks
    for i in range(6):
        yy = 560 + i * 92
        p = cl((lt * 3.4 - i * 0.12))
        if p <= 0:
            continue
        x2 = 1080 - 1080 * (1 - eo(p))
        d.line([x2 - 200, yy, x2, yy], fill=(84, 70, 34), width=3)
    paste_glow(img, 540, 880, 420, GOLD, 60)
    text(d, (540, 700), "ONE MILLION PACKAGES A DAY LAND IN", F(27), STEEL, track=4)
    pop_text(d, 540, 880, "AMERICA", 158, WHITE, lt / 0.32, track=5, ms=0.78)
    text(d, (540, 1030), "7 DAYS A WEEK", F(32), GOLD, track=9)


def b3(d, img, lt, dur):  # 2.75-4.05 24h clock ring
    cx, cy, R = 540, 880, 258
    p = eo(lt / 1.15)
    for i in range(48):
        a = -math.pi / 2 + i * math.pi / 24
        r1 = R + 34
        r2 = R + (52 if i % 4 == 0 else 44)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(52, 60, 78), width=3)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(34, 43, 60), width=6)
    if p > 0.01:
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * p, fill=GOLD, width=11)
    ang = -math.pi / 2 + 2 * math.pi * p
    hx, hy = cx + R * math.cos(ang), cy + R * math.sin(ang)
    d.ellipse([hx - 11, hy - 11, hx + 11, hy + 11], fill=GOLD_L)
    text(d, (cx, cy - 58), "1,000,000", F(70), WHITE)
    text(d, (cx, cy + 26), "PER 24 HOURS", F(30), GOLD, track=7)
    text(d, (540, 520), "THEY KEEP COMING", F(30), STEEL, track=8)


def b4(d, img, lt, dur):  # 4.05-5.60 FTC seal
    cx, cy, R = 540, 800, 236
    p = eo(lt / 0.9)
    paste_glow(img, cx, cy, 380, GOLD, 46)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=GOLD, width=5)
    d.ellipse([cx - R + 26, cy - R + 26, cx + R - 26, cy + R - 26], outline=(96, 80, 38), width=3)
    for i in range(60):
        a = -math.pi / 2 + i * math.pi / 30 + lt * 0.5
        r1, r2 = R - 14, R - 34
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(86, 72, 36), width=2)
    pop_text(d, cx, cy - 10, "FTC", 160, GOLD_L, lt / 0.4, track=4)
    text(d, (cx, cy + 110), "EST. 1914", F(24), (110, 96, 60), track=5)
    text(d, (540, 1120), "FEDERAL TRADE", F(58), WHITE, track=5)
    text(d, (540, 1184), "COMMISSION", F(58), WHITE, track=5)
    if lt > 0.65:
        chip(d, 540, 470, "ALLEGES", 30)


def b5(d, img, lt, dur):  # 5.60-7.69 September 2025 calendar
    text(d, (540, 470), "THE FTC SAYS", F(32), STEEL, track=8)
    # calendar
    cw, ch, gap = 96, 86, 14
    cols, rows = 7, 5
    total_w = cols * cw + (cols - 1) * gap
    x0 = 540 - total_w / 2
    y0 = 640
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cw + gap)
            y = y0 + r * (ch + gap)
            hot = (r == 3 and c == 4)
            app = cl((lt * 2.2) - (r * 0.06 + c * 0.02))
            if app <= 0.02:
                continue
            if hot:
                paste_glow(img, x + cw / 2, y + ch / 2, 130, GOLD, 130)
                d.rounded_rectangle([x, y, x + cw, y + ch], 10, fill=GOLD)
                text(d, (x + cw / 2, y + ch / 2), "SEP", F(32), (20, 16, 8))
            else:
                d.rounded_rectangle([x, y, x + cw, y + ch], 10, fill=(22, 29, 43),
                                    outline=(42, 52, 70), width=2)
    pop_text(d, 540, 1200, "SEPTEMBER 2025", 92, WHITE, cl((lt - 0.7) / 0.4), track=3)
    if lt > 1.15:
        chip(d, 540, 1310, "THE DATE ON THE COMPLAINT", 26, fill=(12, 18, 30))


def b6(d, img, lt, dur):  # 7.69-9.20 GIANT 5
    text(d, (540, 560), "JUST", F(46), STEEL, track=14)
    paste_glow(img, 540, 850, 420, GOLD, 120)
    pop_text(d, 540, 850, "5", 470, GOLD_L, lt / 0.42, ms=0.55)
    text(d, (540, 1140), "PHONE AGENTS", F(78), WHITE, track=8)
    text(d, (540, 1232), "FOR CUSTOMER COMPLAINTS", F(30), STEEL, track=6)
    for i in range(3):
        rr = 260 + i * 46 + (lt * 130) % 60
        d.ellipse([540 - rr, 850 - rr, 540 + rr, 850 + rr], outline=(70, 60, 32), width=2)


def b7(d, img, lt, dur):  # 9.20-11.03 comparison
    text(d, (540, 480), "PACKAGES PER DAY", F(34), STEEL, track=7)
    bw = 840
    p = eo(lt / 0.5)
    d.rounded_rectangle([120, 545, 120 + bw * p, 625], 12, fill=GOLD)
    text(d, (540, 690), "1,000,000", F(64), GOLD_L)
    text(d, (540, 900), "PHONE AGENTS", F(34), STEEL, track=7)
    d.rounded_rectangle([120, 965, 960, 1045], 12, fill=(24, 30, 44))
    d.rounded_rectangle([120, 965, 138, 1045], 4, fill=(178, 66, 56))
    if lt > 0.45:
        text(d, (540, 1110), "5", F(64), (222, 120, 110))
    text(d, (300, 1045 - 108), "WHICH IS BASICALLY NOTHING", F(22), (128, 90, 86), track=4)
    text(d, (540, 1250), "ONE AGENT PER 200,000 PACKAGES", F(28), WHITE, track=4)


def b8(d, img, lt, dur):  # 11.03-13.40 mascot reveal
    paste_glow(img, 762, 1040, 400, GOLD, 58)
    rr = 235 + (lt * 80) % 60
    d.ellipse([762 - rr, 1010 - rr, 762 + rr, 1010 + rr], outline=(78, 66, 34), width=3)
    sc = 0.94 + 0.06 * eo(lt / 0.4) + 0.012 * math.sin(lt * 6)
    put_mascot(img, 762, 1300, 690, scale=sc, bob=math.sin(lt * 4.2) * 8)
    text(d, (80, 520), "HIDING IN", F(66), WHITE, anchor="lm", track=3)
    text(d, (80, 610), "PLAIN", F(66), WHITE, anchor="lm", track=3)
    p = cl((lt - 0.35) / 0.5)
    if p > 0:
        text(d, (80, 700), "SIGHT?", F(66), GOLD_L, anchor="lm", track=3)
        d.line([80, 748, 80 + 280 * eo(p), 748], fill=GOLD, width=6)
    if lt > 0.9:
        chip(d, 200, 830, "SHEIN", 28)


def b9(d, img, lt, dur):  # 13.40-16.06 CTA
    pulse = 1 + 0.02 * math.sin(lt * 9)
    paste_glow(img, 540, 820, 420, GOLD, 70)
    w, h = 862 * pulse, 500 * pulse
    pn = panel(w, h, 38, (13, 19, 33), 235, GOLD, 4)
    img.paste(pn, (int(540 - w / 2), int(820 - h / 2)), pn)
    text(d, (540, 700), "TAP", F(34), STEEL, track=12)
    text(d, (540, 800), "LIKE &", F(96), WHITE, track=4)
    text(d, (540, 910), "SUBSCRIBE", F(96), GOLD_L, track=4)
    for i in range(5):
        star(d, 380 + i * 90, 1000, 15, (70, 60, 34))
    chip(d, 540, 1110, "@TITONOMICS", 30)


def b10(d, img, lt, dur):  # 16.06-19.24 filtered reviews
    text(d, (540, 470), "REVIEWS THAT", F(30), STEEL, track=8)
    pop_text(d, 540, 560, "DISAPPEARED", 86, GOLD_L, lt / 0.4, track=4)
    for i in range(3):
        y = 700 + i * 210
        p = cl((lt * 3.2) - i * 0.35)
        if p <= 0:
            continue
        x0 = 110 + (1 - eo(p)) * 40
        d.rounded_rectangle([x0, y, x0 + 860, y + 176], 18, fill=(20, 27, 41),
                            outline=(44, 54, 72), width=2)
        for s in range(5):
            star(d, x0 + 46 + s * 40, y + 50, 14, (132, 62, 54) if s < 1 else (46, 54, 70))
        d.rounded_rectangle([x0 + 30, y + 92, x0 + 640, y + 112], 8, fill=(46, 55, 72))
        d.rounded_rectangle([x0 + 30, y + 130, x0 + 480, y + 150], 8, fill=(38, 46, 62))
        # redaction sweep
        wp = cl((lt - 0.55 - i * 0.22) / 0.35)
        if wp > 0:
            d.rectangle([x0 + 24, y + 80, x0 + 24 + 660 * eo(wp), y + 158], fill=(9, 12, 20))
        if wp > 0.95:
            d.line([x0 + 620, y + 24, x0 + 700, y + 60], fill=RED, width=7)
            d.line([x0 + 700, y + 24, x0 + 620, y + 60], fill=RED, width=7)
    chip(d, 540, 1350, "FTC ALLEGATION", 26, fg=(212, 130, 120), border=(140, 62, 54))


def b11(d, img, lt, dur):  # 19.24-22.42 origins / shipping
    cx, cy, rx, ry = 540, 800, 280, 330
    paste_glow(img, cx, cy, 380, GOLD, 52)
    for iy in range(-9, 10):
        for ix in range(-7, 8):
            if (ix / 6.6) ** 2 + (iy / 8.2) ** 2 > 1:
                continue
            x = cx + ix * 44
            y = cy + iy * 42
            app = cl(lt * 2.8 - (abs(ix) + abs(iy)) * 0.045)
            if app <= 0.02:
                continue
            hotc = (ix * 5 + iy * 7) % 13 == 0
            r = 4.2 if hotc else 3.0
            d.ellipse([x - r, y - r, x + r, y + r],
                      fill=GOLD if hotc else (52, 64, 86))
    # shipping route
    p = cl(lt / 1.4)
    if p > 0:
        n = max(2, int(150 * p))
        pts = []
        for k in range(n + 1):
            a = math.radians(198 + 132 * (k / 150))
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        d.line(pts, fill=GOLD, width=6, joint="curve")
        tx, ty = pts[-1]
        d.ellipse([tx - 12, ty - 12, tx + 12, ty + 12], fill=GOLD_L)
        paste_glow(img, tx, ty, 70, GOLD, 150)
    if lt > 0.55:
        chip(d, 250, 470, "SHIPPING", 28)
        d.line([330, 502, 372, 560], fill=(80, 70, 40), width=3)
    if lt > 1.45:
        chip(d, 820, 470, "COTTON ORIGIN", 28)
        d.line([790, 502, 748, 566], fill=(80, 70, 40), width=3)
    if lt > 2.05:
        text(d, (540, 1215), "ALLEGEDLY MISLED", F(38), (214, 132, 122), track=6)


def b12(d, img, lt, dur):  # 22.42-24.60 $100,000,000
    v = int(100_000_000 * eo(lt / 0.85))
    paste_glow(img, 540, 850, 470, GOLD, 110)
    for i in range(3):
        rr = 200 + ((lt * 400 + i * 120) % 360)
        d.ellipse([540 - rr, 850 - rr, 540 + rr, 850 + rr],
                  outline=(max(20, 90 - int(rr / 6)), max(16, 74 - int(rr / 7)), 34), width=3)
    text(d, (540, 700), "PROPOSED SETTLEMENT", F(30), STEEL, track=7)
    pop_text(d, 540, 860, f"${v:,}", 118, GOLD_L, lt / 0.3, track=-1)
    text(d, (540, 1010), "ONE HUNDRED MILLION DOLLARS", F(27), WHITE, track=4)


def b13(d, img, lt, dur):  # 24.60-26.54 settlement doc
    p = cl((lt - 0.1) / 0.5)
    doc = Image.new("RGBA", (760, 700), (0, 0, 0, 0))
    dd = ImageDraw.Draw(doc)
    dd.rounded_rectangle([0, 0, 760, 700], 18, fill=(232, 228, 216, 255))
    dd.rectangle([60, 70, 520, 104], fill=(178, 172, 158))
    for i in range(6):
        dd.rectangle([60, 150 + i * 46, 700 - (i % 3) * 90, 172 + i * 46], fill=(196, 190, 176))
    dd.rounded_rectangle([60, 470, 700, 620], 12, fill=(214, 208, 194))
    dd.text((96, 508), "$100,000,000", font=F(64), fill=(30, 30, 34))
    doc = doc.rotate(-4, expand=True, resample=Image.BICUBIC)
    if p > 0:
        hh = int(doc.height * 1.18 * (0.6 + 0.4 * eo(p)))
        sc = doc.resize((int(doc.width * hh / doc.height), hh), Image.LANCZOS)
        img.paste(sc, (540 - sc.width // 2, 860 - sc.height // 2), sc)
    if lt > 0.5:
        chip(d, 540, 430, "AGREED, NOT ADMITTED", 28)


def b14(d, img, lt, dur):  # 26.54-28.31 without admitting liability
    for i in range(6):
        d.line([110, 340 + i * 250, 970, 340 + i * 250], fill=(23, 28, 39), width=2)
    lines = [("WITHOUT", WHITE, 0.00), ("ADMITTING", WHITE, 0.28), ("LIABILITY", GOLD_L, 0.56)]
    for i, (s, col, dly) in enumerate(lines):
        p = cl((lt - dly) / 0.28)
        if p <= 0:
            continue
        pop_text(d, 540, 650 + i * 140, s, 96, col, p, track=4, ms=0.82)
    if lt > 1.02:
        st = Image.new("RGBA", (620, 170), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 616, 166], 10, outline=(190, 68, 58, 255), width=7)
        sd.text((310, 85), "NO ADMISSION", font=F(58), fill=(206, 92, 80, 255), anchor="mm")
        st = st.rotate(-9, expand=True, resample=Image.BICUBIC)
        sc = 1.0 + 0.06 * (1 - eo(cl((lt - 1.02) / 0.2)))
        st = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS)
        img.paste(st, (540 - st.width // 2, 1145 - st.height // 2), st)


def stamp_sprite(label, size=64, color=(196, 74, 62), pad=(54, 26), angle=-8, alpha=255, scale=1.0):
    tmp = Image.new("RGBA", (10, 10))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(label, font=F(size))
    w = int(tw + pad[0] * 2)
    h = int(size + pad[1] * 2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([4, 4, w - 5, h - 5], 8, outline=color + (alpha,), width=7)
    dd.rounded_rectangle([18, 18, w - 19, h - 19], 4, outline=color + (alpha // 2,), width=2)
    dd.text((w // 2, h // 2), label, font=F(size), fill=color + (alpha,), anchor="mm")
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if scale != 1.0:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.LANCZOS)
    return im


def b15(d, img, lt, dur):  # 28.31-30.00 judge must approve
    paste_glow(img, 540, 900, 360, GOLD, 40)
    text(d, (540, 470), "A JUDGE MUST", F(66), WHITE, track=4)
    text(d, (540, 560), "STILL APPROVE IT", F(66), GOLD_L, track=4)
    # bench line
    d.line([300, 640, 780, 640], fill=(78, 66, 36), width=3)
    if lt > 0.18:
        p = cl((lt - 0.18) / 0.26)
        sc = 2.15 - 1.15 * eo(p)
        al = int(255 * cl(p * 1.6))
        st = stamp_sprite("PENDING", 96, (200, 82, 68), angle=-8, alpha=al, scale=sc)
        img.paste(st, (540 - st.width // 2, 900 - st.height // 2), st)
    if lt > 0.55:
        text(d, (540, 1110), "NO VERDICT. NO REFUNDS. NOT YET.", F(24), DIM, track=4)
        chip(d, 540, 1175, "SETTLEMENT IS PROPOSED", 26)
    if lt > 0.95:
        d.line([420, 1245, 660, 1245], fill=(70, 60, 36), width=2)


BEATS = [
    (0.00, b1, "CASE 001 — SHEIN"),
    (1.40, b2, ""),
    (2.75, b3, ""),
    (4.05, b4, "THE REGULATOR"),
    (5.60, b5, ""),
    (7.69, b6, "THE NUMBER"),
    (9.20, b7, ""),
    (11.03, b8, ""),
    (13.40, b9, ""),
    (16.06, b10, "THE ALLEGATIONS"),
    (19.24, b11, ""),
    (22.42, b12, "THE SETTLEMENT"),
    (24.60, b13, ""),
    (26.54, b14, ""),
    (28.31, b15, ""),
]
CUTS = [b[0] for b in BEATS][1:]


def render_frame(t):
    i = 0
    for k, (st, fn, kick) in enumerate(BEATS):
        if t >= st - 1e-9:
            i = k
    st, fn, kick = BEATS[i]
    img = Image.fromarray(BG.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    fn(d, img, t - st, (BEATS[i + 1][0] if i + 1 < len(BEATS) else DUR) - st)
    # cut flash
    for c in CUTS:
        dt = t - c
        if 0 <= dt < 0.10:
            a = 1 - dt / 0.10
            d.rectangle([0, 0, W, H], fill=None)
            lay = Image.new("RGBA", (W, H), (255, 246, 224, int(34 * a)))
            img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
            d = ImageDraw.Draw(img)
    chrome(img, d, t, kick)
    draw_captions(d, img, t)
    # grain
    arr = np.asarray(img, np.int16)
    arr = arr + NOISE[(int(t * FPS) // 2) % 5]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    return img


def main():
    os.makedirs("build", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        for ts in [float(x) for x in sys.argv[2:]]:
            render_frame(ts).save(f"build/prev_{ts:05.2f}.png")
            print("saved", ts)
        return
    out = "build/video_silent.mp4"
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        p.stdin.write(render_frame(f / FPS).tobytes())
        if f % 60 == 0:
            print(f"frame {f}/{NFRAMES}", flush=True)
    p.stdin.close()
    p.wait()
    print("video done", out, p.returncode)


if __name__ == "__main__":
    main()
