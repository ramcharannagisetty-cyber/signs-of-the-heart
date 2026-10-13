"""Billboards v2: same 18 messages, now with hand-built illustrations in a screen-print / linocut style.
Everything is drawn here as vector shapes (no photos, no outside images). Wobbly edges come from an SVG
displacement filter, plus halftone dots, colour misregistration and paper grain.
usage: python3 -I make_boards_v2.py <out_dir>
"""
import json, math, os, random, sys

OUT = sys.argv[1]
G = "EB Garamond, Garamond, Georgia, serif"
O = "Overpass, Arial, Helvetica, sans-serif"
R, DR, Y, A, P, E, EG, GN, I, W = "#c8102e", "#8f0b21", "#ffc72c", "#1f262b", "#fffbfa", "#fcebe7", "#f3b6ac", "#0e6b47", "#1c1517", "#ffffff"
A2, GREY, MID = "#2b343a", "#b9b0ae", "#4a545b"


# ------------------------------------------------------------------ primitives
def t(x, y, s, size, fam=G, wt=800, fill=I, anchor="start", italic=False, extra=""):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{wt}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}"{st} {extra}>{s}</text>')


def line(pts, w, color, extra=""):
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def limb(pts, w, fill, ink=I, ow=12):
    """Thick limb with an ink outline (outline drawn first, fill on top)."""
    return line(pts, w + 2 * ow, ink) + line(pts, w, fill)


