#!/usr/bin/env python3
"""Billboards in more shapes: square (1:1), portrait (4:5), story (9:16) and widescreen (16:9).

Every board is laid out again for each shape instead of being cropped or squashed: headlines are
re-broken and re-sized, art is moved and re-scaled, and panels, roads and floors stretch to fit.

The art comes from make_boards_v2.py / make_boards_v3.py (same folder). Text widths come from the
real fonts, measured once in headless Chrome and cached in text-widths.json (see run_formats.sh).

usage: python3 -I make_formats.py <out_dir> [--probe]
  --probe   write each piece of art on its own (for measuring its bounding box), then stop
"""
import json, os, random, runpy, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
PROBE = "--probe" in sys.argv

# ------------------------------------------------------------------ art + helpers from v2 / v3
_argv, _stdout = sys.argv, sys.stdout
sys.argv, sys.stdout = ["make_boards_v3.py", tempfile.mkdtemp()], open(os.devnull, "w")
V3 = runpy.run_path(os.path.join(HERE, "make_boards_v3.py"))
sys.argv, sys.stdout = _argv, _stdout
V2 = V3["ns"]

G, O = V2["G"], V2["O"]
R, DR, Y, A, P, E, EG, GN, I, W = (V2[k] for k in "R DR Y A P E EG GN I W".split())
A2, GREY, MID = V2["A2"], V2["GREY"], V2["MID"]
t, line, path, circle, rect, rough, shift, defs = (V2[k] for k in "t line path circle rect rough shift defs".split())
SITE_URL = V2["SITE_URL"]
SOFT, FLOOR = "#4d4245", "#a50d26"

# ------------------------------------------------------------------ text widths (measured from the real fonts)
WPATH = os.path.join(HERE, "text-widths.json")
WC = json.load(open(WPATH)) if os.path.exists(WPATH) else {}
MISSING = set()


def em(s, fam=G, wt=800, it=False):
    """Width of s in em (1 em = font size)."""
    k = f"{'G' if fam == G else 'O'}|{wt}|{int(bool(it))}|{s}"
    if k in WC:
        return WC[k] / 1000
    MISSING.add(k)
    return 0.55 * len(s)


class St:
    def __init__(self, fam=G, wt=800, fill=I, it=False):
        self.fam, self.wt, self.fill, self.it = fam, wt, fill, it
        self.lh = 1.02 if fam == G else 1.12

    def em(self, s):
        return em(s, self.fam, self.wt, self.it)

    def attrs(self):
        return (f'font-family="{self.fam}" font-weight="{self.wt}" fill="{self.fill}"'
                + (' font-style="italic"' if self.it else ""))


def serif(fill=I, wt=800, it=False):
    return St(G, wt, fill, it)


def sans(fill=I, wt=900):
    return St(O, wt, fill)


# ------------------------------------------------------------------ formats and shared sizes
FORMATS = [  # id, width, height, label, good for
    ("square", 2160, 2160, "Square 1:1", "Instagram and Facebook posts"),
    ("portrait", 2160, 2700, "Portrait 4:5", "Instagram feed, flyers, posters"),
    ("story", 2160, 3840, "Story 9:16", "Stories, Reels, TikTok, phone screens, tall posters"),
    ("wide", 3840, 2160, "Widescreen 16:9", "TV screens, slides, YouTube, digital signs"),
]
U = 2160                      # base unit: the short side of every format
M = round(0.075 * U)          # outer margin
ASC, DESC = 0.74, 0.26        # ascent / descent as a share of font size
PILL_H, PILL_T = 0.07 * U, 0.046 * U
PILL_W = 0.035 * U + 0.07 * U + 0.025 * U + em(SITE_URL, O, 800) * PILL_T + 0.045 * U
PILL_B = 0.055 * U            # gap under the pill
FOOT = PILL_H + PILL_B + 0.035 * U   # space kept clear for the web address


class Ctx:
    def __init__(self, fmt, w, h):
        self.fmt, self.W, self.H = fmt, w, h
        self.tall = h / w > 1.5
        self.wide = w > h
        self.k = 1.18 if self.tall else 1.0   # type can be bigger on tall formats


class Box:
    def __init__(self, x, y, w, h, ex0, ex1, c):
        self.x, self.y, self.w, self.h, self.ex0, self.ex1, self.c = x, y, w, h, ex0, ex1, c


# ------------------------------------------------------------------ blocks
class Fixed:
    """A block whose height follows from the width (text)."""
    flex = False
    to_bottom = False
    bleed = None

    def __init__(self, gap=0.32, max=0.14):
        self.gap, self.max, self.scale, self.size = gap, max, 1.0, 0

    def gap_px(self):
        return self.gap * self.size

    def shrink(self, f):
        self.scale *= f


