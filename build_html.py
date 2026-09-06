#!/usr/bin/env python3
"""Render plants_egypt.json -> PvZ2_Plants_Ancient_Egypt_Demo.html (A4 landscape pages)."""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "PvZ2_Plants_Ancient_Egypt_Demo.html")

with open(os.path.join(HERE, "plants_egypt.json"), encoding="utf-8") as f:
    PLANTS = json.load(f)

def esc(s): return html.escape(str(s))

CSS = r"""
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #ddd; }
body {
  font-family: "Fredoka", "Baloo 2", "Nunito", "Arial Rounded MT Bold", "Varela Round",
               "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Noto Sans SC",
               "Source Han Sans SC", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
  color: #3E2723;
}
.page {
  width: 297mm; height: 210mm; position: relative; overflow: hidden;
  background: #FBF1D8; page-break-after: always; break-after: page;
  margin: 0 auto 8mm auto; /* screen only spacing */
}
@media print { .page { margin: 0; } html, body { background: #FBF1D8; } }
/* pyramids */
.pyramids { position: absolute; left: 0; right: 0; bottom: 0; height: 40mm; pointer-events: none; }
.pyramids svg { width: 100%; height: 100%; display: block; }
.pageno {
  position: absolute; bottom: 4mm; left: 50%; transform: translateX(-50%);
  background: #5D4037; color: #fff; font-weight: 700; font-size: 10pt;
  padding: 2px 12px; border-radius: 999px;
}

/* ---------- cover ---------- */
.cover { text-align: center; padding-top: 18mm; }
.cover .title { font-size: 40pt; font-weight: 800; color: #7CB342; letter-spacing: .5px; }
.cover .sub { font-size: 26pt; font-weight: 800; color: #5D4037; margin-top: 4mm; }
.cover .zh { font-size: 20pt; color: #3E2723; margin-top: 3mm; }
.cover .strip {
  display: flex; justify-content: center; align-items: flex-end; gap: 4mm;
  margin: 12mm 12mm 0 12mm;
}
.cover .strip img { height: 32mm; width: auto; }
.cover .strip .n { font-size: 8pt; font-weight: 700; color: #5D4037; margin-top: 1mm; text-align: center; }
.cover .tag { margin-top: 8mm; font-size: 16pt; font-weight: 700; color: #5D4037; }
.cover .tagzh { font-size: 13pt; margin-top: 1mm; }
.cover .demo { position: absolute; bottom: 12mm; left: 0; right: 0; font-size: 10pt; color: #8D6E63; }

/* ---------- legend ---------- */
.legend { padding: 14mm 24mm; }
.legend h1 { margin: 0; text-align: center; font-size: 26pt; color: #5D4037; }
.legend h2 { margin: 1mm 0 8mm; text-align: center; font-size: 15pt; font-weight: 500; }
.legend .row {
  display: grid; grid-template-columns: 22mm 60mm 1fr; align-items: center; gap: 4mm;
  background: #fff; border: 2px solid #E8CF97; border-radius: 6mm; padding: 4mm 6mm; margin-bottom: 4mm;
}
.legend .row .ic { font-size: 26pt; text-align: center; }
.legend .row .k { font-size: 17pt; font-weight: 800; color: #5D4037; }
.legend .row .kz { font-size: 12pt; }
.legend .row .d { font-size: 13pt; }
.legend .row .dz { font-size: 11pt; color: #6D4C41; }

/* ---------- plant page ---------- */
.plant { display: grid; grid-template-columns: 100mm 1fr; gap: 8mm; padding: 10mm 12mm 14mm; height: 100%; }
.card {
  background: #fff; border: 2mm solid var(--c); border-radius: 9mm; position: relative;
  display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 6mm 6mm 26mm;
}
.card img { max-width: 100%; max-height: 120mm; object-fit: contain; filter: drop-shadow(0 4px 4px rgba(0,0,0,.18)); }
.card .ribbon {
  position: absolute; left: 5mm; right: 5mm; bottom: 5mm; background: var(--c); color: #fff;
  border-radius: 5mm; text-align: center; padding: 3mm 2mm;
}
.card .ribbon .en { font-size: 20pt; font-weight: 800; line-height: 1.1; }
.card .ribbon .zh { font-size: 13pt; margin-top: 1mm; }

.info { display: flex; flex-direction: column; }
.head { display: flex; justify-content: space-between; align-items: flex-start; }
.head .en { font-size: 36pt; font-weight: 800; color: var(--c); line-height: 1; }
.head .zh { font-size: 19pt; margin-top: 2mm; }
.head .meta { text-align: right; font-size: 9.5pt; color: #6D4C41; line-height: 1.5; padding-top: 2mm; }
.head .meta b { display: inline-block; background: #E8CF97; color: #5D4037; border-radius: 999px; padding: 1px 8px; margin-bottom: 1mm; }

.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 6mm; }
.stat {
  background: #fff; border: 2px solid #E8CF97; border-radius: 5mm; padding: 3mm 4mm;
  display: grid; grid-template-columns: 14mm 1fr auto; align-items: center; gap: 3mm; min-height: 22mm;
}
.stat .ic { font-size: 24pt; text-align: center; line-height: 1; }
.stat .k { font-size: 13pt; font-weight: 800; color: #5D4037; }
.stat .kz { font-size: 9.5pt; color: #8D6E63; }
.stat .v { font-size: 18pt; font-weight: 800; color: var(--c); text-align: right; white-space: nowrap; }
.stat .v.small { font-size: 12.5pt; }

.range { margin-top: 4mm; font-size: 12pt; }
.range b { color: #5D4037; }

.bubble {
  margin-top: 5mm; background: var(--c); color: #fff; border-radius: 6mm; padding: 5mm 6mm; position: relative;
}
.bubble:after {
  content: ""; position: absolute; left: 10mm; bottom: -4mm; border: 4mm solid transparent; border-top-color: var(--c); border-bottom: 0;
}
.bubble .en { font-size: 18pt; font-weight: 800; line-height: 1.2; }
.bubble .zh { font-size: 13pt; margin-top: 2mm; opacity: .95; }

.words { margin-top: 8mm; }
.words .t { font-size: 13pt; font-weight: 700; color: #5D4037; margin-bottom: 2.5mm; }
.words .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.word { background: #fff; border: 2px solid var(--c); border-radius: 4mm; text-align: center; padding: 3mm 2mm; }
.word .en { font-size: 16pt; font-weight: 800; color: var(--c); }
.word .zh { font-size: 11pt; margin-top: 1mm; }
"""