def path(d, fill="none", stroke="none", sw=0, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def circle(cx, cy, r, fill="none", stroke="none", sw=0, extra=""):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def rect(x, y, w, h, fill, rx=0, stroke="none", sw=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def rough(inner, f="rough"):
    return f'<g filter="url(#{f})">{inner}</g>'


def shift(inner, dx, dy):
    return f'<g transform="translate({dx} {dy})">{inner}</g>'


def defs(dark):
    g = 1 if dark else 0
    a = 0.16 if dark else 0.13
    pats = "".join(
        f'<pattern id="dot{k}" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(20)"><circle cx="13" cy="13" r="6" fill="{c}"/></pattern>'
        for k, c in [("R", R), ("I", I), ("W", W), ("Y", Y), ("D", DR), ("G", GREY)])
    return (
        "<defs>"
        '<filter id="rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="11" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="11" xChannelSelector="R" yChannelSelector="G"/></filter>'
        '<filter id="roughBig" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="2" seed="4" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="22" xChannelSelector="R" yChannelSelector="G"/></filter>'
        f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="5" stitchTiles="stitch"/>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 {g}  0 0 0 0 {g}  0 0 0 0 {g}  0 0 0 {a} 0"/></filter>'
        + pats + "</defs>")


def grain():
    return '<rect x="0" y="0" width="4800" height="1400" filter="url(#grain)"/>'


SITE_URL = "heartsigns.vercel.app"


def signoff(color):
    """Big, high-contrast web address strip, same corner on every board so drivers can read and type it.
    color = the old sign-off colour, used only to tell light boards (I) from dark/red ones."""
    if color == I:            # light board: ink strip, white type
        plate, ink, mark = I, W, R
    elif color == W:          # red / mixed board: ink strip
        plate, ink, mark = I, W, Y
    else:                     # dark board: caution-yellow strip, ink type
        plate, ink, mark = Y, I, R
    return (rect(3180, 1140, 1560, 160, plate, 80)
            + f'<path d="M3250 1222 h40 l14 -34 l20 64 l20 -76 l14 44 h44" fill="none" stroke="{mark}" '
              f'stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>'
            + t(4680, 1256, SITE_URL, 104, O, 800, ink, "end"))


def ecg_grid():
    out = [rect(0, 0, 4800, 1400, E)]
    for x in range(0, 4801, 40):
        c, w = (EG, 4) if x % 200 == 0 else ("#f6d3cc", 2)
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="1400" stroke="{c}" stroke-width="{w}"/>')
    for y in range(0, 1401, 40):
        c, w = (EG, 4) if y % 200 == 0 else ("#f6d3cc", 2)
        out.append(f'<line x1="0" y1="{y}" x2="4800" y2="{y}" stroke="{c}" stroke-width="{w}"/>')
    return "".join(out)


def puffs(x, y, color, n=3, s=1.0):
    """Little breath curls."""
    out = ""
    for i in range(n):
        cx, cy, r = x + i * 46 * s, y - i * 30 * s, (22 + i * 6) * s
        out += path(f"M{cx - r} {cy} a{r} {r} 0 1 1 {r * 1.4:.0f} {r * 0.9:.0f}", stroke=color, sw=10 * s)
    return out


def sneaker(x, y, color=P, ink=I, flip=False):
    d = -1 if flip else 1
    return path(f"M{x - 40 * d} {y - 40} L{x + 60 * d} {y - 40} C{x + 110 * d} {y - 40} {x + 120 * d} {y + 5} {x + 110 * d} {y + 12} L{x - 50 * d} {y + 12} Z",
                fill=color, stroke=ink, sw=10)


def svg(title, dark, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4800 1400" width="4800" height="1400">'
            f'<title>{title}</title>{defs(dark)}{body}</svg>')


boards, meta = {}, []


def add(id_, topic, concept, words, inspired, action, title, dark, body):
    boards[id_] = svg(title, dark, body)
    meta.append(dict(id=id_, topic=topic, concept=concept, headline=words, inspired_by=inspired, action=action))


# ================================================================== HEART FAILURE
# hf-A: type climbs the stairs; a breathless figure stops on the top step
steps = rough(rect(-60, 1210, 1840, 300, R) + rect(1760, 890, 600, 600, R) + rect(2340, 570, 1520, 900, R), "roughBig")
climber = (limb([(3560, 380), (3520, 470), (3505, 566)], 40, I, I, 0) + limb([(3560, 380), (3640, 470), (3660, 566)], 40, I, I, 0)
           + line([(3560, 385), (3645, 235)], 76, I)
           + line([(3640, 245), (3672, 345), (3642, 455)], 36, I) + line([(3628, 255), (3598, 360), (3588, 432)], 36, I)
           + circle(3693, 178, 52, I) + sneaker(3515, 566, P, I, True) + sneaker(3665, 566, P, I))
add("hf-A", "heart-failure", "Type climbs a staircase", "Breathless on stairs? Check your heart.",
    "Typographic outdoor (The Economist): the words act out the message", "See a doctor about breathlessness",
    "Breathless on stairs? Check your heart.", False,
    rect(0, 0, 4800, 1400, P) + steps
    + rough(shift(climber.replace(I, R), 9, 7)) + rough(climber) + puffs(3700, 250, GREY, 3, 0.75)
    + t(160, 1170, "Breathless", 300) + t(1830, 850, "on", 300) + t(2400, 530, "stairs?", 280)
    + rough(rect(3800, -40, 1100, 1480, A), "roughBig")
    + t(3920, 560, "Check", 190, O, 900, Y) + t(3920, 780, "your", 190, O, 900, Y) + t(3920, 1000, "heart.", 190, O, 900, Y)
    + grain() + signoff(GREY))

# hf-B: swollen ankles; the letters swell, and so do the ankles (sock line digging in)
def leg(ox, oy, clip_id, sock=True, fill=P):
    d = (f"M{ox} {oy} C{ox - 20} {oy + 300} {ox - 40} {oy + 500} {ox - 60} {oy + 620} "
         f"C{ox - 130} {oy + 700} {ox - 120} {oy + 840} {ox - 60} {oy + 910} "
         f"C{ox - 70} {oy + 990} {ox - 20} {oy + 1040} {ox + 40} {oy + 1040} L{ox + 470} {oy + 1045} "
         f"C{ox + 545} {oy + 1045} {ox + 560} {oy + 990} {ox + 500} {oy + 965} "
         f"C{ox + 420} {oy + 935} {ox + 330} {oy + 900} {ox + 290} {oy + 860} "
         f"C{ox + 370} {oy + 800} {ox + 370} {oy + 690} {ox + 300} {oy + 640} "
         f"C{ox + 270} {oy + 520} {ox + 250} {oy + 300} {ox + 260} {oy} Z")
    out = f'<clipPath id="{clip_id}"><path d="{d}"/></clipPath>' + path(d, fill=fill, stroke=I, sw=16)
    if sock:
        stripes = "".join(rect(ox - 200, oy + 600 + k * 70, 900, 30, R) for k in range(0, 7))
        out += f'<g clip-path="url(#{clip_id})">{rect(ox - 200, oy + 590, 900, 600, W)}{stripes}{rect(ox - 200, oy + 560, 260, 700, "url(#dotR)", extra=chr(32) + "opacity=" + chr(34) + "0.5" + chr(34))}</g>'
        out += path(d, stroke=I, sw=16)
        # skin bulging over the sock top
        out += path(f"M{ox - 95} {oy + 600} C{ox - 30} {oy + 630} {ox + 200} {oy + 640} {ox + 330} {oy + 610}", stroke=I, sw=12)
        out += path(f"M{ox - 70} {oy + 570} C{ox} {oy + 595} {ox + 180} {oy + 600} {ox + 300} {oy + 575}", stroke=I, sw=6, extra='opacity="0.5"')
    return out


sizes = [300, 360, 420, 480, 540, 600, 680]
sw = "".join(f'<tspan font-size="{s}">{ch}</tspan>' for ch, s in zip("ankles?", sizes))
add("hf-B", "heart-failure", "Letters swell like ankles", "Swollen ankles? Ask about heart failure.",
    "Visual pun outdoor (one image, one idea); swelling is a top heart failure sign", "Ask a doctor about swelling",
    "Swollen ankles? Ask about heart failure.", False,
    ecg_grid() + t(160, 820, "Swollen", 300, G, 800, R)
    + f'<text x="1250" y="820" font-family="{G}" font-weight="800" fill="{R}">{sw}</text>'
    + t(160, 1120, "Ask about heart failure.", 170, O, 800, I)
    + rough('<g transform="translate(3330 -280) scale(1.3)">' + leg(380, 0, "legB", True, "#f7e6e2") + leg(0, 0, "legA", True) + "</g>")
    + grain() + signoff(I))

# hf-C: propped up on three pillows at night
def pillow(x, y, w, h):
    return path(f"M{x + 30} {y + 10} C{x + w * 0.3} {y - 18} {x + w * 0.7} {y - 18} {x + w - 30} {y + 10} "
                f"C{x + w + 20} {y + h * 0.5} {x + w + 20} {y + h * 0.5} {x + w - 30} {y + h - 10} "
                f"C{x + w * 0.7} {y + h + 18} {x + w * 0.3} {y + h + 18} {x + 30} {y + h - 10} "
                f"C{x - 20} {y + h * 0.5} {x - 20} {y + h * 0.5} {x + 30} {y + 10} Z", fill=P, stroke=I, sw=12)


bed = (rect(200, 430, 80, 780, MID, 20) + rect(1480, 760, 60, 450, MID, 20)
       + rect(200, 900, 1340, 150, P, 30, I, 12)
       + pillow(300, 800, 520, 100) + pillow(320, 700, 480, 100) + pillow(340, 600, 440, 100)
       + circle(690, 525, 74, P, I, 12)
       + path("M600 905 C 600 720 690 640 800 650 C 960 665 1100 760 1260 805 C 1400 845 1500 870 1545 905 Z", fill=R, stroke=I, sw=12)
       + path("M600 905 C 600 720 690 640 800 650 C 960 665 1100 760 1260 805 C 1400 845 1500 870 1545 905 Z", fill="url(#dotD)", extra='opacity="0.55"'))
moon = path("M1380 230 a110 110 0 1 0 110 150 a85 85 0 1 1 -110 -150 Z", fill=Y)
stars = "".join(circle(x, y, 9, Y) for x, y in [(1150, 260), (1250, 380), (980, 200), (1560, 470)])
add("hf-C", "heart-failure", "Need extra pillows?", "Need extra pillows to breathe? Tell your doctor.",
    "Conversational hook naming one specific, everyday sign (BHF heart attack symptom ads)", "Tell a doctor",
    "Need extra pillows to breathe? Tell your doctor.", True,
    rect(0, 0, 4800, 1400, A) + rough(moon + stars) + rough(bed) + puffs(790, 470, GREY, 3, 0.9)
    + t(1760, 560, "Need extra pillows", 260, G, 800, W) + t(1760, 840, "to breathe?", 260, G, 800, W)
    + t(1760, 1110, "Tell your doctor.", 170, O, 800, Y) + grain() + signoff(GREY))


# ================================================================== FMD / SCAD
def runner(x0, ink, shirt, skin):
    """A runner who has stopped, one hand pressed to her chest. x0 = centre line."""
    c = x0
    out = (limb([(c - 30, 760), (c - 60, 960), (c - 70, 1150)], 46, skin, ink, 10)
           + limb([(c + 20, 760), (c + 80, 960), (c + 110, 1150)], 46, skin, ink, 10)
           + sneaker(c - 70, 1158, P, ink, True) + sneaker(c + 112, 1158, P, ink)
           + limb([(c - 65, 480), (c - 110, 620), (c - 80, 735)], 38, skin, ink, 10)
           + path(f"M{c - 75} 450 L{c + 70} 450 L{c + 45} 770 L{c - 50} 770 Z", fill=shirt, stroke=ink, sw=12)
           + limb([(c + 65, 480), (c + 130, 600), (c + 30, 565)], 38, skin, ink, 10)
           + limb([(c, 380), (c, 450)], 34, skin, ink, 10)
           + circle(c + 5, 335, 70, skin, ink, 12)
           + path(f"M{c - 55} 300 C{c - 120} 300 {c - 170} 360 {c - 160} 440 C{c - 130} 400 {c - 100} 370 {c - 60} 360 Z", fill=ink)
           + path(f"M{c - 62} 300 C{c - 40} 250 {c + 40} 245 {c + 72} 300 C{c + 30} 290 {c - 20} 290 {c - 62} 300 Z", fill=ink))
    return out


pain = "".join(line([(3060 + 70 * math.cos(a), 545 + 70 * math.sin(a)), (3060 + 130 * math.cos(a), 545 + 130 * math.sin(a))], 14, R)
               for a in [-1.2, -0.6, 0, 0.6])
add("fmd-A", "fmd-scad", "Young. Healthy. Call 911.", "Young. Healthy. Chest pain? Call 911.",
    "Act FAST: one action, impossible to miss; breaks the 'too healthy' assumption", "Call 911 for chest pain",
    "Young. Healthy. Chest pain? Call 911.", False,
    rect(0, 0, 4800, 1400, Y) + t(160, 560, "Young. Healthy.", 300) + t(160, 960, "Chest pain?", 300)
    + t(160, 1250, "SCAD can cause heart attacks in women who seem healthy.", 70, O, 700, I)
    + rough(runner(2960, I, R, P) + pain)
    + rough(rect(3300, -40, 1600, 1480, R), "roughBig")
    + t(3460, 640, "Call", 400, O, 900, W) + t(3460, 1060, "911.", 400, O, 900, W) + grain() + signoff(W))

head = ("M300 1450 C 260 1100 170 820 250 560 C 320 330 560 190 770 205 C 970 220 1090 360 1100 520 "
        "L 1110 610 C 1115 650 1170 705 1180 745 C 1160 765 1120 775 1110 785 C 1120 820 1115 850 1095 862 "
        "C 1110 902 1100 932 1070 945 C 1030 985 970 1005 905 1015 L 885 1450 Z")
ear = "M520 560 C 585 515 660 560 660 640 C 660 705 615 725 605 765 C 595 805 560 828 528 805 C 505 765 540 722 518 680 Z"
waves = "".join(path(f"M{560 - r * 0.55:.0f} {650 - r:.0f} A {r} {r} 0 0 0 {560 - r * 0.55:.0f} {650 + r:.0f}", stroke=R, sw=22, extra=f'opacity="{o}"')
                for r, o in [(130, 1), (210, 0.8), (290, 0.55)])
blip = line([(330, 650), (380, 650), (400, 600), (425, 710), (445, 640), (470, 650)], 14, Y)
add("fmd-B", "fmd-scad", "Heartbeat you can hear", "Heartbeat in your ear? Tell a doctor.",
    "One strong visual + short line; turns an odd symptom (pulsatile tinnitus) into something people recognise", "Tell a doctor about a whooshing ear",
    "Heartbeat in your ear? Tell a doctor.", False,
    rect(0, 0, 4800, 1400, P) + rough(shift(path(head, fill=R), 14, 10) + path(head, fill=A) + path(ear, fill=P, stroke=I, sw=12)
                                     + path("M560 600 C 610 590 630 640 600 680", stroke=I, sw=10) + waves + blip)
    + t(1400, 620, "Heartbeat in your ear?", 280) + t(1400, 960, "Tell a doctor.", 180, O, 800, R)
    + t(1400, 1150, "A whooshing sound in time with your pulse can be one sign of FMD.", 70, O, 600, "#4d4245")
    + grain() + signoff(I))


def flexer(c, ink, shirt, skin):
    return (limb([(c - 30, 750), (c - 50, 960), (c - 60, 1140)], 46, skin, ink, 10)
            + limb([(c + 30, 750), (c + 70, 960), (c + 90, 1140)], 46, skin, ink, 10)
            + sneaker(c - 60, 1148, P, ink, True) + sneaker(c + 92, 1148, P, ink)
            + limb([(c - 70, 470), (c - 130, 600), (c - 60, 700)], 38, skin, ink, 10)
            + path(f"M{c - 75} 445 L{c + 75} 445 L{c + 50} 760 L{c - 50} 760 Z", fill=shirt, stroke=ink, sw=12)
            + limb([(c + 70, 470), (c + 200, 470), (c + 190, 330)], 40, skin, ink, 10)
            + path(f"M{c + 120} 445 C{c + 150} 400 {c + 190} 405 {c + 200} 450", fill=skin, stroke=ink, sw=10)
            + limb([(c, 380), (c, 445)], 34, skin, ink, 10)
            + circle(c, 330, 68, skin, ink, 12)
            + path(f"M{c - 50} 295 C{c - 120} 290 {c - 175} 350 {c - 170} 430 C{c - 140} 395 {c - 105} 365 {c - 58} 355 Z", fill=ink)
            + path(f"M{c - 60} 295 C{c - 35} 245 {c + 40} 240 {c + 68} 295 C{c + 25} 285 {c - 20} 285 {c - 60} 295 Z", fill=ink))


add("fmd-C", "fmd-scad", "The myth, struck out", "“Too healthy for a heart attack.” Chest pain? Call 911.",
    "Myth-busting PSA format: say what people think, then cross it out", "Call 911 for chest pain",
    "I'm too healthy for a heart attack. Chest pain? Call 911.", True,
    rect(0, 0, 4800, 1400, A)
    + t(200, 560, "“I’m too healthy", 240, G, 700, W, italic=True) + t(200, 860, "for a heart attack.”", 240, G, 700, W, italic=True)
    + rough(path("M180 495 L2240 470 M180 795 L2330 770", stroke=R, sw=20))
    + t(2700, 600, "Chest pain?", 170, O, 900, Y) + t(2700, 840, "Call 911.", 170, O, 900, Y)
    + rough(shift(flexer(4180, R, R, R), 10, 8) + flexer(4180, I, R, P))
    + t(200, 1150, "SCAD can cause heart attacks in women who seem healthy.", 70, O, 700, GREY) + grain() + signoff(GREY))

# ================================================================== BLOOD PRESSURE
road = (path("M-50 1150 C 1200 1110 3200 1110 4850 1150 L4850 1450 L-50 1450 Z", fill=A2)
        + "".join(rect(x, 1215, 180, 22, Y, 8) for x in range(140, 3400, 380))
        + path("M-50 1120 C 600 1040 1100 1080 1600 1060 C 2300 1030 2900 1090 3600 1050 C 4100 1025 4500 1070 4850 1060", stroke=MID, sw=10))
sign = (rect(870, 1060, 60, 140, GREY) + rect(300, 130, 1200, 930, W, 60)
        + rect(330, 160, 1140, 870, "none", 40, I, 22)
        + t(900, 330, "BLOOD", 120, O, 800, I, "middle") + t(900, 460, "PRESSURE", 120, O, 800, I, "middle")
        + t(900, 590, "LIMIT", 120, O, 800, I, "middle") + t(900, 950, "120/80", 270, O, 900, I, "middle"))
add("bp-A", "hypertension", "Speed-limit sign for your blood", "BLOOD PRESSURE LIMIT 120/80. Stay under it. Check yours.",
    "Borrow the road's own language (TAC road-safety outdoor); drivers read sign shapes instantly", "Check your blood pressure",
    "Blood pressure limit 120/80. Stay under it. Check yours.", True,
    rect(0, 0, 4800, 1400, A) + rough(road, "roughBig") + rough(shift(rect(300, 130, 1200, 930, R, 60), 14, 10)) + rough(sign)
    + t(1800, 600, "Stay under it.", 320, G, 800, W) + t(1800, 900, "Check yours.", 200, O, 900, Y) + grain() + signoff(GREY))

gauge_ticks = "".join(line([(4330 + 108 * math.cos(math.radians(a)), 300 + 108 * math.sin(math.radians(a))),
                            (4330 + 132 * math.cos(math.radians(a)), 300 + 132 * math.sin(math.radians(a)))], 10, I) for a in range(150, 391, 30))
ang = math.degrees(math.atan2(380, -580))
arm = (rect(3700, 1000, 1200, 44, GREY, 10, I, 10) + rect(3760, 1044, 40, 160, GREY, 8, I, 8)
       + limb([(4900, 500), (4320, 880), (3960, 930)], 170, P, I, 14)
       + circle(3885, 920, 78, P, I, 14) + "".join(line([(3830, y), (3870, y)], 8, I) for y in (885, 915, 945))
       + f'<g transform="rotate({ang:.1f} 4640 670)">' + rect(4510, 555, 260, 230, A, 22, I, 12) + rect(4530, 575, 18, 190, MID, 6) + rect(4732, 575, 18, 190, MID, 6) + "</g>"
       + path("M4600 575 C 4500 430 4230 600 4090 520", stroke=I, sw=16)
       + path("M4700 770 C 4760 850 4720 920 4740 960", stroke=I, sw=16)
       + path("M4740 960 C 4680 960 4670 1090 4740 1100 C 4810 1090 4800 960 4740 960 Z", fill=R, stroke=I, sw=12)
       + circle(4090, 380, 145, W, I, 16)
       + path(f"M{4090 + 120 * math.cos(math.radians(330)):.0f} {380 + 120 * math.sin(math.radians(330)):.0f} A120 120 0 0 1 {4090 + 120 * math.cos(math.radians(390)):.0f} {380 + 120 * math.sin(math.radians(390)):.0f}", stroke=R, sw=26)
       + "".join(line([(4090 + 108 * math.cos(math.radians(d)), 380 + 108 * math.sin(math.radians(d))), (4090 + 132 * math.cos(math.radians(d)), 380 + 132 * math.sin(math.radians(d)))], 10, I) for d in range(150, 391, 30))
       + line([(4090, 380), (4090 + 110 * math.cos(math.radians(355)), 380 + 110 * math.sin(math.radians(355)))], 14, R) + circle(4090, 380, 18, I))
dots = "".join(circle(x, 770, 12, GREY) for x in range(1720, 2980, 70))
add("bp-B", "hypertension", "Feels like nothing", "High blood pressure feels like nothing. Get it checked.",
    "Empty space as the message (classic 'silent killer' outdoor); the blank board IS the symptom", "Get your blood pressure checked",
    "High blood pressure feels like nothing. Get it checked.", False,
    rect(0, 0, 4800, 1400, P) + t(160, 470, "High blood pressure", 300) + t(160, 800, "feels like", 300)
    + dots + t(3040, 800, "nothing.", 170, G, 700, R, italic=True) + t(160, 1150, "Get it checked.", 170, O, 900, R)
    + rough(arm) + grain() + signoff(I))

tcx, tcy = 4160, 690
treads = "".join(f'<rect x="{tcx - 34}" y="{tcy - 470}" width="68" height="70" rx="10" fill="{I}" transform="rotate({a} {tcx} {tcy})"/>' for a in range(0, 360, 20))
spokes = "".join(line([(tcx, tcy), (tcx + 230 * math.cos(math.radians(a)), tcy + 230 * math.sin(math.radians(a)))], 34, MID) for a in range(-90, 270, 72))
tire = (treads + circle(tcx, tcy, 430, A, I, 14) + circle(tcx, tcy, 400, "none", MID, 8) + circle(tcx, tcy, 270, GREY, I, 14)
        + spokes + circle(tcx, tcy, 90, P, I, 12) + circle(tcx, tcy, 26, I)
        + f'<g transform="rotate(-38 {tcx - 200} {tcy - 200})">' + rect(tcx - 230, tcy - 620, 60, 430, GREY, 14, I, 10)
        + rect(tcx - 222, tcy - 760, 44, 160, W, 8, I, 8) + "".join(line([(tcx - 222, y), (tcx - 200, y)], 6, I) for y in range(tcy - 740, tcy - 610, 26)) + "</g>")
add("bp-C", "hypertension", "Tire pressure vs blood pressure", "You check your tire pressure. Check your blood pressure.",
    "Speak to the driver reading it, about something they already do (hyper-relevant copy)", "Check your blood pressure",
    "You check your tire pressure. Check your blood pressure.", False,
    rect(0, 0, 4800, 1400, Y) + t(160, 600, "You check your tire pressure.", 230, G, 700, I)
    + t(160, 1000, "Check your blood pressure.", 260, G, 800, R) + rough(shift(circle(tcx, tcy, 430, R), 16, 12) + tire)
    + grain() + signoff(I))

# ================================================================== CHOLESTEROL
def tube(x, cap, blood):
    out = rect(x, 330, 100, 730, P, 50, I, 12)
    if blood:
        out += path(f"M{x + 6} {blood} L{x + 94} {blood} L{x + 94} 1010 C{x + 94} 1060 {x + 6} 1060 {x + 6} 1010 Z", fill=DR)
        out += rect(x + 6, blood, 88, 120, "url(#dotR)", extra='opacity="0.7"')
    out += rect(x - 10, 290, 120, 110, cap, 18, I, 12) + rect(x + 22, 470, 16, 400, W, 8, extra='opacity="0.55"')
    return out


rack = rect(2620, 820, 520, 70, GREY, 14, I, 12) + rect(2650, 890, 30, 260, GREY, 8, I, 10) + rect(3080, 890, 30, 260, GREY, 8, I, 10)
add("chol-A", "cholesterol", "No symptoms. One test.", "No symptoms. One blood test. Get your cholesterol checked.",
    "Two-beat typographic contrast; the problem and the fix in one glance", "Get a cholesterol test",
    "No symptoms. One blood test. Get your cholesterol checked.", True,
    rect(0, 0, 4800, 1400, A) + t(160, 600, "No symptoms.", 320, G, 800, W) + t(160, 1000, "One blood test.", 320, G, 800, Y)
    + rough(tube(2680, R, 560) + tube(2830, Y, 640) + tube(2980, GN, None) + rack)
    + rough(rect(3230, 300, 14, 800, R)) + t(3320, 560, "Get your", 160, O, 900, W) + t(3320, 770, "cholesterol", 160, O, 900, W)
    + t(3320, 980, "checked.", 160, O, 900, W) + grain() + signoff(GREY))

cx, cy = 720, 700
dial_ticks = "".join(line([(cx + 330 * math.cos(math.radians(a)), cy + 330 * math.sin(math.radians(a))),
                           (cx + (300 if a % 40 else 270) * math.cos(math.radians(a)), cy + (300 if a % 40 else 270) * math.sin(math.radians(a)))], 12 if a % 40 else 18, W)
                     for a in range(140, 401, 20))
heart_icon = "M720 1000 C 640 940 600 900 600 850 C 600 815 625 795 655 795 C 685 795 705 815 720 840 C 735 815 755 795 785 795 C 815 795 840 815 840 850 C 840 900 800 940 720 1000 Z"
cluster = (circle(cx, cy, 430, MID) + circle(cx, cy, 400, A2, "#5a656c", 10) + dial_ticks
           + line([(cx, cy), (cx + 280 * math.cos(math.radians(250)), cy + 280 * math.sin(math.radians(250)))], 18, R)
           + circle(cx, cy, 40, MID) + path(heart_icon, stroke="#5a656c", sw=16)
           + t(cx, 620, "mph", 52, O, 700, "#5a656c", "middle"))
add("chol-B", "cholesterol", "No warning light", "Your heart has no warning light. Get a cholesterol test.",
    "Dashboard metaphor for drivers; an unlit warning light shows 'no symptoms' without saying it", "Get a cholesterol test",
    "Your heart has no warning light. Get a cholesterol test.", True,
    rect(0, 0, 4800, 1400, I) + rough(cluster) + t(1450, 520, "Your heart has", 290, G, 800, W) + t(1450, 820, "no warning light.", 290, G, 800, W)
    + t(1450, 1090, "Get a cholesterol test.", 160, O, 900, Y) + grain() + signoff(GREY))

days = "".join(rect(3510 + c * 190, 560 + r * 140, 150, 100, "none", 10, "#d9c4bf", 6) for r in range(4) for c in range(5))
xs = "".join(line([(3530 + c * 190, 580 + r * 140), (3640 + c * 190, 640 + r * 140)], 10, GREY) + line([(3640 + c * 190, 580 + r * 140), (3530 + c * 190, 640 + r * 140)], 10, GREY)
             for r, c in [(0, 0), (0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (3, 4)])
calendar = (rect(3470, 300, 1000, 860, P, 40, I, 18) + rect(3470, 300, 1000, 200, R, 40) + rect(3470, 440, 1000, 60, R)
            + rect(3690, 240, 44, 140, I, 22) + rect(4210, 240, 44, 140, I, 22) + days + xs
            + circle(3970, 800, 190, Y, I, 14) + t(3970, 900, "?", 300, G, 800, I, "middle"))
pencil = (f'<g transform="translate(-40 -230) rotate(32 4420 1000)">' + rect(4380, 700, 90, 520, Y, 6, I, 10) + rect(4380, 640, 90, 80, "#f3b6ac", 10, I, 10)
          + path("M4380 1220 L4425 1330 L4470 1220 Z", fill=P, stroke=I, sw=10) + path("M4410 1290 L4425 1330 L4440 1290 Z", fill=I) + "</g>")
add("chol-C", "cholesterol", "When was your last test?", "When was your last cholesterol test? Can't remember? Book one.",
    "Personal question hook; makes the reader do the maths and realise it's been years", "Book a cholesterol test",
    "When was your last cholesterol test? Can't remember? Book one.", False,
    ecg_grid() + t(160, 520, "When was your last", 290) + t(160, 860, "cholesterol test?", 290)
    + t(160, 1150, "Can’t remember? Book one.", 170, O, 900, R) + rough(shift(rect(3470, 300, 1000, 860, R, 40), 16, 12) + calendar + pencil)
    + grain() + signoff(I))

# ================================================================== CPR
def rescue(ink, skin):
    return (line([(3700, 1150), (4700, 1150)], 14, ink)
            + limb([(4330, 1135), (4560, 1140)], 52, skin, ink, 10) + limb([(4330, 1135), (4390, 900)], 58, skin, ink, 10)
            + path("M4430 905 L4335 905 L4205 650 L4295 610 Z", fill=Y, stroke=ink, sw=12)
            + limb([(4255, 650), (4135, 1000)], 44, skin, ink, 10) + limb([(4285, 640), (4165, 1000)], 44, skin, ink, 10)
            + circle(4200, 565, 62, skin, ink, 12)
            + circle(3810, 1068, 56, skin, ink, 12)
            + rect(3870, 1020, 830, 100, skin, 46, ink, 12)
            + path("M4100 1010 C 4100 985 4200 985 4200 1010 C 4200 1035 4100 1035 4100 1010 Z", fill=skin, stroke=ink, sw=10)
            + "".join(line([(4010, y), (4050, y + 40), (4090, y)], 20, Y) for y in (690, 790, 890)))


hands = rescue(I, P)
add("cpr-A", "heart-attack-cpr", "Push hard. Push fast.", "Push hard. Push fast. 100–120 a minute. Call 911 first.",
    "BHF 'Hard and Fast': the instruction itself is the headline", "Do hands-only CPR",
    "Push hard. Push fast. 100-120 a minute. Call 911 first.", True,
    rect(0, 0, 4800, 1400, R) + t(160, 620, "Push hard.", 400, G, 800, W) + t(160, 1080, "Push fast.", 400, G, 800, W)
    + t(2450, 640, "100–120 a minute", 130, O, 900, Y) + t(2450, 860, "Call 911 first.", 130, O, 900, W)
    + '<g transform="translate(4200 1150) scale(1.18) translate(-4200 -1150)">' + rough(shift(rescue(DR, DR), 12, 9) + hands) + "</g>" + grain() + signoff(W))

grooves = "".join(circle(560, 700, r, "none", "#333c42", 6) for r in range(200, 400, 34))
record = (circle(560, 700, 400, I) + grooves + circle(560, 700, 165, R) + circle(560, 700, 18, I)
          + t(560, 670, "100–120", 66, O, 900, W, "middle") + t(560, 770, "beats a minute", 38, O, 700, W, "middle"))


def disco(ink, shirt, skin):
    return (path("M1150 900 L1100 1150 L1040 1160 L1060 1150 Z", fill=skin, stroke=ink, sw=10)
            + limb([(1200, 700), (1150, 900), (1095, 1140)], 50, skin, ink, 10) + limb([(1255, 700), (1320, 900), (1380, 1130)], 50, skin, ink, 10)
            + path("M1060 1100 L1150 1100 L1170 1170 L1040 1170 Z", fill=skin, stroke=ink, sw=10)
            + path("M1340 1090 L1420 1090 L1450 1160 L1320 1160 Z", fill=skin, stroke=ink, sw=10)
            + limb([(1175, 430), (1090, 560), (1170, 650)], 38, skin, ink, 10)
            + path("M1165 410 L1295 410 L1270 710 L1180 710 Z", fill=shirt, stroke=ink, sw=12)
            + limb([(1285, 430), (1350, 330), (1430, 195)], 38, skin, ink, 10)
            + limb([(1230, 370), (1230, 410)], 32, skin, ink, 10) + circle(1232, 322, 60, skin, ink, 12)
            + path("M1180 300 C 1180 240 1290 230 1295 300 C 1270 270 1200 270 1180 300 Z", fill=ink))


notes = (path("M1520 330 L1520 210 L1600 190 L1600 300", stroke=Y, sw=14) + circle(1500, 335, 26, Y) + circle(1580, 305, 26, Y)
         + path("M1470 480 L1470 400", stroke=Y, sw=12) + circle(1452, 485, 22, Y))
add("cpr-B", "heart-attack-cpr", "Know Stayin' Alive? You know CPR.", "Know “Stayin’ Alive”? You know CPR. Call 911. Push to the beat.",
    "AHA Hands-Only CPR 'Stayin' Alive' campaign: a song people already know sets the tempo", "Call 911 and do hands-only CPR",
    "Know Stayin' Alive? You know CPR.", True,
    rect(0, 0, 4800, 1400, A) + rough(record) + rough(shift(disco(R, R, R), 10, 8) + disco(I, R, P)) + rough(notes)
    + t(1700, 520, "Know “Stayin’ Alive”?", 250, G, 800, W) + t(1700, 830, "You know CPR.", 290, G, 800, Y, italic=True)
    + t(1700, 1050, "Call 911. Push hard and fast to the beat.", 115, O, 800, W) + grain() + signoff(GREY))


def hand(cx, base, mirror):
    m = -1 if mirror else 1
    fingers = [(-105, 250), (-35, 285), (35, 275), (105, 225)]
    out = ""
    for dx, h in fingers:
        out += rect(cx + dx * m - 32, base - 300 - h, 64, h + 60, P, 32, I, 12)
    out += path(f"M{cx - 150} {base} L{cx - 150} {base - 300} C{cx - 150} {base - 340} {cx + 150} {base - 340} {cx + 150} {base - 300} L{cx + 150} {base} Z", fill=P, stroke=I, sw=12)
    tx = cx - 150 * m
    out += f'<rect x="{tx - 32}" y="{base - 330}" width="64" height="230" rx="32" fill="{P}" stroke="{I}" stroke-width="12" transform="rotate({-35 * m} {tx} {base - 120})"/>'
    out += line([(cx - 60, base - 150), (cx + 40, base - 180)], 8, GREY)
    return out


stamp = (f'<g transform="rotate(-9 760 420)">' + circle(760, 420, 200, R) + circle(760, 420, 170, "none", W, 10)
         + t(760, 500, "2×", 230, G, 800, W, "middle") + "</g>")
add("cpr-C", "heart-attack-cpr", "Your hands can double their chances", "Your hands can double their chances. Call 911. Push hard and fast.",
    "One big number + 'you' framing (outdoor that makes the reader the hero)", "Call 911 and do hands-only CPR",
    "Your hands can double their chances.", False,
    ecg_grid() + rough(hand(520, 1420, False) + hand(1000, 1420, True)) + rough(stamp)
    + t(1600, 520, "Your hands can", 260) + t(1600, 820, "double their chances.", 260)
    + t(1600, 1070, "Call 911. Push hard and fast.", 150, O, 900, R)
    + t(1600, 1190, "CPR right away can double or triple survival. Source: American Heart Association", 56, O, 600, "#4d4245")
    + grain() + signoff(I))

# ================================================================== STROKE / AFIB
def icon_b(cx, c):
    return (circle(cx + 50, 380, 34, c) + line([(cx + 35, 415), (cx - 10, 530)], 28, c) + line([(cx - 120, 425), (cx + 160, 480)], 20, c)
            + line([(cx - 10, 530), (cx - 40, 630)], 22, c) + line([(cx - 10, 530), (cx + 70, 590)], 22, c)
            + path(f"M{cx - 140} 650 Q{cx} 600 {cx + 140} 650", stroke=c, sw=10))


def icon_e(cx, c):
    eye = f"M{cx - 150} 480 Q{cx} 350 {cx + 150} 480 Q{cx} 610 {cx - 150} 480 Z"
    return (f'<clipPath id="eyeclip"><path d="{eye}"/></clipPath>' + path(eye, fill=P, stroke=c, sw=16) + circle(cx, 480, 58, c)
            + f'<g clip-path="url(#eyeclip)">{rect(cx + 10, 340, 160, 280, "url(#dotI)")}</g>' + path(eye, stroke=c, sw=16))


def icon_f(cx, c):
    return (circle(cx, 485, 140, P, c, 16) + circle(cx - 50, 450, 15, c) + path(f"M{cx + 25} 455 L{cx + 80} 465", stroke=c, sw=12)
            + path(f"M{cx - 75} 535 Q{cx - 10} 560 {cx + 75} 585", stroke=c, sw=14))


def icon_a(cx, c):
    return (circle(cx, 365, 34, c) + line([(cx, 400), (cx, 560)], 26, c) + line([(cx, 425), (cx - 120, 335)], 20, c)
            + line([(cx, 425), (cx + 100, 520)], 20, c) + line([(cx, 560), (cx - 50, 640)], 20, c) + line([(cx, 560), (cx + 50, 640)], 20, c)
            + line([(cx + 150, 470), (cx + 150, 600)], 12, R) + path(f"M{cx + 115} 565 L{cx + 150} 610 L{cx + 185} 565", stroke=R, sw=12))


def icon_s(cx, c):
    return (path(f"M{cx - 150} 370 L{cx + 150} 370 Q{cx + 170} 370 {cx + 170} 395 L{cx + 170} 530 Q{cx + 170} 555 {cx + 150} 555 L{cx - 40} 555 L{cx - 100} 620 L{cx - 95} 555 L{cx - 150} 555 Q{cx - 170} 555 {cx - 170} 530 L{cx - 170} 395 Q{cx - 170} 370 {cx - 150} 370 Z",
                 fill=P, stroke=c, sw=14)
            + path(f"M{cx - 110} 470 q20 -50 40 0 q20 50 40 0 q15 -60 45 -5 q25 45 40 -10 q15 -40 35 10", stroke=c, sw=12))


def icon_t(cx, c):
    return (circle(cx, 480, 140, "none", c, 16) + line([(cx, 480), (cx, 385)], 16, c) + line([(cx, 480), (cx + 70, 520)], 16, c)
            + "".join(circle(cx + 115 * math.cos(math.radians(a)), 480 + 115 * math.sin(math.radians(a)), 9, c) for a in range(0, 360, 90)))


letters = [("B", "Balance", icon_b), ("E", "Eyes", icon_e), ("F", "Face", icon_f), ("A", "Arms", icon_a), ("S", "Speech", icon_s)]
cols = ""
for i, (L, lab, fn) in enumerate(letters):
    x = 468 + i * 696
    cols += rough(fn(x, I)) + t(x, 960, L, 420, O, 900, R, "middle") + t(x, 1075, lab, 100, O, 800, I, "middle")
add("stroke-A", "afib-stroke", "BE FAST, big", "Spot a stroke: BE FAST. Balance, Eyes, Face, Arms, Speech, Time: call 911.",
    "NHS Act FAST / ASA BE FAST: one memorable acronym that ends in the action", "Call 911 at any stroke sign",
    "Spot a stroke: BE FAST. Time to call 911.", False,
    rect(0, 0, 4800, 1400, P) + t(160, 220, "Spot a stroke:", 130, G, 700, I, italic=True) + cols
    + rough(rect(3600, -40, 1300, 1480, R), "roughBig") + rough(icon_t(4200, W))
    + t(4200, 960, "T", 420, O, 900, W, "middle") + t(4200, 1075, "Time: call 911", 100, O, 800, W, "middle") + grain() + signoff(W))

droop, x = "", 950
for i, ch in enumerate("drooping?"):
    dy, rot = int(6 * i * i), min(i * 3, 18)
    droop += f'<text x="{x}" y="{560 + dy}" font-family="{G}" font-weight="800" font-size="330" fill="{W}" transform="rotate({rot} {x} {560 + dy})">{ch}</text>'
    x += {"d": 170, "r": 126, "o": 165, "p": 170, "i": 92, "n": 175, "g": 160, "?": 145}[ch]
fx, fy = 3560, 600
face = (f'<clipPath id="faceclip"><ellipse cx="{fx}" cy="{fy}" rx="320" ry="410"/></clipPath>'
        + f'<g clip-path="url(#faceclip)">{rect(fx + 10, fy - 420, 340, 840, "url(#dotR)", extra=chr(32) + "opacity=" + chr(34) + "0.75" + chr(34))}</g>'
        + f'<ellipse cx="{fx}" cy="{fy}" rx="320" ry="410" fill="none" stroke="{W}" stroke-width="22"/>'
        + path(f"M{fx - 322} {fy - 60} C{fx - 330} {fy - 470} {fx + 330} {fy - 470} {fx + 322} {fy - 60} C{fx + 250} {fy - 250} {fx - 250} {fy - 250} {fx - 322} {fy - 60} Z", fill=W)
        + path(f"M{fx - 210} {fy - 90} L{fx - 70} {fy - 110}", stroke=W, sw=18) + path(f"M{fx + 60} {fy - 95} L{fx + 200} {fy - 55}", stroke=W, sw=18)
        + path(f"M{fx - 200} {fy - 20} Q{fx - 130} {fy - 70} {fx - 60} {fy - 20} Q{fx - 130} {fy + 20} {fx - 200} {fy - 20} Z", fill=W)
        + path(f"M{fx + 60} {fy + 5} Q{fx + 130} {fy - 15} {fx + 200} {fy + 20}", stroke=W, sw=16)
        + path(f"M{fx} {fy - 10} L{fx - 30} {fy + 120} L{fx + 30} {fy + 130}", stroke=W, sw=14)
        + path(f"M{fx - 150} {fy + 230} Q{fx - 20} {fy + 260} {fx + 60} {fy + 255} Q{fx + 140} {fy + 262} {fx + 170} {fy + 330}", stroke=W, sw=18)
        + line([(fx - 140, fy + 400), (fx - 150, 1180)], 20, W) + line([(fx + 140, fy + 400), (fx + 150, 1180)], 20, W))
add("stroke-B", "afib-stroke", "Drooping letters", "Face drooping? Call 911. Every minute counts.",
    "Act FAST: show the symptom, demand the action; the type itself droops", "Call 911 for stroke signs",
    "Face drooping? Call 911. Every minute counts.", True,
    rect(0, 0, 4800, 1400, A) + t(160, 560, "Face", 330, G, 800, W) + droop + rough(face)
    + t(160, 1150, "Call 911.", 240, O, 900, Y) + t(1640, 1150, "Every minute counts.", 130, O, 700, W) + grain() + signoff(GREY))

rnd = random.Random(7)
d, x = "M120 1110", 120
while x < 2950:
    x += rnd.randint(90, 260)
    d += f" L{x} {1110 + rnd.randint(-12, 12)} l14 -{rnd.randint(120, 200)} l16 {rnd.randint(170, 250)} l12 -{rnd.randint(30, 60)}"
    x += 42
d += " L3080 1110"
hx = 4390
heart = (path(f"M{hx - 140} 440 C{hx - 270} 440 {hx - 310} 580 {hx - 270} 720 C{hx - 220} 900 {hx - 60} 1020 {hx + 30} 1080 C{hx + 90} 1010 {hx + 250} 880 {hx + 270} 700 C{hx + 290} 540 {hx + 210} 440 {hx + 110} 450 C{hx + 60} 455 {hx + 30} 490 {hx + 10} 520 C{hx - 20} 470 {hx - 70} 440 {hx - 140} 440 Z",
              fill=R, stroke=I, sw=16)
         + path(f"M{hx - 140} 440 C{hx - 270} 440 {hx - 310} 580 {hx - 270} 720 C{hx - 230} 860 {hx - 150} 950 {hx - 80} 1010 C{hx - 150} 860 {hx - 200} 700 {hx - 140} 440 Z", fill="url(#dotD)")
         + path(f"M{hx + 10} 520 C{hx + 10} 400 {hx + 10} 330 {hx + 90} 300 C{hx + 170} 270 {hx + 220} 320 {hx + 215} 400", stroke=I, sw=86)
         + path(f"M{hx + 10} 520 C{hx + 10} 400 {hx + 10} 330 {hx + 90} 300 C{hx + 170} 270 {hx + 220} 320 {hx + 215} 400", stroke=R, sw=58)
         + line([(hx - 110, 445), (hx - 140, 330)], 60, I) + line([(hx - 110, 445), (hx - 140, 335)], 34, R)
         + path(f"M{hx - 120} 600 C{hx - 20} 700 {hx + 20} 820 {hx + 30} 1000", stroke=I, sw=12)
         + path(f"M{hx + 150} 560 C{hx + 100} 640 {hx + 80} 700 {hx + 40} 760", stroke=I, sw=10)
         + "".join(path(f"M{hx + sx} {sy} q20 -30 40 0 q20 30 40 0", stroke=I, sw=12) for sx, sy in [(-430, 520), (-450, 820), (300, 500), (320, 860)]))
add("stroke-C", "afib-stroke", "Fluttering heartbeat", "Fluttering heartbeat? AFib can lead to stroke. See a doctor.",
    "ECG-paper vernacular + symptom hook; the irregular trace shows AFib without jargon", "See a doctor about an irregular heartbeat",
    "Fluttering heartbeat? AFib can lead to stroke. See a doctor.", False,
    ecg_grid() + t(160, 500, "Fluttering heartbeat?", 330) + t(160, 780, "AFib can lead to stroke.", 170, O, 800, I)
    + t(2700, 780, "See a doctor.", 170, O, 900, R)
    + rough(f'<path d="{d}" fill="none" stroke="{R}" stroke-width="16" stroke-linejoin="round" stroke-linecap="round"/>')
    + rough(shift(heart.replace(R, DR), 14, 10) + heart) + grain() + signoff(I))

os.makedirs(OUT, exist_ok=True)
for k, v in boards.items():
    open(os.path.join(OUT, k + ".svg"), "w").write(v)
json.dump(meta, open(os.path.join(OUT, "options.json"), "w"), indent=1, ensure_ascii=False)
print(len(boards), "boards written")
