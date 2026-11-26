"""Build exact sentence timeline from per-group TTS clips (silence-based snapping)."""
import json, re, subprocess, os
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
GROUPS = {
    "g1": ["America's credit card bill just passed one point two three trillion dollars.",
           "A record high. And nobody threw a party."],
    "g2": ["The average card now charges around twenty one percent interest a year.",
           "So if you're carrying six thousand dollars, you're paying more than a thousand a year just to stand still."],
    "g3": ["Here's the part they don't put in the ad.",
           "Two out of three shoppers are still paying off last year's holiday gifts."],
    "g4": ["And retailers expect almost eight hundred and fifty billion dollars of returns this year.",
           "Returns aren't free. Someone pays for the shipping, the sorting, and the staff."],
    "g5": ["That someone is you, priced quietly into every item on the shelf.",
           "Every return, every late fee, every missed payment, it all gets priced in."],
    "g6": ["Now watch the checkout.",
           "Split it into four. No interest, unless you're late."],
    "g7": ["Forty one percent of buy now, pay later users say they've already missed a payment.",
           "Nothing here is illegal. That's exactly the point."],
    "g8": ["The debt is the product. You are the inventory.",
           "The system isn't broken. It's working exactly as designed."],
    "g9": ["Business stories hiding in plain sight. Follow TITONOMICS.",
           "Now you know where your money really goes."],
}
GAP_IN = 0.14     # pause between sentences in a group
GAP_OUT = 0.34    # pause between groups
LEAD = 0.55       # intro before first word


def duration(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def silences(path, noise="-38dB", d=0.16):
    out = subprocess.run([FF, "-hide_banner", "-i", path, "-af",
                          f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(s, e) for s, e in zip(starts, ends)]


def split_clip(path, sentences):
    """Return [(text, rel_start, rel_end)] using proportional mapping snapped to silences."""
    dur = duration(path)
    sil = [s for s in silences(path) if s[1] - s[0] >= 0.12]
    mids = [(a + b) / 2 for a, b in sil]
    total_chars = sum(len(s) for s in sentences)
    bounds = []
    acc = 0
    for s in sentences[:-1]:
        acc += len(s)
        bounds.append(acc / total_chars)
    cuts = []
    for f in bounds:
        guess = f * dur
        if mids:
            best = min(mids, key=lambda m: abs(m - guess))
            cuts.append(best if abs(best - guess) < 0.75 else guess)
        else:
            cuts.append(guess)
    edges = [0.0] + cuts + [dur]
    out = []
    for i, s in enumerate(sentences):
        out.append((s, edges[i], edges[i + 1]))
    return out, dur


def main():
    timeline = []
    t = LEAD
    groups_meta = []
    for gi, (g, sents) in enumerate(GROUPS.items()):
        path = f"vo/{g}.mp3"
        parts, dur = split_clip(path, sents)
        gstart = t
        for i, (txt, a, b) in enumerate(parts):
            timeline.append({"text": txt, "start": round(t + a, 3), "end": round(t + b, 3)})
        t += dur
        groups_meta.append({"id": g, "start": round(gstart, 3), "end": round(t, 3)})
        t += GAP_OUT if gi < len(GROUPS) - 1 else 0.0
    total = round(t + 0.9, 3)
    data = {"total": total, "lead": LEAD, "sentences": timeline, "groups": groups_meta,
            "clips": {g: {"path": f"vo/{g}.mp3", "dur": duration(f"vo/{g}.mp3")} for g in GROUPS}}
    os.makedirs("build", exist_ok=True)
    json.dump(data, open("build/timeline.json", "w"), indent=1)
    print(f"total {total:.2f}s, {len(timeline)} sentences")
    for s in timeline:
        print(f"  {s['start']:6.2f}-{s['end']:6.2f}  {s['text'][:64]}")


if __name__ == "__main__":
    main()