class Text(Fixed):
    """Lines of text fitted to the width. A line is a str or a list of (str, St) runs.
    options: alternative line breaks; the one giving the biggest type wins (fewer lines on a near tie).
    wrap: a paragraph, wrapped at a fixed size (share of U)."""

    def __init__(self, lines=None, st=None, max=0.14, gap=0.32, align="start", strike=False, options=None, wrap=None, size=0.03):
        super().__init__(gap, max)
        self.opts = options or [lines]
        self.st, self.align, self.strike, self.wrap, self.fixed = st or serif(), align, strike, wrap, size

    def runs(self, ln):
        return [(ln, self.st)] if isinstance(ln, str) else ln

    def lw(self, ln):
        return sum(st.em(s) for s, st in self.runs(ln))

    def fit(self, w, c):
        if self.wrap:
            self.size = self.fixed * U * max(self.scale, 0.85)
            lines, cur = [], ""
            for wd in self.wrap.split(" "):
                cand = (cur + " " + wd).strip()
                if cur and self.st.em(cand) * self.size > w:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = cand
            self.lines = lines + [cur]
            for ln in self.lines:
                em(ln, self.st.fam, self.st.wt, self.st.it)
        else:
            best = None
            for opt in self.opts:
                sz = min(self.max * U * self.scale * c.k, w / max(self.lw(ln) for ln in opt))
                if best is None or sz > best[0] * 1.04 or (sz >= best[0] * 0.96 and len(opt) < len(best[1])):
                    best = (sz, opt)
            self.size, self.lines = best
        return self.size * (ASC + (len(self.lines) - 1) * self.st.lh + DESC)

    def render(self, B):
        anchor = self.align
        ax = {"start": B.x, "middle": B.x + B.w / 2, "end": B.x + B.w}[anchor]
        out = ""
        for i, ln in enumerate(self.lines):
            by = B.y + self.size * (ASC + i * self.st.lh)
            spans = "".join(f'<tspan {st.attrs()}>{s}</tspan>' for s, st in self.runs(ln))
            out += f'<text x="{ax:.0f}" y="{by:.0f}" font-size="{self.size:.0f}" text-anchor="{anchor}">{spans}</text>'
            if self.strike:
                s, lw = self.size, self.lw(ln) * self.size
                sy = by - 0.27 * s
                out += rough(path(f"M{ax - 0.08 * s:.0f} {sy + 0.05 * s:.0f} L{ax + lw + 0.08 * s:.0f} {sy - 0.07 * s:.0f}",
                                  stroke=R, sw=round(0.085 * s)))
        return out


class Flex:
    """A block that can take a range of heights (art, scenes)."""
    flex = True
    to_bottom = False
    bleed = None

    def __init__(self, grow=1.0, gap=0.04):
        self.grow, self.gap = grow, gap

    def gap_px(self):
        return self.gap * U

    def shrink(self, f):
        pass


class Art(Flex):
    """Art drawn in billboard coordinates; box = the part to show (x0, y0, x1, y1).
    bleed: 'top' / 'bottom' / 'right' runs the art off that edge of the canvas (or column)."""

    def __init__(self, svg, box, grow=1.0, maxs=1.9, halign="middle", valign="middle", bleed=None, avoid_pill=False, gap=0.04, minf=0.6):
        super().__init__(grow, gap)
        self.svg, self.box, self.maxs, self.halign, self.valign = svg, box, maxs, halign, valign
        self.bleed, self.avoid_pill, self.minf = bleed, avoid_pill, minf
        self.bw, self.bh = box[2] - box[0], box[3] - box[1]

    def width(self, B):
        w = (B.ex1 - B.x) if self.bleed == "right" else B.w
        if self.avoid_pill:
            w = min(w, B.ex1 - M - PILL_W - 0.05 * U - B.x)
        return w

    def hrange(self, B):
        hi = self.bh * min(self.width(B) / self.bw, self.maxs)
        return hi * self.minf, hi

    def render(self, B):
        w = self.width(B)
        s = min(w / self.bw, B.h / self.bh, self.maxs)
        aw, ah = self.bw * s, self.bh * s
        ax = B.ex1 - aw if self.bleed == "right" else {"start": B.x, "middle": B.x + (w - aw) / 2, "end": B.x + w - aw}[self.halign]
        ay = {"start": B.y, "middle": B.y + (B.h - ah) / 2, "end": B.y + B.h - ah}[self.valign]
        return f'<g transform="translate({ax - self.box[0] * s:.1f} {ay - self.box[1] * s:.1f}) scale({s:.4f})">{self.svg}</g>'


class Panel(Fixed):
    """A full-bleed colour band holding text. to_bottom: runs to the bottom of the canvas (the web address sits on it)."""

    def __init__(self, fill, blocks, pad=0.065, to_bottom=False, gap=0.0):
        super().__init__(gap, 0)
        self.fill, self.blocks, self.pad, self.to_bottom = fill, blocks, pad * U, to_bottom

    def gap_px(self):
        return self.gap * U

    def shrink(self, f):
        for b in self.blocks:
            b.shrink(f)

    def fit(self, w, c):
        hs = [b.fit(w, c) for b in self.blocks]
        self.inner = sum(hs) + sum(b.gap_px() for b in self.blocks[:-1])
        return self.inner + 2 * self.pad + (FOOT - self.pad if self.to_bottom else 0)

    def render(self, B):
        c = B.c
        y1 = c.H + 60 if self.to_bottom else B.y + B.h
        out = rough(rect(B.ex0 - 60, B.y, B.ex1 - B.ex0 + 120, y1 - B.y, self.fill), "roughBig")
        bottom = c.H - FOOT if self.to_bottom else B.y + B.h - self.pad
        return out + stack(self.blocks, B.x, B.w, B.y + self.pad, bottom, B.ex0, B.ex1, c, "center")


