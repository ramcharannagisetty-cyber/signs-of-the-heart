"""Billboards v3: redraw 7 boards in a cleaner, modern flat-illustration style with realistic proportions.
Runs v2 first (all 18 boards), then overwrites hf-B, hf-C, fmd-B, bp-B, cpr-A, cpr-C, stroke-B.
usage: python3 -I make_boards_v3.py <out_dir>
"""
import json, os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ns = runpy.run_path(os.path.join(HERE, "make_boards_v2.py"))
OUT = sys.argv[1]
t, line, path, circle, rect = ns["t"], ns["line"], ns["path"], ns["circle"], ns["rect"]
grain, signoff, svg, ecg_grid = ns["grain"], ns["signoff"], ns["svg"], ns["ecg_grid"]
G, O = ns["G"], ns["O"]
R, DR, Y, A, P, E, I, W, GREY, MID = (ns[k] for k in ("R", "DR", "Y", "A", "P", "E", "I", "W", "GREY", "MID"))

# skin, hair and clothing tones for flat illustration
S1, S1d = "#f0c3a0", "#d9a37f"
S2, S2d = "#c68a5e", "#a96f47"
S3, S3d = "#8d5a3b", "#6f432a"
H1, H2 = "#241813", "#5b3a25"
TEAL, BLUE, NAVY, WOOD = "#2f6f73", "#35608c", "#22344a", "#6b4f3a"
SHADOW = 'fill="#000" opacity="0.13"'

boards, meta = {}, {}


def put(id_, concept, words, inspired, action, title, dark, body):
    boards[id_] = svg(title, dark, body)
    meta[id_] = dict(concept=concept, headline=words, inspired_by=inspired, action=action)


# ------------------------------------------------------------------ hf-B: a real swollen ankle
leg = ("M3840 -40 C 3830 300 3845 520 3832 640 C 3780 700 3752 800 3770 870 C 3778 920 3794 950 3806 966 "
       "C 3700 1010 3560 1060 3485 1100 C 3430 1125 3420 1185 3475 1188 L 4200 1188 "
       "C 4290 1188 4305 1100 4282 1046 C 4322 990 4338 900 4320 838 C 4302 760 4262 690 4252 620 "
       "C 4246 450 4232 200 4242 -40 Z")
SOCK, SOCKD = "#8fa6bd", "#7890a8"
ribs = "".join(line([(x, 1000), (x, 1050)], 9, SOCKD) for x in range(3740, 4340, 30))
ankle = (f'<clipPath id="legc"><path d="{leg}"/></clipPath>'
         + path(leg, fill=S1)
         + f'<g clip-path="url(#legc)">'
         + rect(4170, -60, 200, 1000, S1d, extra='opacity="0.7"')
         + path("M3770 860 C 3900 900 4150 900 4330 860 L 4330 995 L 3770 995 Z", fill=S1d, extra='opacity="0.55"')
         + rect(3400, 995, 1000, 260, SOCK) + ribs + rect(3400, 1130, 1000, 80, SOCKD)
         + "</g>"
         + line([(3780, 995), (4330, 995)], 10, SOCKD)
         + path("M3832 640 C 3852 760 3860 880 3828 975", stroke=R, sw=11, extra='stroke-dasharray="26 18"')
         + path("M4252 640 C 4232 760 4230 880 4266 1030", stroke=R, sw=11, extra='stroke-dasharray="26 18"')
         + t(4400, 770, "normal", 60, O, 800, R) + t(4400, 832, "ankle", 60, O, 800, R)
         + path("M4392 790 C 4330 800 4290 805 4250 812", stroke=R, sw=8))
