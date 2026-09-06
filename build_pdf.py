#!/usr/bin/env python3
"""Build a kid-friendly bilingual PvZ2 plant book (Ancient Egypt) as PDF."""
import json, os, sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "public", "images")
OUT = os.path.join(HERE, "PvZ2_Plants_Ancient_Egypt_Demo.pdf")

# ---------- fonts ----------
def find_font(cands):
    for p in cands:
        if os.path.exists(p):
            return p
    return None

CJK = find_font([
    os.path.join(HERE, "fonts", "NotoSansSC-Bold.ttf"),
    os.path.join(HERE, "fonts", "NotoSansSC-Regular.ttf"),
    os.path.join(HERE, "fonts", "NotoSansCJKsc-Regular.otf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",
])
if not CJK:
    sys.exit("No CJK font found")
try:
    pdfmetrics.registerFont(TTFont("CJK", CJK))
except Exception:
    pdfmetrics.registerFont(TTFont("CJK", CJK, subfontIndex=0))

ROUND = find_font([
    os.path.join(HERE, "fonts", "Fredoka-Bold.ttf"),
    os.path.join(HERE, "fonts", "Baloo2-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
if ROUND:
    pdfmetrics.registerFont(TTFont("Round", ROUND))
    EN_BOLD = "Round"
else:
    EN_BOLD = "Helvetica-Bold"
EN = "Helvetica"

# ---------- palette ----------
SAND = HexColor("#FBF1D8")
SAND_DARK = HexColor("#E8CF97")
BROWN = HexColor("#5D4037")
INK = HexColor("#3E2723")
SUN = HexColor("#FFB300")
SKY = HexColor("#64B5F6")
GRASS = HexColor("#7CB342")
RED = HexColor("#EF5350")
PURPLE = HexColor("#9575CD")

W, H = landscape(A4)
M = 36  # margin

def rrect(c, x, y, w, h, r, fill, stroke=None, lw=2):
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke else 0)

def text(c, x, y, s, font, size, color=INK, align="left"):
    c.setFont(font, size); c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)

def draw_sun_icon(c, x, y, r):
    c.setFillColor(SUN); c.setStrokeColor(HexColor("#F57F17")); c.setLineWidth(1.5)
    import math
    for i in range(12):
        a = i * math.pi / 6
        c.line(x + r*1.15*math.cos(a), y + r*1.15*math.sin(a), x + r*1.5*math.cos(a), y + r*1.5*math.sin(a))
    c.circle(x, y, r, fill=1, stroke=1)

def draw_heart(c, x, y, s, color=RED):
    p = c.beginPath()
    p.moveTo(x, y - s)
    p.curveTo(x - s*1.6, y + s*0.2, x - s*0.6, y + s*1.2, x, y + s*0.4)
    p.curveTo(x + s*0.6, y + s*1.2, x + s*1.6, y + s*0.2, x, y - s)
    c.setFillColor(color); c.setStrokeColor(color); c.drawPath(p, fill=1, stroke=0)

def draw_bolt(c, x, y, s, color=SUN):
    pts = [(x, y+s), (x-s*0.45, y), (x-s*0.05, y), (x-s*0.3, y-s), (x+s*0.45, y+s*0.1), (x+s*0.05, y+s*0.1)]
    p = c.beginPath(); p.moveTo(*pts[0])
    for pt in pts[1:]: p.lineTo(*pt)
    p.close(); c.setFillColor(color); c.drawPath(p, fill=1, stroke=0)

def draw_clock(c, x, y, r, color=SKY):
    c.setFillColor(white); c.setStrokeColor(color); c.setLineWidth(2.5)
    c.circle(x, y, r, fill=1, stroke=1)
    c.setStrokeColor(color); c.setLineWidth(2)
    c.line(x, y, x, y + r*0.6); c.line(x, y, x + r*0.45, y)

def background(c, page_no=None, total=None):
    c.setFillColor(SAND); c.rect(0, 0, W, H, fill=1, stroke=0)
    # pyramids silhouette footer
    c.setFillColor(SAND_DARK)
    for (bx, bw, bh) in [(40, 180, 70), (170, 260, 105), (W-300, 200, 80), (W-140, 120, 50)]:
        p = c.beginPath(); p.moveTo(bx, 0); p.lineTo(bx + bw/2, bh); p.lineTo(bx + bw, 0); p.close()
        c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(SAND_DARK); c.rect(0, 0, W, 18, fill=1, stroke=0)
    if page_no:
        rrect(c, W/2 - 26, 6, 52, 22, 11, BROWN)
        text(c, W/2, 12, f"{page_no} / {total}", EN_BOLD, 11, white, "center")

def fit_image(path, box_w, box_h):
    img = ImageReader(path)
    iw, ih = img.getSize()
    s = min(box_w/iw, box_h/ih)
    return img, iw*s, ih*s

# ---------- pages ----------
def cover(c, plants):
    background(c)
    rrect(c, M, H - 250, W - 2*M, 200, 28, white, SAND_DARK, 4)
    text(c, W/2, H - 130, "Plants vs. Zombies 2", EN_BOLD, 40, GRASS, "center")
    text(c, W/2, H - 178, "My Plant Book: Ancient Egypt", EN_BOLD, 28, BROWN, "center")
    text(c, W/2, H - 222, "我的植物图鉴 · 古埃及", "CJK", 24, INK, "center")
    # plant thumbnails row
    n = len(plants); tw = (W - 2*M) / n
    for i, p in enumerate(plants):
        path = os.path.join(IMG_DIR, p.get("pvzg_file") or p["file"])
        if os.path.exists(path):
            img, w, h = fit_image(path, tw - 10, 120)
            c.drawImage(img, M + i*tw + (tw - w)/2, 150, w, h, mask="auto")
        text(c, M + i*tw + tw/2, 132, p["en"], EN_BOLD, 8, BROWN, "center")
    text(c, W/2, 95, "Learn English with your favourite plants!", EN_BOLD, 18, BROWN, "center")
    text(c, W/2, 68, "和你最喜欢的植物一起学英语！", "CJK", 15, INK, "center")
    text(c, W/2, 40, "DEMO  ·  11 plants  ·  ages 5-8", EN, 10, BROWN, "center")
    c.showPage()

def legend(c, total):
    background(c, 2, total)
    text(c, W/2, H - 70, "How to read a plant card", EN_BOLD, 28, BROWN, "center")
    text(c, W/2, H - 100, "怎么看植物卡片", "CJK", 18, INK, "center")
    items = [
        ("sun", "Sun Cost", "阳光消耗", "How much sun you need to plant it.", "种它需要多少阳光。"),
        ("clock", "Recharge", "冷却时间", "How long you wait before planting another.", "再种一个要等多久。"),
        ("heart", "Toughness", "生命值", "How much damage it can take.", "它能承受多少伤害。"),
        ("bolt", "Damage", "攻击力", "How hard it hits zombies.", "它打僵尸有多疼。"),
    ]
    y = H - 160
    for icon, en, zh, d_en, d_zh in items:
        rrect(c, M + 40, y - 40, W - 2*M - 80, 72, 16, white, SAND_DARK, 2)
        cx, cy = M + 82, y - 4
        if icon == "sun": draw_sun_icon(c, cx, cy, 14)
        elif icon == "clock": draw_clock(c, cx, cy, 16)
        elif icon == "heart": draw_heart(c, cx, cy - 2, 13)
        else: draw_bolt(c, cx, cy, 16)
        text(c, M + 125, y + 6, en, EN_BOLD, 20, BROWN)
        text(c, M + 125, y - 18, zh, "CJK", 14, INK)
        text(c, M + 330, y + 6, d_en, EN, 14, INK)
        text(c, M + 330, y - 18, d_zh, "CJK", 12, BROWN)
        y -= 90
    c.showPage()

def plant_page(c, p, page_no, total):
    background(c, page_no, total)
    accent = HexColor(p["color"])
    # ---- left: image card ----
    lx, ly, lw, lh = M, 60, 300, H - 60 - 40
    rrect(c, lx, ly, lw, lh, 26, white, accent, 5)
    path = os.path.join(IMG_DIR, p.get("pvzg_file") or p["file"])
    if os.path.exists(path):
        img, w, h = fit_image(path, lw - 40, lh - 120)
        c.drawImage(img, lx + (lw - w)/2, ly + 90 + (lh - 120 - h)/2, w, h, mask="auto")
    else:
        text(c, lx + lw/2, ly + lh/2, "(image)", EN, 14, BROWN, "center")
    # name ribbon
    rrect(c, lx + 14, ly + 16, lw - 28, 64, 14, accent)
    text(c, lx + lw/2, ly + 50, p["en"], EN_BOLD, 24, white, "center")
    text(c, lx + lw/2, ly + 26, p["zh"], "CJK", 16, white, "center")

    # ---- right: info ----
    rx = lx + lw + 24
    rw = W - rx - M
    top = H - 40
    # big title
    text(c, rx, top - 34, p["en"], EN_BOLD, 40, accent)
    text(c, rx, top - 64, p["zh"], "CJK", 22, INK)
    # tag: family + unlock
    text(c, W - M, top - 34, "Ancient Egypt · 古埃及", "CJK", 11, BROWN, "right")
    text(c, W - M, top - 52, f"Unlock: {p['unlock']}", EN, 10, BROWN, "right")
    text(c, W - M, top - 66, f"解锁：{p['unlock_zh']}", "CJK", 10, BROWN, "right")

    # stat boxes (2x2)
    stats = [
        ("sun", "Sun", "阳光", str(p["sun"])),
        ("clock", "Recharge", "冷却", f"{p['recharge']} ({p['recharge_zh']})"),
        ("heart", "Toughness", "生命", str(p["toughness"])),
        ("bolt", "Damage", "攻击", p["damage"]),
    ]
    bw, bh, gap = (rw - 16) / 2, 78, 16
    by = top - 90 - bh
    for i, (icon, en, zh, val) in enumerate(stats):
        col, row = i % 2, i // 2
        x = rx + col * (bw + gap); y = by - row * (bh + 12)
        rrect(c, x, y, bw, bh, 16, white, SAND_DARK, 2)
        cx, cy = x + 30, y + bh/2
        if icon == "sun": draw_sun_icon(c, cx, cy, 12)
        elif icon == "clock": draw_clock(c, cx, cy, 14)
        elif icon == "heart": draw_heart(c, cx, cy - 3, 12)
        else: draw_bolt(c, cx, cy, 14)
        text(c, x + 60, y + bh - 26, en, EN_BOLD, 14, BROWN)
        text(c, x + 60, y + bh - 44, zh, "CJK", 10, BROWN)
        # value
        vfont = "CJK" if any(ord(ch) > 127 for ch in val) else EN_BOLD
        text(c, x + bw - 14, y + 26, val, vfont, 20 if len(val) < 8 else 14, accent, "right")

    # range line
    ry = by - (bh + 12) - 30
    text(c, rx, ry, "Range 范围: ", "CJK", 12, BROWN)
    text(c, rx + 88, ry, f"{p['range']}  /  {p['range_zh']}", "CJK", 12, INK)

    # official bilingual descriptions
    dy = ry - 22
    text(c, rx, dy, "About · 简介", EN_BOLD, 10, accent)
    text(c, rx + 70, dy, str(p.get("intro_en", p.get("description", "")))[:105], EN, 8, INK)
    text(c, rx + 70, dy - 13, str(p.get("intro_zh", p.get("description_zh", "")))[:72], "CJK", 8, BROWN)
    text(c, rx, dy - 31, "Plant Food · 叶绿素", EN_BOLD, 9, accent)
    text(c, rx + 100, dy - 31, str(p.get("plant_food", ""))[:82], EN, 8, INK)
    text(c, rx + 100, dy - 44, str(p.get("plant_food_zh", ""))[:55], "CJK", 8, BROWN)

    # sentence bubble
    sy = ry - 72
    sh = 84
    rrect(c, rx, sy - sh, rw, sh, 20, accent)
    # little tail
    p3 = c.beginPath(); p3.moveTo(rx + 30, sy - sh + 2); p3.lineTo(rx + 8, sy - sh - 14); p3.lineTo(rx + 52, sy - sh + 2); p3.close()
    c.setFillColor(accent); c.drawPath(p3, fill=1, stroke=0)
    text(c, rx + 18, sy - 34, p["sentence"], EN_BOLD, 19, white)
    text(c, rx + 18, sy - 62, p["sentence_zh"], "CJK", 14, white)

    # words to learn
    wy = sy - sh - 44
    text(c, rx, wy, "Words to learn  ·  学单词", "CJK", 14, BROWN)
    ww = (rw - 24) / 3
    for i, (en, zh) in enumerate(p["words"]):
        x = rx + i * (ww + 12); y = wy - 62
        rrect(c, x, y, ww, 50, 12, white, accent, 2)
        text(c, x + ww/2, y + 28, en, EN_BOLD, 17, accent, "center")
        text(c, x + ww/2, y + 10, zh, "CJK", 11, INK, "center")
    c.showPage()

def main():
    with open(os.path.join(HERE, "plants_egypt.json"), encoding="utf-8") as f:
        plants = json.load(f)
    total = 2 + len(plants)
    c = canvas.Canvas(OUT, pagesize=landscape(A4))
    c.setTitle("PvZ2 Plant Book - Ancient Egypt (Demo)")
    c.setAuthor("Made for Leo's kids")
    cover(c, plants)
    legend(c, total)
    for i, p in enumerate(plants):
        plant_page(c, p, 3 + i, total)
    c.save()
    print("wrote", OUT)

if __name__ == "__main__":
    main()