# ------------------------------------------------------------------ layout engine
def stack(blocks, x, w, y0, y1, ex0, ex1, c, mode="spread"):
    """Lay blocks out top to bottom between y0 and y1."""
    B0 = Box(x, y0, w, y1 - y0, ex0, ex1, c)
    for attempt in range(7):   # type shrinks a little (to about 70%), then the art gives way
        hs = [None if b.flex else b.fit(w, c) for b in blocks]
        rng = {id(b): b.hrange(B0) for b in blocks if b.flex}
        fixed = sum(h for h in hs if h is not None) + sum(b.gap_px() for b in blocks[:-1])
        avail = (y1 - y0) - fixed
        need = sum(lo for lo, _ in rng.values())
        if avail >= need or attempt == 6:
            break
        for b in blocks:
            b.shrink(0.95)
    if avail < need:
        f = max(avail, 0) / need if need else 0
        rng = {k: (lo * f, hi) for k, (lo, hi) in rng.items()}
        need = sum(lo for lo, _ in rng.values())
    # share the free height between flexible blocks (by grow, up to each one's max)
    alloc = {k: lo for k, (lo, _) in rng.items()}
    rem = avail - need
    active = [b for b in blocks if b.flex]
    while rem > 0.5 and active:
        tg = sum(b.grow for b in active)
        used, nxt = 0, []
        for b in active:
            lo, hi = rng[id(b)]
            add, room = rem * b.grow / tg, hi - alloc[id(b)]
            if add >= room:
                alloc[id(b)] += room
                used += room
            else:
                alloc[id(b)] += add
                used += add
                nxt.append(b)
        rem -= used
        if len(nxt) == len(active):
            break
        active = nxt
    left = max(rem, 0)
    heights = [alloc[id(b)] if b.flex else h for b, h in zip(blocks, hs)]
    # leftover space: a little between blocks, the rest above / below
    n = len(blocks)
    last_bottom = blocks[-1].to_bottom
    if last_bottom:
        heights[-1] += left * 0.4
        left *= 0.6
    share = {"spread": 0.5, "center": 0.25, "top": 0.0}[mode]
    inner = min(left * share, 0.07 * c.H * (n - 1)) if n > 1 else 0
    per = inner / (n - 1) if n > 1 else 0
    rest = left - inner
    if last_bottom or blocks[-1].bleed == "bottom" or mode == "top":
        top = rest
    else:
        top = rest * (0.3 if mode == "spread" else 0.5)
    y, out = y0 + top, ""
    for i, (b, h) in enumerate(zip(blocks, heights)):
        out += b.render(Box(x, y, w, h, ex0, ex1, c))
        y += h + (b.gap_px() + per if i < n - 1 else 0)
    return out


class Col:
    def __init__(self, frac, blocks, fill=None, foot=None, bleed_bottom=False, mode="center"):
        self.frac, self.blocks, self.fill, self.foot, self.bleed_bottom, self.mode = frac, blocks, fill, foot, bleed_bottom, mode


def layout_cols(cols, c, sp):
    xs = [0]
    for col in cols:
        xs.append(xs[-1] + col.frac)
    n, out = len(cols), ""
    for i, col in enumerate(cols):
        cx0, cx1 = xs[i] * c.W, (c.W if i == n - 1 else xs[i + 1] * c.W)
        if col.fill:
            out += rough(rect(cx0, -60, cx1 - cx0 + 60, c.H + 120, col.fill), "roughBig")
        il = M if (i == 0 or col.fill) else 0.03 * U
        ir = M if (i == n - 1 or col.fill) else 0.03 * U
        foot = col.foot if col.foot is not None else (i == n - 1)
        if sp.get("y1"):
            y1 = sp["y1"](c)
        elif col.bleed_bottom:
            y1 = c.H
        elif foot:
            y1 = c.H - FOOT
        else:
            y1 = c.H - M
        y0 = 0 if col.blocks[0].bleed == "top" else M
        out += stack(col.blocks, cx0 + il, cx1 - cx0 - il - ir, y0, y1, cx0, cx1, c, col.mode)
    return out


def layout_stack(blocks, c, sp):
    last = blocks[-1]
    if sp.get("y1"):
        y1 = sp["y1"](c)
    elif last.to_bottom or last.bleed == "bottom":
        y1 = c.H
    else:
        y1 = c.H - FOOT
    y0 = 0 if blocks[0].bleed == "top" else M
    return stack(blocks, M, c.W - 2 * M, y0, y1, 0, c.W, c, sp.get("mode", "spread"))


# ------------------------------------------------------------------ canvas pieces
def background(bg, w, h):
    if bg != "ecg":
        return rect(0, 0, w, h, bg)
    out, step = [rect(0, 0, w, h, E)], 54
    for k, x in enumerate(range(0, w + 1, step)):
        c_, sw = (EG, 5) if k % 5 == 0 else ("#f6d3cc", 2.5)
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{c_}" stroke-width="{sw}"/>')
    for k, y in enumerate(range(0, h + 1, step)):
        c_, sw = (EG, 5) if k % 5 == 0 else ("#f6d3cc", 2.5)
        out.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{c_}" stroke-width="{sw}"/>')
    return "".join(out)


def pill(c, surface):
    """Web address in a high-contrast pill, bottom right, same as the billboards."""
    if surface in (R, DR, FLOOR):
        plate, ink, mark = I, W, Y
    elif surface in (P, E, Y, W, "ecg"):
        plate, ink, mark = I, W, R
    else:
        plate, ink, mark = Y, I, R
    x1, y1 = c.W - M, c.H - PILL_B
    x0, y0 = x1 - PILL_W, y1 - PILL_H
    k = PILL_H / 172
    mid = y0 + PILL_H / 2
    return (rect(round(x0), round(y0), round(PILL_W), round(PILL_H), plate, round(PILL_H / 2))
            + f'<path transform="translate({x0 + 0.035 * U:.0f} {mid:.0f}) scale({k:.3f})" d="M0 0 h40 l15 -36 l21 68 l21 -80 l15 46 h46" '
              f'fill="none" stroke="{mark}" stroke-width="15" stroke-linejoin="round" stroke-linecap="round"/>'
            + t(round(x1 - 0.045 * U), round(mid + 0.355 * PILL_T), SITE_URL, round(PILL_T), O, 800, ink, "end"))


