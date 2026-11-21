#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one open passport spread for the invented Republic of Velmaris:
a data page (portrait + machine-readable zone) and a visa/stamps page
whose stamps form one coherent travel history after the issue date.

Deterministic, no network, PIL only. Writes entry.png to
$MAKEFUN_OUTPUT_DIR (default /output).
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
MONO_B = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")

W, H = 1024, 1024
CREAM = (247, 241, 221, 255)
CREAM_DARK = (238, 230, 203, 255)
NAVY = (31, 42, 68, 255)
NAVY_SOFT = (58, 74, 106, 255)
GOLD = (176, 141, 58, 255)
GOLD_SOFT = (201, 169, 92, 255)
GREY = (110, 108, 96, 255)
RED = (148, 38, 44, 255)
BLUE = (28, 74, 128, 255)
GREEN = (38, 96, 66, 255)
DESK = (46, 52, 64, 255)
DESK_DARK = (34, 39, 49, 255)
SKIN = (217, 169, 134, 255)
SKIN_DARK = (198, 148, 112, 255)
HAIR = (58, 42, 30, 255)
JACKET = (44, 62, 90, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with letter tracking; returns width used."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def center(draw, cx, y, text, fnt, fill, tracking=0):
    w = draw.textlength(text, font=fnt) + tracking * max(0, len(text) - 1)
    tracked(draw, (cx - w / 2, y), text, fnt, fill, tracking)
    return w


# --- ICAO MRZ check digits (7-3-1 weights) -------------------------------
def _val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 .. Z=35


def check_digit(s):
    weights = (7, 3, 1)
    return str(sum(_val(c) * weights[i % 3] for i, c in enumerate(s)) % 10)


def mrz_lines():
    line1 = "P<VLMMARIN<<ELENA<SOFIA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VM0418827"
    nat = "VLM"
    dob = "940314"
    sex = "F"
    exp = "360601"
    pers = "<" * 14
    body = (doc + check_digit(doc) + nat + dob + check_digit(dob) + sex
            + exp + check_digit(exp) + pers + check_digit(pers))
    line2 = body + check_digit(body)
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


# --- small drawing helpers -------------------------------------------------
def guilloche(draw, box, colour, step=14):
    """Faint wavy security lines across a page."""
    x0, y0, x1, y1 = box
    for yy in range(y0, y1, step):
        pts = []
        for xx in range(x0, x1 + 1, 12):
            pts.append((xx, yy + 3 * ((xx // 24) % 2) - 1))
        draw.line(pts, fill=colour, width=1)


def emblem(draw, cx, cy, r, gold=GOLD, navy=NAVY):
    """Velmaris roundel: lighthouse over waves."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=gold, width=3)
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=gold, width=1)
    # rays
    for a in (-35, -18, 0, 18, 35):
        import math
        rad = math.radians(a - 90)
        x2 = cx + int(0.62 * r * math.cos(rad))
        y2 = cy + int(0.62 * r * math.sin(rad))
        draw.line([(cx, cy - int(0.18 * r)), (x2, y2)], fill=gold, width=2)
    # tower
    tw = int(0.16 * r)
    draw.polygon([(cx - tw, cy + int(0.55 * r)), (cx - int(0.6 * tw), cy - int(0.28 * r)),
                  (cx + int(0.6 * tw), cy - int(0.28 * r)), (cx + tw, cy + int(0.55 * r))],
                 fill=navy)
    draw.rectangle([cx - int(0.9 * tw), cy - int(0.42 * r),
                    cx + int(0.9 * tw), cy - int(0.28 * r)], fill=navy)
    draw.ellipse([cx - int(0.5 * tw), cy - int(0.52 * r),
                  cx + int(0.5 * tw), cy - int(0.40 * r)], fill=gold)
    # waves
    for k, yy in enumerate((0.62, 0.74, 0.86)):
        y = cy + int(yy * r)
        pts = []
        for xx in range(cx - r + 8, cx + r - 7, 6):
            pts.append((xx, y + (4 if ((xx // 12) % 2 == 0) else -4)))
        draw.line(pts, fill=navy if k % 2 == 0 else gold, width=2)


def draw_portrait(base, box):
    """Stylised passport portrait: front-facing bust, flat vector style."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    photo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(photo)
    # background gradient (light steel blue)
    for yy in range(h):
        t = yy / h
        c = (int(184 + (143 - 184) * t), int(199 + (165 - 199) * t),
             int(217 + (189 - 217) * t), 255)
        d.line([(0, yy), (w, yy)], fill=c)
    cx = w // 2
    # shoulders / jacket
    d.pieslice([cx - 78, h - 96, cx + 78, h + 60], 180, 360, fill=JACKET)
    d.rectangle([cx - 78, h - 58, cx + 78, h], fill=JACKET)
    # shirt + collar
    d.polygon([(cx - 16, h - 62), (cx + 16, h - 62), (cx, h - 34)], fill=(240, 238, 230, 255))
    d.polygon([(cx - 16, h - 62), (cx - 2, h - 48), (cx - 16, h - 34)], fill=(225, 222, 210, 255))
    d.polygon([(cx + 16, h - 62), (cx + 2, h - 48), (cx + 16, h - 34)], fill=(225, 222, 210, 255))
    # neck
    d.rectangle([cx - 13, h - 92, cx + 13, h - 58], fill=SKIN_DARK)
    # head
    d.ellipse([cx - 34, 26, cx + 34, 104], fill=SKIN)
    # ears
    d.ellipse([cx - 40, 58, cx - 30, 78], fill=SKIN)
    d.ellipse([cx + 30, 58, cx + 40, 78], fill=SKIN)
    # hair: cap + side sweeps
    d.pieslice([cx - 37, 18, cx + 37, 78], 180, 360, fill=HAIR)
    d.polygon([(cx - 37, 52), (cx - 30, 22), (cx - 22, 44), (cx - 30, 62)], fill=HAIR)
    d.polygon([(cx + 37, 52), (cx + 30, 22), (cx + 22, 44), (cx + 30, 62)], fill=HAIR)
    d.ellipse([cx - 36, 30, cx - 8, 52], fill=HAIR)
    # brows
    d.arc([cx - 22, 58, cx - 4, 68], 200, 340, fill=HAIR, width=2)
    d.arc([cx + 4, 58, cx + 22, 68], 200, 340, fill=HAIR, width=2)
    # eyes
    d.ellipse([cx - 18, 66, cx - 10, 71], fill=(38, 30, 26, 255))
    d.ellipse([cx + 10, 66, cx + 18, 71], fill=(38, 30, 26, 255))
    # nose
    d.line([(cx, 70), (cx - 2, 84), (cx + 3, 86)], fill=SKIN_DARK, width=2)
    # mouth
    d.arc([cx - 10, 90, cx + 10, 100], 20, 160, fill=(150, 90, 80, 255), width=2)
    # chin shadow
    d.arc([cx - 14, 88, cx + 14, 108], 30, 150, fill=SKIN_DARK, width=1)
    base.alpha_composite(photo, (x0, y0))


def stamp_rect(base, box, lines, colour, angle, size=11, bold=True):
    """Rectangular border-control stamp, slightly rotated."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(SANS_B if bold else SANS, size)
    d.rounded_rectangle([3, 3, w + 4, h + 4], radius=6, outline=colour, width=2)
    d.rounded_rectangle([7, 7, w, h], radius=4, outline=colour, width=1)
    yy = 9
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((w + 8 - tw) / 2, yy), ln, font=f, fill=colour)
        yy += size + 3
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (x0 - 4, y0 - 4))


def stamp_circle(base, box, top, mid, bottom, colour, angle, size=10):
    """Circular arrival/departure stamp."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = (w + 8) // 2, (h + 8) // 2
    r = min(w, h) // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=2)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], outline=colour, width=1)
    f = font(SANS_B, size)
    for j, ln in enumerate((top, mid, bottom)):
        tw = d.textlength(ln, font=f)
        d.text((cx - tw / 2, cy - 16 + j * (size + 2)), ln, font=f, fill=colour)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (x0 - 4, y0 - 4))


def field(draw, x, y, label, value, label_f, value_f, vsize=None):
    draw.text((x, y), label, font=label_f, fill=GREY)
    fnt = font(SANS_B, vsize) if vsize else value_f
    draw.text((x, y + 13), value, font=fnt, fill=NAVY)


# --- pages -----------------------------------------------------------------
def data_page(img):
    px, py, pw, ph = 32, 162, 470, 700
    page = Image.new("RGBA", (pw, ph), CREAM)
    d = ImageDraw.Draw(page)
    guilloche(d, (14, 120, pw - 14, ph - 120), (214, 200, 158, 255), step=18)
    d.rectangle([10, 10, pw - 11, ph - 11], outline=GOLD, width=2)
    d.rectangle([16, 16, pw - 17, ph - 17], outline=GOLD_SOFT, width=1)

    f_title = font(SERIF_B, 21)
    f_sub = font(SANS, 10)
    f_label = font(SANS, 9)
    f_value = font(SANS_B, 14)
    f_small = font(SANS, 10)

    center(d, pw // 2, 30, "REPUBLIC OF VELMARIS", f_title, NAVY, tracking=1)
    center(d, pw // 2, 58, "REPUBLIKA  VELMARIS", f_sub, NAVY_SOFT, tracking=3)
    emblem(d, pw // 2, 118, 34)
    center(d, pw // 2, 164, "PASSPORT  ·  PUTOVNICA", f_sub, NAVY, tracking=2)
    d.line([(30, 188), (pw - 30, 188)], fill=GOLD, width=1)

    # portrait + right-hand fields
    draw_portrait(page, (34, 206, 184, 396))
    d.rectangle([34, 206, 184, 396], outline=NAVY_SOFT, width=2)
    fx = 202
    field(d, fx, 206, "TYPE / VRSTA", "P", f_label, f_value)
    field(d, fx + 62, 206, "CODE / KOD", "VLM", f_label, f_value)
    field(d, fx + 150, 206, "PASSPORT No. / BROJ", "VM0418827", f_label, f_value)
    field(d, fx, 248, "SURNAME / PREZIME", "MARIN", f_label, f_value)
    field(d, fx, 290, "GIVEN NAMES / IMENA", "ELENA SOFIA", f_label, f_value)
    field(d, fx, 332, "NATIONALITY / DRŽAVLJANSTVO", "VELMARIN", f_label, f_value)
    field(d, 34, 414, "DATE OF BIRTH / DATUM ROĐENJA", "14 MAR 1994", f_label, f_value)
    field(d, 248, 414, "SEX / SPOL", "F", f_label, f_value)
    field(d, 34, 456, "PLACE OF BIRTH / MJESTO ROĐENJA", "PORT ANSELM", f_label, f_value)
    field(d, 248, 456, "DATE OF ISSUE / IZDANO", "02 JUN 2026", f_label, f_value)
    field(d, 34, 498, "AUTHORITY / TIJELO", "PORT ANSELM", f_label, f_value)
    field(d, 248, 498, "DATE OF EXPIRY / VRIJEDI DO", "01 JUN 2036", f_label, f_value)
    d.line([(30, 544), (pw - 30, 544)], fill=GOLD, width=1)
    # signature
    f_sig = font(SERIF, 20)
    d.text((34, 556), "Elena Sofia Marin", font=f_sig, fill=NAVY)
    d.line([(34, 582), (210, 582)], fill=NAVY_SOFT, width=1)
    d.text((34, 586), "HOLDER'S SIGNATURE / POTPIS", font=f_label, fill=GREY)

    # seafarer endorsement stamp, clear zone right of the signature
    stamp_rect(page, (270, 552, 430, 600),
               ["SEAFARER", "LIGHTHOUSE SERVICE"], RED, -8, size=9)

    # MRZ
    l1, l2 = mrz_lines()
    f_mrz = font(MONO, 15)
    d.rectangle([24, 616, pw - 24, 668], fill=CREAM_DARK)
    d.text((30, 622), l1, font=f_mrz, fill=NAVY)
    d.text((30, 644), l2, font=f_mrz, fill=NAVY)
    return page


def visa_page(img):
    px, py, pw, ph = 522, 162, 470, 700
    page = Image.new("RGBA", (pw, ph), CREAM)
    d = ImageDraw.Draw(page)
    guilloche(d, (14, 60, pw - 14, ph - 60), (214, 200, 158, 255), step=18)
    d.rectangle([10, 10, pw - 11, ph - 11], outline=GOLD, width=2)
    d.rectangle([16, 16, pw - 17, ph - 17], outline=GOLD_SOFT, width=1)

    f_head = font(SERIF_B, 16)
    f_sub = font(SANS, 10)
    f_label = font(SANS, 9)
    center(d, pw // 2, 28, "VISAS", f_head, NAVY, tracking=4)
    center(d, pw // 2, 52, "VIZE  ·  STAMPS  ·  ŽIGOVI", f_sub, GREY, tracking=2)
    d.line([(30, 76), (pw - 30, 76)], fill=GOLD, width=1)

    # --- Sardonia visa sticker ---
    vx0, vy0, vx1, vy1 = 34, 92, pw - 34, 210
    d.rectangle([vx0, vy0, vx1, vy1], fill=(226, 238, 228, 255),
                outline=GREEN, width=2)
    d.rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy1 - 5], outline=GREEN, width=1)
    f_vh = font(SANS_B, 12)
    f_vt = font(SANS, 10)
    f_vb = font(SANS_B, 10)
    d.text((vx0 + 12, vy0 + 10), "VISA — KINGDOM OF SARDONIA", font=f_vh, fill=GREEN)
    d.text((vx0 + 12, vy0 + 32), "Single entry  ·  90 days  ·  No. SD-2026-11844",
           font=f_vt, fill=NAVY)
    d.text((vx0 + 12, vy0 + 50), "Issued 28 AUG 2026 — Port Anselm  ·  Fee paid 25 VLD",
           font=f_vt, fill=NAVY)
    d.text((vx0 + 12, vy0 + 70), "CONDITION: REPORT TO HARBOUR", font=f_vb, fill=RED)
    d.text((vx0 + 12, vy0 + 86), "MASTER ON ARRIVAL", font=f_vb, fill=RED)
    emblem(d, vx1 - 42, vy0 + 34, 22, gold=GOLD, navy=GREEN)

    # --- border stamps: one coherent trip, all after issue 02 JUN 2026 ---
    # row 1
    stamp_rect(page, (34, 232, 236, 300),
               ["DARUVIA", "ARRIVAL  18 JUN 2026", "KESTREL GATE"], BLUE, -4)
    stamp_rect(page, (254, 232, 436, 300),
               ["DARUVIA", "DEPARTURE  25 JUN 2026", "KESTREL GATE"], RED, 3)
    # row 2
    stamp_circle(page, (48, 322, 148, 422), "ALDORRA", "ARRIVAL", "03 JUL 2026", BLUE, -6)
    stamp_circle(page, (178, 322, 278, 422), "ALDORRA", "DEPARTURE", "12 JUL 2026", RED, 5)
    stamp_rect(page, (306, 336, 436, 404),
               ["SARDONIA", "ARRIVAL  05 SEP 2026", "PORT LUMEN"], BLUE, -3, size=10)
    # row 3
    stamp_rect(page, (34, 452, 226, 520),
               ["SARDONIA", "DEPARTURE  19 SEP 2026", "PORT LUMEN"], RED, 4)
    stamp_circle(page, (250, 442, 334, 526), "KOSTEN IS.", "ARRIVAL", "08 OCT 2026", BLUE, -5, size=9)
    stamp_circle(page, (352, 442, 436, 526), "KOSTEN IS.", "DEPARTURE", "22 OCT 2026", RED, 6, size=9)

    d.line([(30, 560), (pw - 30, 560)], fill=GOLD, width=1)
    f_note = font(SANS, 10)
    d.text((34, 574), "This passport contains 32 pages.", font=f_note, fill=GREY)
    d.text((34, 592), "If found, please return to any Velmarin", font=f_note, fill=GREY)
    d.text((34, 610), "consulate or to the Harbour Master, Port Anselm.",
           font=f_note, fill=GREY)
    f_pg = font(SANS_B, 12)
    d.text((pw - 44, 640), "12", font=f_pg, fill=NAVY_SOFT)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    img = Image.new("RGBA", (W, H), DESK)
    d = ImageDraw.Draw(img)
    # desk shading + soft shadow under the spread
    for yy in range(H):
        t = yy / H
        c = (int(46 + (34 - 46) * t), int(52 + (39 - 52) * t),
             int(64 + (49 - 64) * t), 255)
        d.line([(0, yy), (W, yy)], fill=c)
    d.rounded_rectangle([24, 154, 1000, 874], radius=8, fill=DESK_DARK)
    d.rounded_rectangle([26, 156, 998, 872], radius=8, fill=(20, 23, 30, 255))

    left = data_page(img)
    right = visa_page(img)
    img.alpha_composite(left, (32, 162))
    img.alpha_composite(right, (522, 162))
    # centre gutter shadow
    gutter = Image.new("RGBA", (14, 700), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gutter)
    for xx in range(14):
        a = 90 - abs(xx - 7) * 12
        gd.line([(xx, 0), (xx, 700)], fill=(0, 0, 0, max(0, a)))
    img.alpha_composite(gutter, (495, 162))

    out = img.convert("RGB")
    path = os.path.join(out_dir, "entry.png")
    out.save(path, format="PNG", optimize=True)
    print("wrote", path, out.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