PYRAMIDS = """<div class="pyramids"><svg viewBox="0 0 1122 150" preserveAspectRatio="none">
<polygon points="40,150 130,80 220,150" fill="#E8CF97"/>
<polygon points="170,150 300,45 430,150" fill="#E8CF97"/>
<polygon points="820,150 920,70 1020,150" fill="#E8CF97"/>
<polygon points="980,150 1040,100 1100,150" fill="#E8CF97"/>
<rect x="0" y="132" width="1122" height="18" fill="#E8CF97"/>
</svg></div>"""

def img_tag(p, cls=""):
    local = f"images/{p['file']}"
    remote = esc(p["img"])
    return f'<img class="{cls}" src="{local}" onerror="this.onerror=null;this.src=\'{remote}\'" alt="{esc(p["en"])}">'

def cover(total):
    strip = "".join(
        f'<div>{img_tag(p)}<div class="n">{esc(p["en"])}</div></div>' for p in PLANTS)
    return f"""
<section class="page cover">
  <div class="title">Plants vs. Zombies 2</div>
  <div class="sub">My Plant Book: Ancient Egypt</div>
  <div class="zh">我的植物图鉴 · 古埃及</div>
  <div class="strip">{strip}</div>
  <div class="tag">Learn English with your favourite plants!</div>
  <div class="tagzh">和你最喜欢的植物一起学英语！</div>
  <div class="demo">DEMO · {len(PLANTS)} plants · ages 5-8</div>
  {PYRAMIDS}
</section>"""

def legend(total):
    rows = [
        ("☀️", "Sun Cost", "阳光消耗", "How much sun you need to plant it.", "种它需要多少阳光。"),
        ("⏱️", "Recharge", "冷却时间", "How long you wait before planting another one.", "再种一个要等多久。"),
        ("❤️", "Toughness", "生命值", "How much damage it can take.", "它能承受多少伤害。"),
        ("⚡", "Damage", "攻击力", "How hard it hits zombies.", "它打僵尸有多疼。"),
    ]
    body = "".join(f"""
    <div class="row"><div class="ic">{ic}</div>
      <div><div class="k">{k}</div><div class="kz">{kz}</div></div>
      <div><div class="d">{d}</div><div class="dz">{dz}</div></div></div>""" for ic, k, kz, d, dz in rows)
    return f"""
<section class="page legend">
  <h1>How to read a plant card</h1>
  <h2>怎么看植物卡片</h2>
  {body}
  {PYRAMIDS}<div class="pageno">2 / {total}</div>
</section>"""

def plant_page(p, n, total):
    def stat(ic, k, kz, v):
        small = " small" if len(str(v)) > 7 else ""
        return f'<div class="stat"><div class="ic">{ic}</div><div><div class="k">{k}</div><div class="kz">{kz}</div></div><div class="v{small}">{esc(v)}</div></div>'
    stats = "".join([
        stat("☀️", "Sun", "阳光", p["sun"]),
        stat("⏱️", "Recharge", "冷却", f"{p['recharge']} · {p['recharge_zh']}"),
        stat("❤️", "Toughness", "生命", p["toughness"]),
        stat("⚡", "Damage", "攻击", p["damage"]),
    ])
    words = "".join(f'<div class="word"><div class="en">{esc(en)}</div><div class="zh">{esc(zh)}</div></div>' for en, zh in p["words"])
    return f"""
<section class="page" style="--c:{p['color']}">
  <div class="plant">
    <div class="card">
      {img_tag(p)}
      <div class="ribbon"><div class="en">{esc(p['en'])}</div><div class="zh">{esc(p['zh'])}</div></div>
    </div>
    <div class="info">
      <div class="head">
        <div><div class="en">{esc(p['en'])}</div><div class="zh">{esc(p['zh'])}</div></div>
        <div class="meta"><b>Ancient Egypt · 古埃及</b><br>Unlock: {esc(p['unlock'])}<br>解锁：{esc(p['unlock_zh'])}</div>
      </div>
      <div class="stats">{stats}</div>
      <div class="range"><b>Range 范围：</b>{esc(p['range'])} &nbsp;/&nbsp; {esc(p['range_zh'])}</div>
      <div class="bubble"><div class="en">{esc(p['sentence'])}</div><div class="zh">{esc(p['sentence_zh'])}</div></div>
      <div class="words"><div class="t">Words to learn · 学单词</div><div class="grid">{words}</div></div>
    </div>
  </div>
  {PYRAMIDS}<div class="pageno">{n} / {total}</div>
</section>"""

def main():
    total = 2 + len(PLANTS)
    pages = [cover(total), legend(total)] + [plant_page(p, 3 + i, total) for i, p in enumerate(PLANTS)]
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>PvZ2 Plant Book · Ancient Egypt (Demo)</title>
<style>{CSS}</style></head>
<body>{''.join(pages)}</body></html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