sizes = [300, 360, 420, 480, 540, 600, 680]
sw = "".join(f'<tspan font-size="{s}">{ch}</tspan>' for ch, s in zip("ankles?", sizes))
put("hf-B", "Real swollen ankle with the normal outline", "Swollen ankles? Ask about heart failure.",
    "Visual pun outdoor + a literal, recognisable sign (sock marks, puffy ankle)", "Ask a doctor about swelling",
    "Swollen ankles? Ask about heart failure.", False,
    rect(0, 0, 4800, 1400, P) + circle(3950, 680, 600, E) + f'<ellipse cx="3860" cy="1196" rx="520" ry="24" {SHADOW}/>' + ankle
    + t(160, 820, "Swollen", 300, G, 800, R) + f'<text x="1250" y="820" font-family="{G}" font-weight="800" fill="{R}">{sw}</text>'
    + t(160, 1120, "Ask about heart failure.", 170, O, 800, I) + grain() + signoff(I))


# ------------------------------------------------------------------ hf-C: sitting up in bed to breathe
def pillow(x, y, w, h):
    d = (f"M{x + 40} {y} C{x + w * 0.35} {y - 22} {x + w * 0.65} {y - 22} {x + w - 40} {y} "
         f"C{x + w + 15} {y + h * 0.5} {x + w + 15} {y + h * 0.5} {x + w - 40} {y + h} "
         f"C{x + w * 0.65} {y + h + 22} {x + w * 0.35} {y + h + 22} {x + 40} {y + h} "
         f"C{x - 15} {y + h * 0.5} {x - 15} {y + h * 0.5} {x + 40} {y} Z")
    return path(d, fill=P) + path(f"M{x + 30} {y + h - 8} C{x + w * 0.4} {y + h + 12} {x + w * 0.7} {y + h + 10} {x + w - 30} {y + h - 8}", stroke="#d8cdc9", sw=14)


win = (rect(1080, 170, 360, 360, "#3a454c", 18) + rect(1100, 190, 320, 320, "#141c24", 8)
       + path("M1300 250 a70 70 0 1 0 70 95 a55 55 0 1 1 -70 -95 Z", fill=Y)
       + "".join(circle(x, y, 7, Y) for x, y in [(1150, 260), (1210, 420), (1390, 440), (1160, 470)])
       + rect(1255, 190, 14, 320, "#3a454c") + rect(1100, 345, 320, 14, "#3a454c"))
person = (path("M600 660 C 640 640 710 640 742 656 L 882 906 L 690 926 Z", fill=TEAL)
          + path("M655 598 L 700 598 L 706 662 L 650 662 Z", fill=S2d)
          + path("M640 470 C 660 445 720 440 760 470 C 780 490 790 515 788 535 L 806 576 L 790 586 C 796 596 792 606 785 611 "
                 "C 786 626 770 636 750 638 C 720 641 690 631 670 616 C 630 601 615 561 620 521 C 622 496 630 481 640 470 Z", fill=S2)
          + path("M636 468 C 662 432 742 430 772 466 C 742 456 702 462 690 484 C 680 522 650 542 624 562 C 612 522 615 490 636 468 Z", fill=H1)
          + f'<ellipse cx="680" cy="548" rx="14" ry="22" fill="{S2d}"/>' + line([(740, 520), (760, 522)], 7, H1)
          + f'<ellipse cx="786" cy="600" rx="7" ry="9" fill="{H1}"/>'
          + line([(705, 672), (792, 792)], 62, TEAL) + line([(792, 792), (740, 722)], 48, S2) + circle(732, 716, 32, S2)
          + "".join(path(f"M{820 + k * 34} {585 - k * 8} q 30 -14 60 0", stroke=W, sw=9, extra=f'opacity="{0.8 - k * 0.2}"') for k in range(3)))
blanket = (path("M680 926 C 760 820 900 782 1050 800 C 1250 830 1400 880 1522 922 L 1522 962 L 680 962 Z", fill=R)
           + path("M900 830 C 980 860 1040 900 1080 950 M1200 840 C 1250 870 1290 900 1320 940", stroke=DR, sw=10))
bed = (rect(190, 430, 90, 730, WOOD, 30) + rect(1476, 760, 64, 400, WOOD, 26)
       + rect(190, 930, 1350, 120, P, 24) + rect(190, 1040, 1350, 50, WOOD) + rect(230, 1090, 40, 70, WOOD) + rect(1460, 1090, 40, 70, WOOD)
       + pillow(290, 830, 470, 95) + pillow(300, 735, 450, 95) + pillow(310, 642, 430, 92))