# ------------------------------------------------------------------ art pieces (billboard coordinates)
v = V2
ARTS = {
    "climber": rough(shift(v["climber"].replace(I, R), 9, 7)) + rough(v["climber"]) + v["puffs"](3700, 250, GREY, 3, 0.75),
    "ankle": circle(3950, 680, 600, E) + f'<ellipse cx="3860" cy="1196" rx="520" ry="24" {V3["SHADOW"]}/>' + V3["ankle"],
    "bed": V3["win"] + V3["bed"] + V3["person"] + V3["blanket"],
    "runner": rough(v["runner"](2960, I, R, P) + v["pain"]),
    "head": V3["head"],
    # the same head inside a round frame, for tall formats where it can't run off the bottom
    "head-round": ('<clipPath id="headround"><circle cx="610" cy="790" r="650"/></clipPath>' + circle(610, 790, 650, E)
                   + '<g clip-path="url(#headround)">' + V3["head"] + "</g>"),
    "flexer": rough(shift(v["flexer"](4180, R, R, R), 10, 8) + v["flexer"](4180, I, R, P)),
    "sign": rough(shift(rect(300, 130, 1200, 930, R, 60), 14, 10)) + rough(v["sign"]),
    "bp-arm": V3["armB"] + V3["device"],
    "tire": rough(shift(circle(v["tcx"], v["tcy"], 430, R), 16, 12) + v["tire"]),
    "tubes": rough(v["tube"](2680, R, 560) + v["tube"](2830, Y, 640) + v["tube"](2980, GN, None) + v["rack"]),
    "dial": rough(v["cluster"]),
    "calendar": rough(shift(rect(3470, 300, 1000, 860, R, 40), 16, 12) + v["calendar"] + v["pencil"]),
    "cpr": V3["rescuer_back"] + V3["patient"] + V3["arms"] + V3["handsC"] + V3["motion"],
    "disco": rough(v["record"]) + rough(shift(v["disco"](R, R, R), 10, 8) + v["disco"](I, R, P)) + rough(v["notes"]),
    "chart": V3["hatch"] + V3["chart"],
    "face": V3["face"],
    "heart": rough(shift(v["heart"].replace(R, DR), 14, 10) + v["heart"]),
}
BOXES_PATH = os.path.join(HERE, "art-boxes.json")
BOX = json.load(open(BOXES_PATH)) if os.path.exists(BOXES_PATH) else {}
# art that runs off an edge of the billboard keeps that edge
BOX_EDGE = {"ankle": {1: 0}, "head": {3: 1400}, "bp-arm": {2: 4800}, "cpr": {2: 4800, 3: 1145}}
BOX["head-round"] = [-46, 134, 1266, 1446]


def box(name):
    b = list(BOX[name])
    for i, val in BOX_EDGE.get(name, {}).items():
        b[i] = val
    return tuple(b)


# ------------------------------------------------------------------ special blocks
class Stairs(Flex):
    """hf-A: the words climb a staircase; a breathless figure stops on the top step."""
    words = ["Breathless", "on", "stairs?"]
    pad = 0.22

    def size(self, B):
        ems = [serif().em(w_) for w_ in self.words]
        self.ems = ems
        self.s = min(0.17 * U, ((B.ex1 - B.ex0) - 2 * M) / (ems[0] + ems[1] + ems[2] * 0.94 + 5 * self.pad + 1.7))
        return self.s

    def __init__(self):
        super().__init__(2.0, 0.0)

    def rmax(self, c):
        return 3.4 if c.tall else 2.3

    def hrange(self, B):
        s = self.size(B)
        return 1.0 * s + 2 * 0.9 * s + 1.62 * s, 1.0 * s + 2 * self.rmax(B.c) * s + 1.62 * s

    def render(self, B):
        s, ems, p = self.size(B), self.ems, self.pad
        yb = B.y + B.h
        y1 = yb - 1.0 * s
        r = max(0.75 * s, min(self.rmax(B.c) * s, (B.h - 1.0 * s - 1.62 * s) / 2))
        y2, y3 = y1 - r, y1 - 2 * r
        xa = B.ex0 + M + ems[0] * s + p * s
        xb = xa + p * s + ems[1] * s + p * s
        steps = (rect(B.ex0 - 60, y1, xa + 20 - (B.ex0 - 60), yb + 90 - y1, R)
                 + rect(xa, y2, xb + 20 - xa, yb + 90 - y2, R)
                 + rect(xb, y3, B.ex1 + 60 - xb, yb + 90 - y3, R))
        out = rough(steps, "roughBig")
        out += t(round(B.ex0 + M), round(y1 - 0.13 * s), "Breathless", round(s))
        out += t(round(xa + p * s), round(y2 - 0.13 * s), "on", round(s))
        out += t(round(xb + p * s), round(y3 - 0.13 * s), "stairs?", round(s * 0.94))
        k = s / 300
        cx = xb + p * s + ems[2] * s * 0.94 + 0.3 * s
        out += f'<g transform="translate({cx - 3395 * k:.1f} {y3 + 4 * k - 578 * k:.1f}) scale({k:.4f})">{ARTS["climber"]}</g>'
        return out


