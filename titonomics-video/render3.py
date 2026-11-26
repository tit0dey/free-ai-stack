"""
TITONOMICS — "Paper Doodle" episode engine.
Paper texture, hand-drawn ink strokes that draw themselves, marker swipes, sticky notes,
stamps, sticker mascot. 1080x1920 @30. Sentences are timed from the real TTS clips.
"""
import os, sys, json, math, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H, FPS = 1080, 1920, 30
FF = imageio_ffmpeg.get_ffmpeg_exe()
FD = "/usr/share/fonts/truetype/dejavu/"
AF = "../assets/fonts/"

INK = (24, 21, 18)
INK2 = (58, 52, 44)
PAPER = (247, 242, 230)
PAPER_D = (238, 231, 214)
RED = (222, 58, 44)
GREEN = (56, 178, 84)
YELLOW = (255, 212, 60)
BLUE = (38, 106, 214)
WHITE = (252, 250, 244)

TL = json.load(open("build/timeline.json"))
DUR = TL["total"]
NFRAMES = int(round(DUR * FPS))
S = TL["sentences"]


def sstart(i):
    return S[i]["start"]


def send(i):
    return S[i]["end"]


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):
    x = cl(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x)
    return 3 * x * x - 2 * x * x * x


def overshoot(x, s=2.6):
    x = cl(x) - 1
    return x * x * ((s + 1) * x + s) + 1


@lru_cache(maxsize=512)
def F(size, kind="ab"):
    f = {"ab": "archivo-black-latin-400-normal.ttf",
         "pm": "permanent-marker-latin-400-normal.ttf",
         "ban": "bangers-latin-400-normal.ttf",
         "dj": None}[kind]
    path = (AF + f) if f else (FD + "DejaVuSans-Bold.ttf")
    return ImageFont.truetype(path, max(6, int(size)))


def tl(d, s, font):
    return d.textlength(s, font=font)


def text(d, xy, s, font, fill, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def fit(d, xy, s, size, fill, kind="ab", maxw=900, anchor="mm"):
    while size > 18 and tl(d, s, F(size, kind)) > maxw:
        size -= 2
    text(d, xy, s, F(size, kind), fill, anchor)


# ---------------- paper background ----------------
def build_paper():
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(0, 1, W)[None, :, None]
    base = np.array([250, 246, 236], np.float32) * (1 - yy * 0.10) + np.array([236, 228, 210], np.float32) * (yy * 0.10)
    base = base + np.zeros((1, W, 1), np.float32)
    # warm bloom top-left
    d = np.sqrt((xx - 0.25) ** 2 + (yy - 0.2) ** 2)
    base = base + np.clip(1 - d / 0.9, 0, 1).reshape(H, W, 1) * np.array([5, 4, 1], np.float32)
    # dot grid
    gy, gx = np.mgrid[0:H, 0:W]
    dots = ((gx % 44 < 2) & (gy % 44 < 2)).astype(np.float32)
    base = base - dots[..., None] * np.array([12, 13, 12], np.float32)
    # vignette
    v = np.clip(1 - (np.sqrt((xx - .5) ** 2 * 1.15 + (yy - .5) ** 2) / 0.82), 0, 1) ** 0.8
    base = base * (0.93 + 0.07 * v)
    return base.astype(np.float32)


PAPER_IMG = build_paper()
FIBERS = [np.random.default_rng(s).integers(-6, 7, (H, W, 1), dtype=np.int16) for s in range(4)]


# ---------------- rough drawing ----------------
def _wob(pts, seed, amp=1.3):
    rng = np.random.default_rng(seed)
    return [(x + rng.normal(0, amp), y + rng.normal(0, amp)) for x, y in pts]


def segments(p0, p1, n=9):
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]


def stroke(d, pts, prog, seed, color=INK, w=5, jitter=1.3, double=True):
    if prog <= 0:
        return
    k = max(2, int(len(pts) * cl(prog)))
    base = _wob(pts[:k], seed, jitter)
    d.line(base, fill=color, width=w, joint="curve")
    if double:
        d.line(_wob(pts[:k], seed + 77, jitter * 1.6), fill=color, width=max(2, w - 2), joint="curve")


def r_line(d, p0, p1, prog=1.0, seed=1, color=INK, w=5, jitter=1.3):
    stroke(d, segments(p0, p1), prog, seed, color, w, jitter)