put("hf-C", "Propped up in bed to breathe", "Need extra pillows to breathe? Tell your doctor.",
    "Conversational hook naming one specific, everyday sign (BHF heart attack symptom ads)", "Tell a doctor",
    "Need extra pillows to breathe? Tell your doctor.", True,
    rect(0, 0, 4800, 1400, A) + win + bed + person + blanket
    + t(1760, 560, "Need extra pillows", 260, G, 800, W) + t(1760, 840, "to breathe?", 260, G, 800, W)
    + t(1760, 1110, "Tell your doctor.", 170, O, 800, Y) + grain() + signoff(GREY))

# ------------------------------------------------------------------ fmd-B: hearing your own pulse
# realistic right-facing profile: eye at half head height, ear between brow and nose base,
# brow / nose base / chin in equal thirds, jaw shadow and neck
profile = ("M560 1450 L545 1180 C 535 1000 520 900 500 860 C 400 820 330 720 310 600 C 290 460 340 320 450 250 "
           "C 540 195 660 185 760 195 C 880 210 960 270 990 360 C 1005 410 1012 470 1015 525 "
           "C 1018 548 1005 565 996 578 C 1020 620 1060 670 1086 712 C 1094 728 1080 742 1060 744 "
           "C 1048 746 1036 748 1028 754 C 1030 775 1037 792 1039 805 C 1035 815 1023 821 1021 826 "
           "C 1031 835 1037 846 1033 856 C 1025 866 1013 870 1009 876 C 1016 892 1028 906 1026 924 "
           "C 1022 944 1000 956 972 958 C 935 964 880 978 845 993 C 842 1060 852 1150 870 1250 L 900 1450 Z")
hair = ("M992 360 C 975 280 890 205 770 188 C 640 172 500 200 410 270 C 320 340 285 470 300 610 "
        "C 312 720 380 820 500 868 L 560 880 C 600 820 640 760 668 690 C 672 640 700 600 760 580 "
        "C 790 570 800 540 820 500 C 850 460 890 430 930 420 C 960 412 985 390 992 360 Z")
skin_grad = ('<defs><linearGradient id="skinG" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{S1d}"/><stop offset="0.6" stop-color="{S1}"/><stop offset="1" stop-color="#f6d0b2"/></linearGradient></defs>')
rings = "".join(circle(735, 670, r, "none", R, 18, f'opacity="{o}"') for r, o in [(220, 0.95), (310, 0.65), (400, 0.38)])
bars = "".join(rect(70 + i * 30, 670 - h / 2, 18, h, R, 9) for i, h in enumerate([50, 110, 240, 120, 70, 40]))
head = (skin_grad + rings + bars
        + path(profile, fill="url(#skinG)")
        + path("M972 958 C 900 940 820 885 775 832 C 782 885 805 945 845 995 C 900 980 940 968 972 958 Z", fill=S1d, extra='opacity="0.5"')
        + path("M775 832 C 832 892 902 940 972 958", stroke="#c48a66", sw=6, extra='opacity="0.55"')
        + f'<ellipse cx="925" cy="705" rx="55" ry="32" fill="#e59a80" opacity="0.45"/>'
        + circle(335, 330, 108, H2) + path("M395 395 C 420 370 430 330 420 300", stroke=H1, sw=12)
        + path(hair, fill=H2)
        + path("M940 300 C 880 240 780 215 680 220", stroke="#7a5236", sw=24, extra='opacity="0.55"')
        + "".join(path(d_, stroke=H1, sw=7, extra='opacity="0.5"') for d_ in [
            "M960 330 C 900 260 800 225 690 230", "M930 400 C 860 330 760 300 640 320", "M620 260 C 520 300 430 400 400 520"])
        + path("M770 595 C 740 560 680 565 672 625 C 666 670 690 700 700 735 C 705 760 715 785 745 782 C 765 780 772 760 770 745 Z", fill=S1d)
        + path("M748 615 C 718 610 702 640 714 680 C 722 705 736 716 742 732", stroke="#b97c58", sw=10)
        + f'<ellipse cx="755" cy="690" rx="12" ry="20" fill="#b97c58"/>'
        + path("M920 568 Q 958 548 998 570 L 982 581 Q 950 587 920 568 Z", fill=W) + f'<ellipse cx="982" cy="570" rx="12" ry="13" fill="{H1}"/>'
        + path("M914 565 Q 958 542 1001 567", stroke=H1, sw=10) + path("M1001 567 l 14 -8 M 990 558 l 10 -12", stroke=H1, sw=5)
        + path("M925 590 Q 955 598 985 588", stroke="#c48a66", sw=5, extra='opacity="0.6"')
        + path("M918 530 Q 958 510 1002 527", stroke=H2, sw=14)
        + path("M1040 738 q 12 -7 19 4", stroke="#b97c58", sw=6)
        + path("M1019 801 C 1040 797 1047 812 1034 826 C 1047 836 1043 854 1019 860 C 1009 848 1009 832 1017 826 C 1009 818 1011 807 1019 801 Z", fill="#c9705f")
        + path("M1017 826 L 1035 826", stroke="#9e4f42", sw=4)
        + path("M420 1450 C 470 1250 560 1190 700 1185 C 820 1182 900 1220 950 1290 L 990 1450 Z", fill=TEAL)
        + path("M700 1185 C 760 1240 820 1250 900 1235", stroke="#245a5d", sw=10))