class Swell(Fixed):
    """hf-B: 'Swollen' then 'ankles?' with each letter bigger than the last."""
    K = [1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.27]

    def fit(self, w, c):
        st = serif(R)
        e1 = st.em("Swollen")
        e2 = sum(st.em(ch) * k for ch, k in zip("ankles?", self.K))
        self.size = min(self.max * U * self.scale * c.k, w / max(e1, e2 * 1.02))
        s = self.size
        self.b1 = ASC * s
        self.b2 = self.b1 + 0.28 * s + 0.72 * self.K[-1] * s
        return self.b2 + 0.12 * s

    def render(self, B):
        s = self.size
        spans = "".join(f'<tspan font-size="{s * k:.0f}">{ch}</tspan>' for ch, k in zip("ankles?", self.K))
        return (t(round(B.x), round(B.y + self.b1), "Swollen", round(s), G, 800, R)
                + f'<text x="{B.x:.0f}" y="{B.y + self.b2:.0f}" font-family="{G}" font-weight="800" fill="{R}">{spans}</text>')


class Droop(Fixed):
    """stroke-B: 'Face drooping?' with the letters of 'drooping?' sliding down."""
    word = "drooping?"

    def fit(self, w, c):
        st = serif(W)
        self.adv = [st.em(ch) + 0.02 for ch in self.word]
        tot = sum(self.adv) + 0.15
        cap = self.max * U * self.scale * c.k
        one = min(cap, w / (st.em("Face ") + tot))
        two = min(cap, w / max(st.em("Face"), tot))
        self.one = one >= 0.86 * two
        s = self.size = one if self.one else two
        drop = 384 / 330 * s
        self.b1 = ASC * s
        self.b2 = self.b1 if self.one else self.b1 + 1.0 * s
        self.x2 = st.em("Face ") * s if self.one else 0
        return self.b2 + drop + 0.32 * s

    def render(self, B):
        s, out = self.size, t(round(B.x), round(B.y + self.b1), "Face", round(self.size), G, 800, W)
        x = B.x + self.x2
        for i, ch in enumerate(self.word):
            dy, rot = 6 * i * i * s / 330, min(i * 3, 18)
            yy = B.y + self.b2 + dy
            out += (f'<text x="{x:.0f}" y="{yy:.0f}" font-family="{G}" font-weight="800" font-size="{s:.0f}" fill="{W}" '
                    f'transform="rotate({rot} {x:.0f} {yy:.0f})">{ch}</text>')
            x += self.adv[i] * s
        return out


class Dots(Fixed):
    """bp-B: a dotted line that ends in 'nothing.'"""

    def __init__(self, max=0.1, gap=0.5):
        super().__init__(gap, max)

    def fit(self, w, c):
        self.size = min(self.max * U * self.scale * c.k, w * 0.42 / serif(R, 700, True).em("nothing."))
        return (ASC + DESC) * self.size

    def render(self, B):
        s = self.size
        nw = serif(R, 700, True).em("nothing.") * s
        base = B.y + ASC * s
        x_end = B.x + B.w - nw - 0.25 * s
        step = 0.41 * s
        dots = "".join(circle(round(B.x + 0.07 * s + k * step), round(base - 0.18 * s), round(0.07 * s), GREY)
                       for k in range(int((x_end - B.x) / step)))
        return dots + t(round(B.x + B.w), round(base), "nothing.", round(s), G, 700, R, "end", italic=True)


def road(c, rh):
    """bp-A: a road across the bottom of the canvas."""
    y, k, w, h = c.H - rh, rh / 290, c.W, c.H
    out = (path(f"M-50 {y + 0.13 * rh:.0f} C {w * 0.25:.0f} {y:.0f} {w * 0.67:.0f} {y:.0f} {w + 50} {y + 0.13 * rh:.0f} L{w + 50} {h + 50} L-50 {h + 50} Z", fill=A2)
           + "".join(rect(round(x), round(y + 0.36 * rh), round(180 * k), round(22 * k), Y, round(8 * k)) for x in [140 * k + j * 380 * k for j in range(int(w / (380 * k)) + 1)])
           + path(f"M-50 {y - 0.1 * rh:.0f} C {w * 0.12:.0f} {y - 0.37 * rh:.0f} {w * 0.23:.0f} {y - 0.23 * rh:.0f} {w * 0.33:.0f} {y - 0.3 * rh:.0f} "
                  f"C {w * 0.48:.0f} {y - 0.4 * rh:.0f} {w * 0.6:.0f} {y - 0.2 * rh:.0f} {w * 0.75:.0f} {y - 0.34 * rh:.0f} "
                  f"C {w * 0.85:.0f} {y - 0.43 * rh:.0f} {w * 0.94:.0f} {y - 0.27 * rh:.0f} {w + 50} {y - 0.3 * rh:.0f}", stroke=MID, sw=round(10 * k)))
    return rough(out, "roughBig")


class Floor(Flex):
    """cpr-A: the CPR scene on a floor that runs to the bottom right corner."""
    FH = 0.14 * U

    def hrange(self, B):
        bx = box("cpr")
        hi = (bx[3] - bx[1]) * min((B.ex1 - B.x) / (bx[2] - bx[0]), 1.9)
        return self.FH + 0.35 * hi, self.FH + hi

    def render(self, B):
        c, bx = B.c, box("cpr")
        fy = c.H - self.FH
        s = min((B.ex1 - B.x) / (bx[2] - bx[0]), (fy - B.y) / (bx[3] - bx[1]), 1.9)
        ax = B.ex1 - (bx[2] - bx[0]) * s
        return (rect(round(B.ex0 - 60), round(fy), round(B.ex1 - B.ex0 + 120), round(self.FH + 60), FLOOR)
                + f'<g transform="translate({ax - bx[0] * s:.1f} {fy - bx[3] * s:.1f}) scale({s:.4f})">{ARTS["cpr"]}</g>')