def r_rect(d, box, prog=1.0, seed=2, color=INK, w=5, fill=None, r=None):
    x0, y0, x1, y1 = box
    if fill:
        d.rounded_rectangle(box, 6, fill=fill)
    pts = segments((x0, y0), (x1, y0), 7) + segments((x1, y0), (x1, y1), 7) + \
          segments((x1, y1), (x0, y1), 7) + segments((x0, y1), (x0, y0), 7)
    stroke(d, pts, prog, seed, color, w, 1.2, double=False)


def r_circle(d, cx, cy, rx, ry, prog=1.0, seed=3, color=INK, w=5, start=-2.4):
    if prog <= 0:
        return
    n = 46
    pts = []
    for i in range(n + 1):
        a = start + (i / n) * math.tau * 1.06
        r = 1 + 0.012 * math.sin(i * 1.7 + seed)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    stroke(d, pts, prog, seed, color, w, 1.8, double=True)


def arrow(d, p0, p1, prog=1.0, seed=5, color=INK, w=5, head=20):
    r_line(d, p0, p1, prog, seed, color, w)
    if prog > 0.9:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s in (+0.5, -0.5):
            r_line(d, p1, (p1[0] - head * math.cos(ang + s), p1[1] - head * math.sin(ang + s)), 1.0, seed + 3, color, w)