put("fmd-B", "Hearing your own pulse", "Heartbeat in your ear? Tell a doctor.",
    "One strong visual + short line; turns an odd symptom (pulsatile tinnitus) into something people recognise", "Tell a doctor about a whooshing ear",
    "Heartbeat in your ear? Tell a doctor.", False,
    rect(0, 0, 4800, 1400, P) + head
    + t(1400, 620, "Heartbeat in your ear?", 280) + t(1400, 960, "Tell a doctor.", 180, O, 800, R)
    + t(1400, 1080, "A whooshing sound in time with your pulse can be one sign of FMD.", 70, O, 600, "#4d4245")
    + grain() + signoff(I))

# ------------------------------------------------------------------ bp-B: the monitor says what you can't feel
device = (rect(3950, 280, 540, 600, "#000", 60, extra='opacity="0.12"') + rect(3930, 260, 540, 600, W, 60, "#d9cfcb", 8)
          + rect(3990, 320, 420, 330, "#cfdccf", 24)
          + t(4010, 380, "SYS", 44, O, 700, "#3a4a3a") + t(4390, 480, "158", 170, O, 900, I, "end")
          + t(4010, 545, "DIA", 44, O, 700, "#3a4a3a") + t(4390, 625, "96", 120, O, 900, I, "end")
          + rect(4010, 565, 150, 56, R, 12) + t(4085, 607, "HIGH", 38, O, 900, W, "middle")
          + t(4390, 690, "mmHg", 34, O, 700, "#3a4a3a", "end")
          + circle(4200, 760, 56, BLUE) + f'<ellipse cx="4060" cy="760" rx="44" ry="26" fill="#d9cfcb"/>' + f'<ellipse cx="4340" cy="760" rx="44" ry="26" fill="#d9cfcb"/>')
armB = (rect(3760, 1110, 1100, 42, "#d9cfcb") + rect(3760, 1152, 1100, 16, "#c3b6b1") + f'<ellipse cx="4300" cy="1180" rx="600" ry="18" {SHADOW}/>'
        + path("M4850 980 L 4100 1000 C 4040 1002 3990 1020 3975 1060 C 3965 1095 3990 1110 4040 1110 L 4850 1110 Z", fill=S2)
        + path("M3990 1015 C 3930 1010 3880 1030 3870 1070 C 3862 1100 3880 1112 3930 1112 L 4040 1112 Z", fill=S2)
        + "".join(line([(3890 + k * 26, 1080), (3905 + k * 26, 1108)], 6, S2d) for k in range(4))
        + path("M4850 1000 L 4300 1012 L 4300 1030 L 4850 1020 Z", fill=S2d, extra='opacity="0.5"')
        + rect(4450, 952, 270, 186, NAVY, 30) + rect(4470, 968, 230, 26, "#33496a", 10)
        + path("M4520 952 C 4500 880 4300 900 4200 862", stroke="#1c1517", sw=14))