class Ecg(Flex):
    """stroke-C: an uneven heart trace across the column."""

    def __init__(self):
        super().__init__(0.35, 0.04)

    def hrange(self, B):
        return 0.08 * U, 0.15 * U

    def render(self, B):
        k = B.h / 290
        L = B.w / k
        rnd = random.Random(7)
        d, x = "M0 230", 0
        while x < L - 320:
            x += rnd.randint(90, 260)
            d += f" L{x} {230 + rnd.randint(-12, 12)} l14 -{rnd.randint(120, 200)} l16 {rnd.randint(170, 250)} l12 -{rnd.randint(30, 60)}"
            x += 42
        d += f" L{L:.0f} 230"
        return rough(f'<g transform="translate({B.x:.0f} {B.y:.0f}) scale({k:.4f})"><path d="{d}" fill="none" stroke="{R}" '
                     f'stroke-width="16" stroke-linejoin="round" stroke-linecap="round"/></g>')


class Grid(Flex):
    """stroke-A: B E F A S T as a grid of cells; T is a red tile."""
    CELLS = [("B", "Balance", "icon_b"), ("E", "Eyes", "icon_e"), ("F", "Face", "icon_f"),
             ("A", "Arms", "icon_a"), ("S", "Speech", "icon_s"), ("T", "Time: call 911", "icon_t")]
    IB = (-190, 320, 195, 655)   # icon box when drawn at cx = 0

    def __init__(self, cols, rows):
        super().__init__(1.0, 0.04)
        self.cols, self.rows, self.g = cols, rows, 0.03 * U

    def cw(self, w):
        return (w - (self.cols - 1) * self.g) / self.cols

    def hrange(self, B):
        cw = self.cw(B.w)
        return self.rows * cw * 0.85 + (self.rows - 1) * self.g, self.rows * cw * 1.3 + (self.rows - 1) * self.g

    def render(self, B):
        cw = self.cw(B.w)
        ch = (B.h - (self.rows - 1) * self.g) / self.rows
        ci = ch * 0.84
        ls = min(0.42 * ci, 0.95 * cw)
        ll = min(0.105 * ci, min(0.88 * cw / em(lab, O, 800) for _, lab, _ in self.CELLS))
        si = min(0.3 * ci / 335, 0.62 * cw / 385)
        tot = 335 * si + 0.07 * ci + 0.72 * ls + 0.1 * ci + 0.72 * ll
        out = ""
        for i, (L_, lab, fn) in enumerate(self.CELLS):
            x = B.x + (i % self.cols) * (cw + self.g)
            y = B.y + (i // self.cols) * (ch + self.g)
            tile = L_ == "T"
            ink, letter = (W, W) if tile else (I, R)
            if tile:
                out += rough(rect(round(x), round(y), round(cw), round(ch), R, round(0.03 * U)), "roughBig")
            top = y + (ch - tot) / 2
            cx = x + cw / 2
            out += f'<g transform="translate({cx:.0f} {top - 320 * si:.1f}) scale({si:.4f})">{rough(v[fn](0, ink))}</g>'
            lb = top + 335 * si + 0.07 * ci + 0.72 * ls
            out += t(round(cx), round(lb), L_, round(ls), O, 900, letter, "middle")
            out += t(round(cx), round(lb + 0.1 * ci + 0.72 * ll), lab, round(ll), O, 800, ink, "middle")
        return out


# ------------------------------------------------------------------ the boards
def note_scad():
    return "SCAD can cause heart attacks in women who seem healthy."


def hfA(c):
    cta = Text(st=sans(Y), max=0.14, options=[["Check your heart."], ["Check your", "heart."]])
    return dict(bg=P, dark=False, pill=A, mode="top",
                stack=[Stairs(), Panel(A, [cta], to_bottom=True)],
                cols=[Col(0.7, [Stairs()], bleed_bottom=True, foot=False),
                      Col(0.3, [Text(["Check", "your", "heart."], sans(Y), max=0.17)], fill=A)])


def hfB(c):
    ask = lambda: Text(["Ask about heart failure."], sans(I, 800), max=0.08, options=[["Ask about heart failure."], ["Ask about", "heart failure."]])
    art = lambda: Art(ARTS["ankle"], box("ankle"), bleed="top", valign="start", halign="end" if not c.wide else "middle")
    return dict(bg=P, dark=False,
                stack=[art(), Swell(max=0.13, gap=0.35), ask()],
                cols=[Col(0.56, [Swell(max=0.15, gap=0.35), ask()]), Col(0.44, [art()])])


def hfC(c):
    head = lambda: Text(st=serif(W), options=[["Need extra pillows", "to breathe?"], ["Need extra", "pillows to", "breathe?"]])
    cta = lambda: Text(["Tell your doctor."], sans(Y, 800), max=0.09)
    art = lambda: Art(ARTS["bed"], box("bed"))
    return dict(bg=A, dark=True, stack=[head(), art(), cta()],
                cols=[Col(0.42, [art()]), Col(0.58, [head(), cta()])])


def fmdA(c):
    head = lambda: Text(st=serif(I), options=[["Young. Healthy.", "Chest pain?"], ["Young.", "Healthy.", "Chest pain?"]])
    note = lambda: Text(st=sans(I, 700), wrap=note_scad(), size=0.032)
    art = lambda: Art(ARTS["runner"], box("runner"), maxs=1.7)
    return dict(bg=Y, dark=False, pill=R,
                stack=[head(), note(), art(), Panel(R, [Text(["Call 911."], sans(W), max=0.2)], to_bottom=True)],
                cols=[Col(0.46, [head(), note()]), Col(0.2, [art()]),
                      Col(0.34, [Text(["Call", "911."], sans(W), max=0.22)], fill=R)])


def fmdB(c):
    head = lambda: Text(st=serif(I), options=[["Heartbeat", "in your ear?"], ["Heartbeat in your ear?"]])
    cta = lambda: Text(["Tell a doctor."], sans(R, 800), max=0.09)
    note = lambda: Text(st=sans(SOFT, 600), wrap="A whooshing sound in time with your pulse can be one sign of FMD.", size=0.03, gap=0.3)
    bust = lambda: Art(ARTS["head"], box("head"), bleed="bottom", valign="end", maxs=1.8)
    cols = lambda f: [Col(f, [bust()], bleed_bottom=True, foot=False), Col(1 - f, [head(), cta(), note()])]
    return dict(bg=P, dark=False,
                stack=[head(), cta(), note(), Art(ARTS["head-round"], box("head-round"), maxs=1.4)],
                cols=cols(0.36))


def fmdC(c):
    quote = lambda: Text(st=serif(W, 700, True), strike=True, gap=0.45,
                         options=[["“I’m too healthy", "for a heart attack.”"], ["“I’m too", "healthy for a", "heart attack.”"]])
    cta = lambda: Text(st=sans(Y), max=0.1, options=[["Chest pain? Call 911."], ["Chest pain?", "Call 911."]])
    note = lambda: Text(st=sans(GREY, 700), wrap=note_scad(), size=0.03)
    art = lambda: Art(ARTS["flexer"], box("flexer"), maxs=1.7)
    return dict(bg=A, dark=True, stack=[quote(), cta(), art(), note()],
                cols=[Col(0.62, [quote(), cta(), note()]), Col(0.38, [art()])])


def bpA(c):
    rh = 0.17 * U
    head = lambda: Text(["Stay under it."], serif(W), max=0.15, gap=0.25)
    cta = lambda: Text(["Check yours."], sans(Y), max=0.1)
    sign = lambda: Art(ARTS["sign"], box("sign"), valign="end", maxs=1.9)
    return dict(bg=A, dark=True, pill=A2, under=lambda c: road(c, rh), y1=lambda c: c.H - rh * 0.88,
                stack=[head(), cta(), sign()],
                cols=[Col(0.42, [sign()], mode="spread"), Col(0.58, [head(), cta()])])


def bpB(c):
    head = lambda: Text(st=serif(I), gap=0.1, options=[["High blood", "pressure", "feels like"], ["High blood pressure", "feels like"]])
    art = lambda: Art(ARTS["bp-arm"], box("bp-arm"), bleed="right", maxs=1.8)
    cta = lambda: Text(["Get it checked."], sans(R), max=0.1)
    return dict(bg=P, dark=False, stack=[head(), Dots(), art(), cta()],
                cols=[Col(0.6, [head(), Dots(), cta()]), Col(0.4, [art()])])


def bpC(c):
    a = lambda: Text(["You check your", "tire pressure."], serif(I, 700), max=0.13)
    b = lambda: Text(["Check your", "blood pressure."], serif(R), max=0.13)
    art = lambda: Art(ARTS["tire"], box("tire"), maxs=1.6)
    return dict(bg=Y, dark=False, stack=[a(), art(), b()],
                cols=[Col(0.62, [a(), b()]), Col(0.38, [art()])])


def cholA(c):
    head = lambda: Text([[("No symptoms.", serif(W))], [("One blood test.", serif(Y))]], serif(W), max=0.15)
    art = lambda: Art(ARTS["tubes"], box("tubes"), maxs=1.7)
    cta = lambda: Text(st=sans(W), max=0.09, options=[["Get your cholesterol", "checked."], ["Get your", "cholesterol", "checked."]])
    return dict(bg=A, dark=True, stack=[head(), art(), cta()],
                cols=[Col(0.48, [head()]), Col(0.2, [art()]), Col(0.32, [Text(["Get your", "cholesterol", "checked."], sans(W), max=0.1)])])


def cholB(c):
    head = lambda: Text(st=serif(W), options=[["Your heart has", "no warning light."], ["Your heart", "has no warning", "light."]])
    cta = lambda: Text(["Get a cholesterol test."], sans(Y), max=0.09, options=[["Get a cholesterol test."], ["Get a", "cholesterol test."]])
    art = lambda: Art(ARTS["dial"], box("dial"), maxs=1.6)
    return dict(bg=I, dark=True, stack=[head(), art(), cta()],
                cols=[Col(0.38, [art()]), Col(0.62, [head(), cta()])])


def cholC(c):
    head = lambda: Text(st=serif(I), options=[["When was your last", "cholesterol test?"], ["When was", "your last", "cholesterol test?"]])
    cta = lambda: Text(st=sans(R), max=0.09, options=[["Can’t remember? Book one."], ["Can’t remember?", "Book one."]])
    art = lambda: Art(ARTS["calendar"], box("calendar"), maxs=1.6)
    return dict(bg="ecg", dark=False, stack=[head(), art(), cta()],
                cols=[Col(0.64, [head(), cta()]), Col(0.36, [art()])])


def cprA(c):
    head = lambda: Text(["Push hard.", "Push fast."], serif(W), max=0.18)
    sub = lambda: Text([[("100–120 a minute", sans(Y))], [("Call 911 first.", sans(W))]], sans(W), max=0.085)
    return dict(bg=R, dark=False, pill=FLOOR,
                stack=[head(), sub(), Floor()],
                cols=[Col(0.56, [head(), sub()], foot=False), Col(0.44, [Floor()], bleed_bottom=True)])


def cprB(c):
    head = lambda: Text(st=serif(W), gap=0.15, options=[["Know “Stayin’ Alive”?"], ["Know", "“Stayin’ Alive”?"]])
    know = lambda: Text(["You know CPR."], serif(Y, 800, True), max=0.15)
    art = lambda: Art(ARTS["disco"], box("disco"), maxs=1.6)
    cta = lambda: Text(st=sans(W, 800), max=0.065, options=[["Call 911. Push hard and fast to the beat."], ["Call 911. Push hard", "and fast to the beat."]])
    return dict(bg=A, dark=True, stack=[head(), know(), art(), cta()],
                cols=[Col(0.38, [art()]), Col(0.62, [head(), know(), cta()])])


def cprC(c):
    head = lambda: Text(st=serif(I), options=[["Start CPR before", "help arrives."], ["Start CPR", "before help", "arrives."]])
    cta = lambda: Text(st=sans(R), max=0.085, options=[["Call 911. Push hard and fast."], ["Call 911.", "Push hard and fast."]])
    note = lambda: Text(st=sans(SOFT, 600), size=0.027,
                        wrap="Immediate CPR can double or triple chances of survival after cardiac arrest. Source: American Heart Association")
    art = lambda: Art(ARTS["chart"], box("chart"), maxs=1.3)
    return dict(bg=P, dark=False, stack=[head(), cta(), art(), note()],
                cols=[Col(0.44, [head(), cta(), note()]), Col(0.56, [art()])])


def strokeA(c):
    spot = Text(["Spot a stroke:"], serif(I, 700, True), max=0.09)
    if c.wide:
        return dict(bg=P, dark=False, stack=[spot, Grid(6, 1)], mode="center")
    return dict(bg=P, dark=False, stack=[spot, Grid(2, 3) if c.tall else Grid(3, 2)])


def strokeB(c):
    ask = lambda: Text(st=sans(W, 800), max=0.07, options=[[[("Ask them to smile. ", sans(W, 800)), ("Uneven?", sans(Y))]],
                                                         [[("Ask them to smile.", sans(W, 800))], [("Uneven?", sans(Y))]]])
    call = lambda: Text(["Call 911."], sans(Y), max=0.15, gap=0.2)
    every = lambda: Text(["Every minute counts."], sans(W, 700), max=0.07)
    art = lambda: Art(ARTS["face"], box("face"), maxs=1.5)
    cols = lambda f: [Col(f, [Droop(max=0.16), call(), every()]), Col(1 - f, [art(), ask()])]
    return dict(bg=A, dark=True, stack=[Droop(max=0.15), art(), ask(), call(), every()],
                sqcols=cols(0.54), cols=cols(0.58))


def strokeC(c):
    head = lambda: Text(st=serif(I), options=[["Fluttering heartbeat?"], ["Fluttering", "heartbeat?"]])
    afib = lambda: Text(["AFib can lead to stroke."], sans(I, 800), max=0.085, options=[["AFib can lead to stroke."], ["AFib can lead", "to stroke."]])
    see = lambda: Text(["See a doctor."], sans(R), max=0.1)
    art = lambda: Art(ARTS["heart"], box("heart"), maxs=1.6)
    return dict(bg="ecg", dark=False, stack=[head(), afib(), art(), Ecg(), see()],
                cols=[Col(0.64, [head(), afib(), Ecg(), see()]), Col(0.36, [art()])])


BOARDS = {"hf-A": hfA, "hf-B": hfB, "hf-C": hfC, "fmd-A": fmdA, "fmd-B": fmdB, "fmd-C": fmdC,
          "bp-A": bpA, "bp-B": bpB, "bp-C": bpC, "chol-A": cholA, "chol-B": cholB, "chol-C": cholC,
          "cpr-A": cprA, "cpr-B": cprB, "cpr-C": cprC, "stroke-A": strokeA, "stroke-B": strokeB, "stroke-C": strokeC}


def build(bid, fmt, w, h):
    c = Ctx(fmt, w, h)
    sp = BOARDS[bid](c)
    body = background(sp["bg"], w, h) + (sp["under"](c) if sp.get("under") else "")
    if c.wide and "cols" in sp:
        body += layout_cols(sp["cols"], c, sp)
    elif c.fmt == "square" and "sqcols" in sp:
        body += layout_cols(sp["sqcols"], c, sp)
    else:
        body += layout_stack(sp["stack"], c, sp)
    body += f'<rect x="0" y="0" width="{w}" height="{h}" filter="url(#grain)"/>' + pill(c, sp.get("pill", sp["bg"]))
    title = next(m["headline"] for m in V2["meta"] if m["id"] == bid)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>{title}</title>{defs(sp["dark"])}{body}</svg>')


os.makedirs(OUT, exist_ok=True)
if PROBE:
    for name, art in ARTS.items():
        open(os.path.join(OUT, name + ".svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-600 -600 6000 2600" width="3000" height="1300">{defs(False)}{art}</svg>')
    print(len(ARTS), "art probes written")
    sys.exit(0)

files = []
for bid in BOARDS:
    for fmt, w, h, label, use in FORMATS:
        svg_ = build(bid, fmt, w, h)
        name = f"{bid}-{fmt}.svg"
        open(os.path.join(OUT, name), "w").write(svg_)
        files.append(dict(id=bid, format=fmt, file=name, width=w, height=h))
if MISSING:
    json.dump(sorted(MISSING), open(os.path.join(HERE, "measure-req.json"), "w"), ensure_ascii=False)
    print(f"{len(MISSING)} text widths missing; measure them and run again")
    sys.exit(3)
json.dump(dict(formats=[dict(id=f, width=w, height=h, label=lb, use=u) for f, w, h, lb, u in FORMATS], files=files),
          open(os.path.join(OUT, "formats.json"), "w"), indent=1)
print(len(files), "files written")