def highlight(d, box, color, prog=1.0, seed=9, tilt=0.0):
    if prog <= 0:
        return
    x0, y0, x1, y1 = box
    w = (x1 - x0) * cl(prog)
    lay = Image.new("RGBA", (int(w) + 8, int(y1 - y0) + 8), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rectangle([4, 4, w + 4, (y1 - y0) + 4], fill=color + (205,))
    lay = lay.rotate(tilt, expand=True, resample=Image.BICUBIC)
    return lay


def put_highlight(img, box, color, prog=1.0, tilt=0.0):
    lay = highlight(img, box, color, prog, tilt=tilt)
    if lay is not None:
        img.paste(lay, (int(box[0] - 4), int(box[1] - 4)), lay)


def sticker(m, pad=12, outline=WHITE, ow=10):
    a = m.getchannel("A")
    big = a.filter(ImageFilter.MaxFilter(ow * 2 - 1))
    base = Image.new("RGBA", (m.width + ow * 2, m.height + ow * 2), (0, 0, 0, 0))
    wl = Image.new("RGBA", m.size, outline + (255,))
    wl.putalpha(big)
    base.paste(wl, (ow, ow))
    base.paste(m, (ow, ow), m)
    return base


MASCOT = None


def mascot():
    global MASCOT
    if MASCOT is None:
        MASCOT = Image.open("../assets/mascot_rick_rgba.png").convert("RGBA")
    return MASCOT


def put_kid(img, cx, bottom, height, rot=0.0, pop=1.0, alpha=1.0):
    m = mascot()
    hh = max(2, int(height * pop))
    ww = max(2, int(m.width * hh / m.height))
    im = m.resize((ww, hh), Image.LANCZOS)
    im = sticker(im, 10, WHITE, 9)
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im.putalpha(a)
    img.paste(im, (int(cx - im.width / 2), int(bottom - im.height)), im)


def tape(img, x, y, w=110, h=34, rot=-8, color=(255, 240, 170)):
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rectangle([0, 0, w, h], fill=color + (200,))
    for i in range(0, w, 7):
        dd.line([i, 0, i, h], fill=color + (110,), width=1)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.paste(lay, (int(x - w / 2), int(y - h / 2)), lay)


def stamp_img(label, size=64, color=RED, angle=-8, alpha=255, scale=1.0, kind="ban"):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(label, font=F(size, kind))
    w, h = int(tw + 96), int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rectangle([3, 3, w - 4, h - 4], outline=color + (alpha,), width=7)
    dd.rectangle([14, 14, w - 15, h - 15], outline=color + (alpha // 2,), width=2)
    dd.text((w // 2, h // 2), label, font=F(size, kind), fill=color + (alpha,), anchor="mm")
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if scale != 1.0:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.LANCZOS)
    return im


# ---------------- captions ----------------
CAPS = [
    (S[0], [("America's credit card bill", [INK]), ("just passed", [INK]), ("$1.23 trillion.", [RED])]),
    (S[1], [("A record high.", [INK]), ("And nobody", [INK]), ("threw a party.", [INK])]),
    (S[2], [("The average card now charges", [INK]), ("around 21% interest", [RED]), ("a year.", [INK])]),
    (S[3], [("Carrying $6,000?", [INK]), ("You pay", [INK]), ("$1,000+ a year", [RED]), ("just to stand still.", [INK])]),
    (S[4], [("Here's the part they don't", [INK]), ("put in the ad.", [INK])]),
    (S[5], [("Two out of three shoppers", [INK]), ("are still paying off", [INK]), ("last year's gifts.", [RED])]),
    (S[6], [("Retailers expect almost", [INK]), ("$850 billion", [RED]), ("in returns this year.", [INK])]),
    (S[7], [("Returns aren't free.", [INK]), ("Shipping. Sorting. Staff.", [INK])]),
    (S[8], [("That someone is you.", [INK]), ("Priced into every shelf item.", [INK])]),
    (S[9], [("Every return. Every late fee.", [INK]), ("Every missed payment.", [INK]), ("It all gets priced in.", [RED])]),
    (S[10], [("Now watch the checkout.", [INK])]),
    (S[11], [("Split it into four.", [INK]), ("No interest —", [INK]), ("unless you're late.", [RED])]),
    (S[12], [("41% of buy now, pay later", [INK]), ("users already", [INK]), ("missed a payment.", [RED])]),
    (S[13], [("Nothing here is illegal.", [INK]), ("That's exactly the point.", [RED])]),
    (S[14], [("The debt is the product.", [INK]), ("You are the inventory.", [RED])]),
    (S[15], [("The system isn't broken.", [INK]), ("It's working as designed.", [INK])]),
    (S[16], [("Business stories hiding", [INK]), ("in plain sight.", [INK]), ("Follow TITONOMICS.", [GREEN])]),
    (S[17], [("Now you know where your", [INK]), ("money really goes.", [GREEN])]),
]


def caption_at(t):
    idx = -1
    for i, c in enumerate(CAPS):
        if t >= c[0]["start"] - 1e-6:
            idx = i
    return CAPS[idx] if idx >= 0 else None


def wrap(d, words, size, maxw):
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tl(d, t, F(size, "ab")) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_captions(img, d, t):
    c = caption_at(t)
    if not c:
        return
    size = 44
    words = []
    for seg in c[1]:
        for w in seg[0].split():
            words.append((w, seg[1][0]))
    lines = []
    cur, curw = [], ""
    for w, col in words:
        test = (curw + " " + w).strip()
        if tl(d, test, F(size, "ab")) <= 830 or not cur:
            cur.append((w, col))
            curw = test
        else:
            lines.append(cur)
            cur = [(w, col)]
            curw = w
    lines.append(cur)
    if len(lines) > 2:  # merge overflow into 2 lines
        lines = [sum(lines[:len(lines) // 2], []), sum(lines[len(lines) // 2:], [])]
        size = 40
    lh = 58
    h = len(lines) * lh + 34
    y0 = 1502 - h
    pn = Image.new("RGBA", (900, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(pn)
    dd.rounded_rectangle([0, 0, 899, h - 1], 18, fill=(255, 252, 244, 235), outline=INK + (255,), width=3)
    img.paste(pn, (90, y0), pn)
    for i, ln in enumerate(lines):
        total = sum(tl(d, w, F(size, "ab")) + tl(d, " ", F(size, "ab")) for w, _ in ln) - tl(d, " ", F(size, "ab"))
        x = 540 - total / 2
        y = y0 + 17 + i * lh + lh / 2
        for w, col in ln:
            text(d, (x, y), w, F(size, "ab"), col, anchor="lm")
            x += tl(d, w, F(size, "ab")) + tl(d, " ", F(size, "ab"))


# ---------------- chrome ----------------
def crop_marks(d):
    for (x, y, sx, sy) in [(52, 52, 1, 1), (W - 52, 52, -1, 1), (52, H - 52, 1, -1), (W - 52, H - 52, -1, -1)]:
        d.line([x, y, x + 34 * sx, y], fill=(176, 168, 152), width=3)
        d.line([x, y, x, y + 34 * sy], fill=(176, 168, 152), width=3)


def chrome(img, d, t):
    crop_marks(d)
    d.rectangle([0, 0, W, 10], fill=PAPER_D)
    d.rectangle([0, 0, int(W * (t / DUR)), 10], fill=INK)
    text(d, (108, 74), "TITONOMICS", F(38, "ban"), INK, anchor="lm")
    d.ellipse([74, 62, 90, 78], fill=GREEN)
    d.line([108, 96, 300, 96], fill=INK2, width=3)


# =========================================================
# BEATS — each returns nothing, draws onto img
# =========================================================
def b_hook(d, img, lt, dur):
    p = eo(lt / 0.6)
    put_highlight(img, (86, 292, 210 + 640 * p, 348), YELLOW, cl(p * 1.4), -1.2)
    text(d, (110, 300), "AMERICA'S", F(64, "ban"), INK, anchor="lm")
    text(d, (110, 370), "CREDIT CARD BILL", F(52, "ban"), INK, anchor="lm")
    # big number slams
    q = cl((lt - 0.35) / 0.3)
    if q > 0:
        sc = 1.4 - 0.4 * overshoot(q)
        fit(d, (540, 700), "$1.23", 210 * sc, RED, "ab", 900)
        fit(d, (540, 860), "TRILLION", 120 * sc, INK, "ab", 900)
    r_circle(d, 540, 760, 380 * (0.6 + 0.4 * eio(cl((lt - 0.7) / 0.5))), 190, cl((lt - 0.7) / 0.55), 71, RED, 7, start=-2.6)
    text(d, (110, 1010), "and it just hit a", F(34, "pm"), INK2, anchor="lm")
    text(d, (110, 1060), "record.", F(34, "pm"), RED, anchor="lm")


def b_record(d, img, lt, dur):
    p = cl(lt / 0.28)
    st = stamp_img("RECORD", 92, RED, -7, int(255 * cl(p * 1.6)), 1.9 - 0.9 * eo(p))
    img.paste(st, (540 - st.width // 2, 620 - st.height // 2), st)
    if lt > 0.5:
        text(d, (540, 900), "nobody threw a party", F(46, "pm"), INK, anchor="mm")
        r_line(d, (300, 950), (780, 950), cl((lt - 0.6) / 0.4), 33, INK, 4)
    if lt > 1.0:
        put_kid(img, 830, 1330, 330, rot=6, pop=0.92 + 0.05 * math.sin(lt * 5))
        text(d, (250, 1180), ":(", F(90, "ban"), INK2)


def b_apr(d, img, lt, dur):
    # credit card doodle
    r_rect(d, (150, 520, 700, 900), cl(lt / 0.5), 11, INK, 7, fill=WHITE)
    r_rect(d, (150, 600, 700, 660), cl((lt - 0.35) / 0.3), 12, INK, 5, fill=INK)
    text(d, (185, 830), "•••• 4812", F(44, "ab"), INK, anchor="lm")
    if lt > 0.7:
        fit(d, (230, 720), "YOUR CARD", 34, INK2, "ban", 380, "lm")
    q = cl((lt - 0.85) / 0.35)
    if q > 0:
        sc = 1.5 - 0.5 * overshoot(q)
        text(d, (800, 700), f"{int(21 * eo(q))}%", F(190 * sc, "ab"), RED, anchor="mm")
        r_line(d, (700, 800), (940, 800), q, 21, RED, 6)
        text(d, (820, 860), "interest / yr", F(34, "pm"), INK, anchor="mm")


def b_maths(d, img, lt, dur):
    text(d, (110, 330), "CARRY $6,000", F(46, "ban"), INK, anchor="lm")
    r_rect(d, (110, 400, 480, 700), cl(lt / 0.4), 14, INK, 6, fill=WHITE)
    text(d, (295, 500), "$6,000", F(64, "ab"), INK)
    text(d, (295, 580), "balance", F(30, "pm"), INK2)
    if lt > 0.5:
        arrow(d, (500, 550), (620, 550), cl((lt - 0.5) / 0.3), 15, INK, 6)
    q = cl((lt - 0.8) / 0.4)
    if q > 0:
        text(d, (830, 460), "+ $1,390", F(78, "ab"), RED, anchor="mm")
        text(d, (830, 540), "a year", F(34, "pm"), INK2, anchor="mm")
        text(d, (830, 600), "in interest", F(34, "pm"), INK2, anchor="mm")
        r_circle(d, 830, 520, 210, 120, q, 44, RED, 6)
    if lt > 1.55:
        put_highlight(img, (300, 842, 300 + 500 * cl((lt - 1.55) / 0.4), 922), YELLOW, 1.0, -1.0)
        text(d, (540, 880), "just to stand still", F(52, "ban"), INK)


def b_ad(d, img, lt, dur):
    # torn ad page
    p = cl(lt / 0.45)
    pg = Image.new("RGBA", (760, 620), (0, 0, 0, 0))
    dd = ImageDraw.Draw(pg)
    dd.rectangle([0, 0, 760, 620], fill=(255, 253, 246, 255))
    dd.rectangle([0, 0, 760, 90], fill=(255, 212, 60, 255))
    dd.text((40, 45), "0% APR*", font=F(56, "ab"), fill=(30, 26, 20), anchor="lm")
    for i in range(4):
        dd.rectangle([40, 140 + i * 60, 620 - i * 40, 172 + i * 60], fill=(232, 226, 212))
    dd.text((40, 430), "*terms apply. very much apply.", font=F(30, "pm"), fill=(90, 84, 74), anchor="lm")
    pg = pg.rotate(-3, expand=True, resample=Image.BICUBIC)
    if p > 0:
        hh = int(pg.height * (0.85 + 0.15 * eo(p)))
        sc = pg.resize((int(pg.width * hh / pg.height), hh), Image.LANCZOS)
        img.paste(sc, (540 - sc.width // 2, int(600 - sc.height // 2 + (1 - eo(p)) * -260)), sc)
    if lt > 0.7:
        q = cl((lt - 0.7) / 0.35)
        for a in (-1, 1):
            r_line(d, (330, 520 - a * 60), (760, 700 + a * 60), q, 51 + a, RED, 9)
    if lt > 1.15:
        text(d, (540, 1010), "the part they don't", F(44, "pm"), INK2)
        text(d, (540, 1065), "put in the ad", F(44, "pm"), RED)


def b_two_of_three(d, img, lt, dur):
    # highlighter first, people on top
    for i in range(3):
        if i >= 2:
            continue
        p = cl((lt - i * 0.18) / 0.4)
        if p <= 0:
            continue
        x = 260 + i * 280
        pgl = highlight(img, (x - 66, 500, x + 66, 820), YELLOW, p * 0.85, tilt=-2)
        if pgl is not None:
            img.paste(pgl, (int(x - 70), int(496)), pgl)
    for i in range(3):
        x = 260 + i * 280
        p = cl((lt - i * 0.18) / 0.35)
        if p <= 0:
            continue
        r_circle(d, x, 560, 54, 54, p, 60 + i, INK, 6)
        stroke(d, segments((x, 614), (x, 730), 5), p, 70 + i, INK, 7)
        stroke(d, segments((x - 55, 660), (x + 55, 660), 5), p, 80 + i, INK, 7)
        stroke(d, segments((x, 730), (x - 40, 800), 5) + segments((x, 730), (x + 40, 800), 5), p, 90 + i, INK, 7)
    if lt > 0.9:
        text(d, (540, 960), "2 out of 3", F(96, "ab"), INK)
    if lt > 1.25:
        text(d, (540, 1050), "still paying for last year's gifts", F(40, "pm"), RED)


def b_returns(d, img, lt, dur):
    text(d, (110, 320), "RETURNS THIS YEAR", F(40, "ban"), INK, anchor="lm")
    q = cl((lt - 0.15) / 0.5)
    if q > 0:
        r_line(d, (250, 560), (250 + 580 * cl((lt - 0.35) / 0.4), 560), 1.0, 19, RED, 8)
        text(d, (540, 470), f"${int(850 * eo(q))}B", F(180, "ab"), RED)
    # box with return arrow
    r_rect(d, (300, 640, 620, 900), cl((lt - 0.5) / 0.4), 21, INK, 7, fill=WHITE)
    r_line(d, (460, 640), (460, 900), 1, 22, INK2, 3)
    if lt > 0.9:
        pts = [(700, 800), (760, 720), (700, 660), (620, 700)]
        stroke(d, pts, cl((lt - 0.9) / 0.5), 23, RED, 8)
        arrow(d, (700, 660), (640, 680), cl((lt - 1.3) / 0.2), 24, RED, 8)
    if lt > 1.8:
        text(d, (540, 1010), "returns aren't free", F(48, "pm"), INK)


def b_who_pays(d, img, lt, dur):
    text(d, (540, 330), "RETURN COSTS", F(46, "ban"), INK)
    items = [("shipping", 0.15), ("sorting", 0.45), ("staff", 0.75)]
    for i, (nm, dly) in enumerate(items):
        q = cl((lt - dly) / 0.3)
        if q <= 0:
            continue
        y = 480 + i * 130
        r_rect(d, (180, y, 780, y + 100), q, 30 + i, INK, 5, fill=WHITE)
        text(d, (220, y + 50), nm, F(42, "pm"), INK, anchor="lm")
        text(d, (740, y + 50), "$$$", F(38, "ab"), RED, anchor="rm")
    if lt > 1.9:
        text(d, (540, 1000), "someone has to pay", F(42, "pm"), INK2)
        text(d, (540, 1055), "for all of it", F(42, "pm"), INK2)


def b_you(d, img, lt, dur):
    text(d, (110, 320), "THAT SOMEONE", F(40, "ban"), INK, anchor="lm")
    if lt > 0.15:
        text(d, (110, 400), "IS YOU", F(88, "ban"), RED, anchor="lm")
    # shelf with price tags
    r_line(d, (100, 800), (980, 800), cl(lt / 0.4), 61, INK, 6)
    for i in range(4):
        x = 190 + i * 220
        q = cl((lt - 0.5 - i * 0.12) / 0.3)
        if q <= 0:
            continue
        r_rect(d, (x - 60, 660, x + 60, 795), q, 62 + i, INK, 5, fill=PAPER_D)
        put_highlight(img, (x - 70, 560, x + 70, 620), YELLOW, q, -2)
        text(d, (x, 590), f"+{i + 2}%", F(38, "ab"), INK)
    if lt > 1.6:
        put_kid(img, 860, 1480, 400, rot=-5, pop=0.9 + 0.08 * eo(cl((lt - 1.6) / 0.3)))
        arrow(d, (740, 1180), (620, 1060), cl((lt - 1.75) / 0.3), 63, INK, 6)


def b_every(d, img, lt, dur):
    text(d, (540, 330), "IT ALL GETS PRICED IN", F(44, "ban"), INK)
    stamps = [("RETURN", 0.1, -8), ("LATE FEE", 0.45, 6), ("MISSED", 0.8, -5)]
    for i, (lb, dly, ang) in enumerate(stamps):
        q = cl((lt - dly) / 0.25)
        if q <= 0:
            continue
        st = stamp_img(lb, 76, [INK, RED, INK][i], ang, int(255 * cl(q * 2)), 2.0 - 1.0 * eo(q))
        img.paste(st, (540 - st.width // 2, 500 + i * 200 - st.height // 2), st)
    if lt > 2.0:
        put_highlight(img, (170, 1090, 910, 1180), YELLOW, cl((lt - 2.0) / 0.4), -0.8)
        text(d, (540, 1135), "priced into everything", F(52, "pm"), INK)


def b_checkout(d, img, lt, dur):
    # phone + cart
    r_rect(d, (300, 440, 780, 1180), cl(lt / 0.4), 71, INK, 9, fill=WHITE)
    r_line(d, (500, 470), (580, 470), 1, 70, INK2, 8)
    r_rect(d, (350, 520, 730, 700), 1, 72, INK2, 4, fill=PAPER_D)
    text(d, (540, 610), "CHECKOUT", F(46, "ban"), INK)
    r_rect(d, (350, 760, 730, 870), 1, 73, INK2, 4, fill=YELLOW)
    text(d, (540, 815), "PAY NOW", F(46, "ban"), INK)
    text(d, (540, 960), "or pay in 4", F(34, "pm"), RED)
    text(d, (540, 1010), "no interest*", F(34, "pm"), INK2)
    if lt > 0.4:
        cx, cy = 540, 800
        r = 40 + 20 * abs(math.sin(lt * 3))
        r_circle(d, cx, cy, r, r, 1, 74, RED, 5)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=WHITE)


def b_bnpl(d, img, lt, dur):
    text(d, (110, 330), "SPLIT IT INTO FOUR", F(46, "ban"), INK, anchor="lm")
    for i in range(4):
        q = cl((lt - 0.15 - i * 0.13) / 0.3)
        if q <= 0:
            continue
        x = 160 + (i % 2) * 400
        y = 470 + (i // 2) * 240
        r_rect(d, (x, y, x + 340, y + 180), q, 80 + i, INK, 6, fill=WHITE)
        text(d, (x + 170, y + 70), "PAY 4/4", F(38, "ban"), INK)
        text(d, (x + 170, y + 130), "no interest", F(28, "pm"), INK2)
    if lt > 1.1:
        text(d, (540, 1010), "unless you're late", F(52, "pm"), RED)
        r_line(d, (330, 1060), (750, 1060), cl((lt - 1.2) / 0.3), 90, RED, 5)


def b_41(d, img, lt, dur):
    text(d, (110, 330), "BUY NOW, PAY LATER", F(44, "ban"), INK, anchor="lm")
    cx, cy, R = 400, 730, 230
    for i in range(56):
        a = -math.pi / 2 + i * math.tau / 56
        d.ellipse([cx + R * math.cos(a) - 6, cy + R * math.sin(a) - 6,
                   cx + R * math.cos(a) + 6, cy + R * math.sin(a) + 6], fill=INK)
    q = cl(lt / 0.6)
    if q > 0:
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * 0.41 * eo(q), fill=RED)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=7)
    d.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], fill=PAPER)
    text(d, (cx, cy - 12), "41%", F(84, "ab"), RED)
    text(d, (cx, cy + 50), "late", F(32, "pm"), INK)
    text(d, (752, 640), "of BNPL users", F(38, "pm"), INK, anchor="lm")
    text(d, (752, 700), "already missed", F(38, "pm"), INK, anchor="lm")
    text(d, (752, 760), "a payment", F(38, "pm"), RED, anchor="lm")
    if lt > 1.6:
        text(d, (540, 1090), "buy now, pay later", F(46, "ban"), INK)
        text(d, (540, 1150), "is a subscription", F(46, "ban"), RED)


def b_legal(d, img, lt, dur):
    text(d, (540, 430), "NOTHING HERE", F(60, "ban"), INK)
    text(d, (540, 520), "IS ILLEGAL", F(60, "ban"), INK)
    if lt > 0.5:
        q = cl((lt - 0.5) / 0.35)
        pts = [(360, 700), (470, 830), (740, 600)]
        stroke(d, pts, q, 95, GREEN, 16, 1.5)
    if lt > 1.1:
        put_highlight(img, (300, 990, 300 + 480 * cl((lt - 1.1) / 0.4), 1062), YELLOW, 1.0, -1.0)
        text(d, (540, 985), "that's exactly", F(48, "pm"), INK)
        text(d, (540, 1040), "the point", F(48, "pm"), RED)


def b_product(d, img, lt, dur):
    text(d, (540, 340), "THE DEBT IS THE PRODUCT", F(42, "ban"), INK)
    # person + barcode
    pp = cl(lt / 0.45)
    r_circle(d, 380, 620, 78, 78, pp, 101, INK, 7)
    stroke(d, segments((380, 698), (380, 760), 4), pp, 103, INK, 7)
    r_rect(d, (290, 760, 470, 1080), pp, 102, INK, 7, fill=WHITE)
    stroke(d, segments((292, 800), (238, 950), 5), pp, 104, INK, 10)
    stroke(d, segments((468, 800), (522, 950), 5), pp, 105, INK, 10)
    stroke(d, segments((340, 1080), (330, 1170), 4) + segments((420, 1080), (430, 1170), 4), pp, 106, INK, 7)
    if lt > 0.8:
        q = cl((lt - 0.8) / 0.6)
        for i in range(12):
            x = 640 + i * 22
            if q * 12 < i:
                break
            d.rectangle([x, 720, x + 12, 980], fill=INK)
        text(d, (700, 1030), "TITONOMICS-001", F(26, "ab"), INK2)
    if lt > 1.8:
        put_highlight(img, (250, 1180, 830, 1270), YELLOW, cl((lt - 1.8) / 0.4), -0.6)
        text(d, (540, 1225), "you are the inventory", F(50, "pm"), RED)


def b_designed(d, img, lt, dur):
    text(d, (540, 330), "THE SYSTEM ISN'T BROKEN", F(44, "ban"), INK)
    # gears
    for i, (cx, cy, R, sp) in enumerate([(400, 760, 150, 1.0), (700, 900, 110, -1.4)]):
        p = cl((lt - 0.2 - i * 0.2) / 0.5)
        if p <= 0:
            continue
        rot = lt * sp
        for k in range(8):
            a = rot + k * math.tau / 8
            d.line([cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a),
                    cx + (R + 14) * math.cos(a), cy + (R + 14) * math.sin(a)], fill=INK, width=16)
        r_circle(d, cx, cy, R, R, p, 110 + i, INK, 8)
        r_circle(d, cx, cy, R * 0.35, R * 0.35, p, 120 + i, INK, 6)
    if lt > 1.4:
        text(d, (540, 1180), "working exactly", F(46, "pm"), INK)
        text(d, (540, 1235), "as designed", F(46, "pm"), GREEN)


def b_cta(d, img, lt, dur):
    put_kid(img, 300, 1330, 520, rot=-6, pop=0.9 + 0.08 * eo(cl(lt / 0.3)))
    text(d, (700, 550), "FOLLOW", F(56, "ban"), INK, anchor="lm")
    text(d, (700, 630), "TITONOMICS", F(56, "ban"), GREEN, anchor="lm")
    q = cl((lt - 0.4) / 0.3)
    if q > 0:
        r_rect(d, (690, 720, 990, 830), q, 130, INK, 6, fill=RED)
        text(d, (840, 775), "SUBSCRIBE", F(38, "ban"), WHITE)
    if lt > 1.1:
        r_circle(d, 840, 775, 200, 80, cl((lt - 1.1) / 0.4), 131, RED, 5)
    if lt > 1.7:
        text(d, (700, 940), "business stories", F(34, "pm"), INK2, anchor="lm")
        text(d, (700, 990), "hiding in plain sight", F(34, "pm"), INK2, anchor="lm")


def b_end(d, img, lt, dur):
    text(d, (540, 520), "NOW YOU KNOW", F(64, "ban"), INK)
    text(d, (540, 610), "WHERE IT GOES", F(64, "ban"), INK)
    # receipt
    p = cl((lt - 0.2) / 0.5)
    if p > 0:
        rc = Image.new("RGBA", (620, 700), (0, 0, 0, 0))
        dd = ImageDraw.Draw(rc)
        dd.rectangle([0, 0, 620, 700], fill=(255, 253, 246, 255))
        dd.text((40, 50), "AMERICA'S CARD BILL", font=F(30, "ab"), fill=(30, 26, 20))
        for i, (k, v) in enumerate([("BALANCE", "$1.23T"), ("AVG RATE", "21%"), ("RETURNS", "$850B"),
                                    ("BNPL LATE", "41%")]):
            dd.text((40, 140 + i * 80), k, font=F(28, "pm"), fill=(80, 74, 64))
            dd.text((580, 140 + i * 80), v, font=F(32, "ab"), fill=(30, 26, 20), anchor="ra")
            dd.line([40, 190 + i * 80, 580, 190 + i * 80], fill=(210, 204, 190), width=2)
        dd.text((40, 540), "THANK YOU FOR SHOPPING", font=F(26, "ab"), fill=(120, 112, 100))
        dd.text((40, 600), "TITONOMICS", font=F(46, "ban"), fill=(56, 178, 84))
        rc = rc.rotate(-2, expand=True, resample=Image.BICUBIC)
        hh = int(rc.height * 1.05 * (0.9 + 0.1 * eo(p)))
        sc = rc.resize((int(rc.width * hh / rc.height), hh), Image.LANCZOS)
        img.paste(sc, (540 - sc.width // 2, int(1080 - sc.height // 2)), sc)
    if lt > 1.2:
        text(d, (540, 1296), "sources: NY Fed · Federal Reserve · industry surveys", F(20, "pm"), INK2)


# (start_index, fn)  — beat starts at that sentence's start
BEATS = [
    (0, b_hook), (1, b_record), (2, b_apr), (3, b_maths), (4, b_ad), (5, b_two_of_three),
    (6, b_returns), (7, b_who_pays), (8, b_you), (9, b_every), (10, b_checkout),
    (11, b_bnpl), (12, b_41), (13, b_legal), (14, b_product), (15, b_designed),
    (16, b_cta), (17, b_end),
]
STARTS = [max(0.0, sstart(i) - 0.42) for i, _ in BEATS]
CUTS = STARTS[1:]

SHAKES = [(STARTS[1], 9, 7), (STARTS[6], 8, 7), (STARTS[9], 10, 6), (STARTS[12], 8, 6), (STARTS[14], 9, 6)]


def shake_at(t):
    x = y = 0.0
    for (st, amp, dec) in SHAKES:
        dt = t - st
        if 0 <= dt < 0.6:
            a = amp * math.exp(-dt * dec)
            x += a * math.sin(dt * 62)
            y += a * math.cos(dt * 88)
    return x, y


def camera(img, zoom, dx, dy):
    if abs(zoom - 1) < 0.002 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return img
    w, h = W / zoom, H / zoom
    x0 = cl((W - w) / 2 + dx, 0, W - w)
    y0 = cl((H - h) / 2 + dy, 0, H - h)
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)


def render_frame(t):
    i = 0
    for k, (si, fn) in enumerate(BEATS):
        if t >= STARTS[k] - 1e-9:
            i = k
    start = STARTS[i]
    end = STARTS[i + 1] if i + 1 < len(BEATS) else DUR
    lt = t - start
    img = Image.fromarray(PAPER_IMG.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    BEATS[i][1](d, img, lt, end - start)
    d = ImageDraw.Draw(img)

    zoom = 1.01 + 0.035 * (lt / max(0.3, end - start))
    sx, sy = shake_at(t)
    img = camera(img, zoom, sx, sy)
    d = ImageDraw.Draw(img)
    chrome(img, d, t)
    draw_captions(img, d, t)

    arr = np.asarray(img, np.int16) + FIBERS[(int(t * FPS) // 2) % 4]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def main():
    os.makedirs("build", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        for ts in [float(x) for x in sys.argv[2:]]:
            render_frame(ts).save(f"build/v3_{ts:05.2f}.png")
        print("ok")
        return
    out = "build/video3_silent.mp4"
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
           "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        p.stdin.write(render_frame(f / FPS).tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{NFRAMES}", flush=True)
    p.stdin.close()
    p.wait()
    print("done", p.returncode)


if __name__ == "__main__":
    main()