dots = "".join(circle(x, 770, 12, GREY) for x in range(1720, 2980, 70))
put("bp-B", "The monitor shows what you can't feel", "High blood pressure feels like nothing. Get it checked.",
    "Silent-killer outdoor: the person feels fine; the numbers tell the truth", "Get your blood pressure checked",
    "High blood pressure feels like nothing. Get it checked.", False,
    rect(0, 0, 4800, 1400, P) + t(160, 470, "High blood pressure", 300) + t(160, 800, "feels like", 300)
    + dots + t(3040, 800, "nothing.", 170, G, 700, R, italic=True) + t(160, 1150, "Get it checked.", 170, O, 900, R)
    + armB + device + grain() + signoff(I))

# ------------------------------------------------------------------ cpr-A: a real CPR scene
cx = 3990
rescuer_back = (path(f"M{cx - 125} 880 L{cx + 125} 880 L{cx + 150} 1060 L{cx - 150} 1060 Z", fill="#2b343a")
                + path(f"M{cx - 165} 575 C{cx - 150} 545 {cx + 150} 545 {cx + 165} 575 L{cx + 120} 900 L{cx - 120} 900 Z", fill=Y)
                + path(f"M{cx - 30} 520 L{cx + 30} 520 L{cx + 34} 572 L{cx - 34} 572 Z", fill=S2d)
                + circle(cx, 455, 82, S2)
                + path(f"M{cx - 84} 452 C{cx - 90} 360 {cx + 90} 350 {cx + 86} 448 C{cx + 60} 405 {cx - 60} 405 {cx - 84} 452 Z", fill=H1)
                + path(f"M{cx - 42} 470 q 14 10 28 0 M{cx + 14} 470 q 14 10 28 0", stroke=H1, sw=7))
patient = (rect(4330, 1035, 600, 110, "#2b343a", 50)
           + path("M3760 1040 C 3800 980 3900 962 4000 966 L 4360 990 L 4360 1140 L 3760 1140 Z", fill=BLUE)
           + line([(3810, 1112), (4230, 1126)], 46, S1)
           + rect(3700, 1045, 90, 70, S1d, 20)
           + circle(3640, 1070, 80, S1) + path("M3640 990 C 3650 975 3672 972 3676 992 Z", fill=S1)
           + path("M3562 1068 C 3560 1010 3590 985 3620 988 C 3600 1030 3600 1100 3640 1150 C 3590 1145 3562 1110 3562 1068 Z", fill=H2))
arms = (path(f"M{cx - 160} 585 L{cx - 108} 570 L{cx - 6} 965 L{cx - 52} 975 Z", fill=S2)
        + path(f"M{cx + 160} 585 L{cx + 108} 570 L{cx + 6} 965 L{cx + 52} 975 Z", fill=S2)
        + path(f"M{cx - 168} 580 L{cx - 100} 562 L{cx - 80} 650 L{cx - 140} 668 Z", fill=Y)
        + path(f"M{cx + 168} 580 L{cx + 100} 562 L{cx + 80} 650 L{cx + 140} 668 Z", fill=Y))
handsC = (f'<ellipse cx="{cx}" cy="972" rx="82" ry="30" fill="{S2}"/>' + f'<ellipse cx="{cx}" cy="958" rx="66" ry="24" fill="{S2d}"/>'
          + "".join(line([(cx - 40 + k * 26, 948), (cx - 46 + k * 26, 972)], 6, S2) for k in range(4)))
motion = (path(f"M{cx - 140} 930 q -30 40 0 80 M{cx + 140} 930 q 30 40 0 80", stroke=W, sw=12)
          + "".join(line([(3720, y), (3770, y + 50), (3820, y)], 20, Y) for y in (620, 740, 860)))
put("cpr-A", "Push hard. Push fast. (real CPR scene)", "Push hard. Push fast. 100–120 a minute. Call 911 first.",
    "BHF 'Hard and Fast': the instruction itself is the headline, with the exact position shown", "Do hands-only CPR",
    "Push hard. Push fast. 100-120 a minute. Call 911 first.", True,
    rect(0, 0, 4800, 1400, R) + rect(3400, 1145, 1500, 300, "#a50d26")
    + rescuer_back + patient + arms + handsC + motion
    + t(160, 620, "Push hard.", 400, G, 800, W) + t(160, 1080, "Push fast.", 400, G, 800, W)
    + t(2360, 640, "100–120 a minute", 130, O, 900, Y) + t(2360, 860, "Call 911 first.", 130, O, 900, W)
    + grain() + signoff(W))

# ------------------------------------------------------------------ cpr-C: rewritten, clear comparison
hatch = '<defs><pattern id="hatchR" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="12" height="28" fill="#c8102e"/></pattern></defs>'
chart = (rect(2380, 250, 2300, 720, E, 40)
         + t(2500, 400, "No CPR until help arrives", 90, O, 700, I) + rect(2500, 430, 550, 100, GREY, 18) + t(3090, 510, "1×", 80, O, 800, "#7d7472")
         + t(2500, 690, "CPR right away", 90, O, 800, R) + rect(2500, 720, 1100, 100, R, 18) + rect(3580, 720, 570, 100, "url(#hatchR)", 18, R, 6)
         + t(4190, 815, "2–3×", 200, G, 800, R)
         + t(2500, 920, "Chance of surviving a cardiac arrest", 70, O, 600, "#4d4245"))
put("cpr-C", "Start CPR before help arrives (2–3× chart)", "Start CPR before help arrives. CPR right away: 2–3× the chance of survival. Call 911. Push hard and fast.",
    "Make the payoff concrete: one comparison anyone can read in a glance (AHA: immediate CPR can double or triple survival)", "Call 911 and start hands-only CPR",
    "Start CPR before help arrives.", False,
    hatch + rect(0, 0, 4800, 1400, P) + t(160, 420, "Start CPR before", 260) + t(160, 690, "help arrives.", 260)
    + t(160, 960, "Call 911. Push hard and fast.", 150, O, 900, R)
    + t(160, 1180, "Immediate CPR can double or triple chances of survival after cardiac arrest. Source: American Heart Association", 52, O, 600, "#4d4245")
    + chart + grain() + signoff(I))

# ------------------------------------------------------------------ stroke-B: a real face, uneven smile
fx, fy = 3300, 620
face = (f'<clipPath id="portrait"><circle cx="{fx}" cy="{fy}" r="460"/></clipPath>'
        + circle(fx, fy, 460, DR)
        + f'<g clip-path="url(#portrait)">'
        + path(f"M{fx - 90} 900 L{fx + 90} 900 L{fx + 110} 1100 L{fx - 110} 1100 Z", fill=S3d)
        + path(f"M{fx - 420} 1120 C{fx - 360} 1010 {fx - 200} 990 {fx - 100} 1000 L{fx + 100} 1000 C{fx + 200} 990 {fx + 360} 1010 {fx + 420} 1120 L{fx + 420} 1200 L{fx - 420} 1200 Z", fill=TEAL)
        + "</g>"
        + f'<ellipse cx="{fx - 282}" cy="{fy}" rx="34" ry="62" fill="{S3d}"/>' + f'<ellipse cx="{fx + 282}" cy="{fy + 20}" rx="34" ry="62" fill="{S3d}"/>'
        + path(f"M{fx} 250 C{fx + 200} 250 {fx + 290} 390 {fx + 285} 570 C{fx + 280} 730 {fx + 210} 870 {fx + 120} 940 C{fx + 60} 980 {fx - 60} 980 {fx - 120} 940 "
               f"C{fx - 210} 870 {fx - 280} 730 {fx - 285} 570 C{fx - 290} 390 {fx - 200} 250 {fx} 250 Z", fill=S3)
        + path(f"M{fx - 300} 560 C{fx - 330} 270 {fx - 150} 170 {fx} 175 C{fx + 150} 170 {fx + 330} 270 {fx + 300} 560 "
               f"C{fx + 270} 430 {fx + 160} 345 {fx + 20} 330 C{fx - 120} 320 {fx - 250} 400 {fx - 300} 560 Z", fill=H1)
        + path(f"M{fx - 200} 480 Q{fx - 125} 450 {fx - 50} 470", stroke=H1, sw=18)
        + path(f"M{fx + 50} 498 Q{fx + 125} 495 {fx + 200} 525", stroke=H1, sw=18)
        + path(f"M{fx - 180} 560 Q{fx - 120} 525 {fx - 60} 560 Q{fx - 120} 585 {fx - 180} 560 Z", fill=W) + circle(fx - 120, 558, 22, H1)
        + path(f"M{fx + 60} 585 Q{fx + 120} 565 {fx + 180} 590 Q{fx + 120} 605 {fx + 60} 585 Z", fill=W) + circle(fx + 120, 590, 16, H1)
        + path(f"M{fx + 55} 582 Q{fx + 120} 548 {fx + 185} 588 L{fx + 185} 576 Q{fx + 120} 536 {fx + 55} 570 Z", fill=S3d)
        + path(f"M{fx - 6} 560 C{fx - 10} 620 {fx - 40} 680 {fx - 55} 705 C{fx - 30} 722 {fx + 30} 722 {fx + 55} 708", stroke=S3d, sw=12)
        + path(f"M{fx - 140} 790 Q{fx - 60} 820 {fx} 818 Q{fx + 80} 822 {fx + 135} 860 Q{fx + 60} 850 {fx} 842 Q{fx - 70} 845 {fx - 140} 790 Z", fill="#5a2a1d")
        + path(f"M{fx - 132} 794 Q{fx - 60} 815 {fx} 814 L{fx} 826 Q{fx - 70} 826 {fx - 132} 794 Z", fill=W, extra='opacity="0.85"')
        + path(f"M{fx + 160} 760 C{fx + 185} 800 {fx + 190} 840 {fx + 175} 880", stroke=S3d, sw=10)
        + line([(fx, 290), (fx, 960)], 8, Y, 'stroke-dasharray="22 18"'))
droop, x = "", 950
for i, ch in enumerate("drooping?"):
    dy, rot = int(6 * i * i), min(i * 3, 18)
    droop += f'<text x="{x}" y="{560 + dy}" font-family="{G}" font-weight="800" font-size="330" fill="{W}" transform="rotate({rot} {x} {560 + dy})">{ch}</text>'
    x += {"d": 170, "r": 126, "o": 165, "p": 170, "i": 92, "n": 175, "g": 160, "?": 145}[ch]
put("stroke-B", "Face drooping: an uneven smile", "Face drooping? Ask them to smile. Uneven? Call 911. Every minute counts.",
    "Act FAST: show the exact symptom check (ask them to smile) and demand the action", "Call 911 for stroke signs",
    "Face drooping? Call 911. Every minute counts.", True,
    rect(0, 0, 4800, 1400, A) + face + t(160, 560, "Face", 330, G, 800, W) + droop
    + t(3880, 540, "Ask them", 110, O, 800, W) + t(3880, 670, "to smile.", 110, O, 800, W) + t(3880, 820, "Uneven?", 110, O, 900, Y)
    + t(160, 1150, "Call 911.", 240, O, 900, Y) + t(1640, 1150, "Every minute counts.", 130, O, 700, W) + grain() + signoff(GREY))

for k, v in boards.items():
    open(os.path.join(OUT, k + ".svg"), "w").write(v)
mp = os.path.join(OUT, "options.json")
rows = json.load(open(mp))
for r_ in rows:
    if r_["id"] in meta:
        r_.update(meta[r_["id"]])
json.dump(rows, open(mp, "w"), indent=1, ensure_ascii=False)
print("v3 overrides written:", ", ".join(boards))
