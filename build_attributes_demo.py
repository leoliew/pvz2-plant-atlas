#!/usr/bin/env python3
"""Build a compact, print-ready A4 attribute almanac demo (4 plants / page)."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "PvZ2_Plants_Ancient_Egypt_Attributes_Demo.html"
PLANTS = json.loads((ROOT / "plants_egypt.json").read_text(encoding="utf-8"))

# Keep the demo aligned with the Ancient Egypt print edition while covering
# lobbed, freezing, melee, and utility mechanics.
PICKED_CODES = ("cabbagepult", "iceburg", "bonkchoy", "gravebuster")
LABELS = {
    "SUNCOST": ("Sun cost", "阳光消耗"), "RECHARGE": ("Recharge", "冷却时间"),
    "TOUGHNESS": ("Toughness", "生命"), "DAMAGE": ("Damage", "伤害"),
    "RANGE": ("Range", "索敌"), "AREA": ("Area", "范围"),
    "FAMILY": ("Family", "家族"), "DURATION": ("Duration", "持续时间"),
    "ARMINGTIME": ("Arming time", "装填时间"), "PLANTFOOD": ("Plant Food", "叶绿素效果"),
    "SUNPRODUCTION": ("Sun production", "阳光产量"), "GROWTIME": ("Grow time", "生长时间"),
    "SPECIAL": ("Special", "特点"),
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def display(value) -> str:
    if isinstance(value, dict):
        en = value.get("en", value.get("EN", ""))
        zh = value.get("zh", value.get("ZH", ""))
        return f"<span>{esc(en or zh)}</span>" + (f"<small>{esc(zh)}</small>" if zh else "")
    if isinstance(value, list):
        return esc(" · ".join(display_plain(item) for item in value))
    return esc(value)


def display_plain(value) -> str:
    if isinstance(value, dict):
        return " / ".join(f"{k}: {display_plain(v)}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(display_plain(v) for v in value)
    return str(value)


def picked():
    by_code = {plant.get("codename"): plant for plant in PLANTS}
    selected = [by_code[code] for code in PICKED_CODES if code in by_code]
    return selected or PLANTS[:4]


def attr_block(plant):
    rows = []
    for key, value in (plant.get("elements") or {}).items():
        if key == "FAMILY":
            continue
        if value in (None, "", "—"):
            continue
        en, zh = LABELS.get(key, (key.replace("_", " ").title(), "属性"))
        rows.append(
            f'<div class="attr"><b>{esc(en)}<small>{esc(zh)}</small></b>'
            f'<div class="val">{display(value)}</div></div>'
        )
    return "".join(rows)


def special_block(plant):
    rows = []
    for item in plant.get("special") or []:
        if not isinstance(item, dict):
            continue
        name, description = item.get("NAME"), item.get("DESCRIPTION")
        if name or description:
            rows.append(
                f'<div class="feature"><b>{display(name or "Special")}</b>'
                f'<span>{display(description or "")}</span></div>'
            )
    return "".join(rows)


# Every gap/padding below was measured down to the tenth of a millimetre so the
# 2x2 A4 grid keeps exactly 4 plants/page while giving every reclaimed sliver
# of margin straight back to font-size. Nothing is trimmed or hidden — content
# sections are unchanged, only denser and bigger.
CSS = r"""
@page { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; }
html, body { margin:0; background:#d8c7a7; color:#352820; font-family:"Nunito","PingFang SC",sans-serif; -webkit-font-smoothing:antialiased; }
.page { width:210mm; height:297mm; margin:0 auto 7mm; padding:6mm 6mm 7mm; position:relative; overflow:hidden; background:#fbf2dd; page-break-after:always; }
.plant-grid { display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:2.6mm; height:100%; }
.plant-card { min-width:0; min-height:0; overflow:hidden; display:flex; flex-direction:column; gap:1mm;
  padding:2mm 2.2mm; border:1.3px solid var(--accent); border-radius:3.5mm; background:#fffaf0; }

.topline { flex:0 0 auto; display:flex; justify-content:space-between; align-items:flex-start; gap:1.5mm;
  border-bottom:1px dashed #c5a66f; padding-bottom:1mm; }
.kicker { color:#9a7548; font-size:6.2pt; font-weight:800; letter-spacing:.09em; text-transform:uppercase; }
.title { margin-top:.8mm; color:var(--accent); font:800 17.5pt/1.02 "Baloo 2",sans-serif; }
.title-zh { color:#76563d; font-size:9.4pt; font-weight:700; margin-top:.3mm; }
.meta { text-align:right; color:#76563d; font-size:6.4pt; line-height:1.32; max-width:35mm; flex:0 0 auto; }
.meta b { color:var(--accent); }

.layout { flex:1; min-height:0; display:grid; grid-template-columns:22mm minmax(0,1fr); gap:1.8mm; }
.portrait { min-height:0; overflow:hidden; display:flex; flex-direction:column; align-items:center; justify-content:flex-start;
  padding:1.6mm 1.2mm; border:1px solid var(--accent); border-radius:2.5mm; background:linear-gradient(150deg,#fffaf0,#f1dfba); }
.portrait img.art { width:19.5mm; height:23mm; object-fit:contain; filter:drop-shadow(0 2px 3px #6e432540); }
.family { width:6.6mm!important; height:6.6mm!important; margin-top:1mm; }
.portrait .family-name { color:#76563d; font-size:5.3pt; font-weight:700; text-align:center; line-height:1.1; margin-top:.4mm; }
.portrait .range { width:100%; margin-top:1.4mm; padding-top:1.2mm; border-top:1px dashed #c5a66f; color:#76553c; font-size:5.4pt; line-height:1.2; text-align:center; }
.portrait .range b { display:block; color:var(--accent); font-size:5.6pt; }
.portrait .tagline { width:100%; margin-top:1.2mm; color:#76553c; font-size:5.2pt; line-height:1.2; text-align:center;
  overflow:hidden; display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:6; }

.content { min-width:0; min-height:0; display:flex; flex-direction:column; gap:1mm; }
.section-title { flex:0 0 auto; margin:0; color:#69432f; font:800 8.6pt "Baloo 2",sans-serif; }
.section-title span { margin-left:1mm; color:#a27a50; font:600 6.2pt "Nunito",sans-serif; }

.attr-grid { flex:1.55 1 0; min-height:0; display:flex; flex-wrap:wrap; align-content:stretch; gap:.9mm; }
.attr { flex:1 1 31%; min-width:24mm; display:flex; flex-direction:column; justify-content:center;
  padding:.9mm 1.3mm; border-radius:1.4mm; background:#fff; border:1px solid #e4cf9f; }
.attr b { display:block; color:var(--accent); font-size:6.6pt; }
.attr b small { display:block; color:#a88968; font-size:5.4pt; font-weight:600; }
.attr .val { margin-top:.3mm; color:#76553c; font-size:7.4pt; font-weight:800; line-height:1.1; overflow-wrap:anywhere; }
.attr .val span, .attr .val small { display:block; }
.attr .val small { color:#9e8061; font-size:5.8pt; font-weight:600; }

.copy-row { flex:1.35 1 0; min-height:0; display:grid; grid-template-columns:1fr 1fr; gap:.9mm; }
.copy-card { min-width:0; min-height:0; overflow:hidden; padding:1.3mm 1.5mm; border-radius:1.4mm; background:#f7edda; }
.copy-card b { display:block; margin-bottom:.3mm; color:var(--accent); font-size:6.9pt; }
.copy-card p { margin:0; color:#76553c; font-size:6.6pt; line-height:1.24; overflow-wrap:anywhere; }
.copy-card em { display:block; margin-top:.5mm; color:#9e8061; font-style:normal; font-size:6pt; line-height:1.2; overflow-wrap:anywhere; }

.feature-row { flex:.95 1 0; min-height:0; display:flex; flex-wrap:wrap; align-content:stretch; gap:.9mm; }
.feature { flex:1 1 46%; min-width:34mm; min-height:0; overflow:hidden; display:flex; flex-direction:column; justify-content:center;
  padding:1mm 1.4mm; border-radius:1.4mm; background:#e5f2df; }
.feature b { display:block; color:var(--accent); font-size:6.3pt; }
.feature span { display:block; margin-top:.3mm; color:#76553c; font-size:6.1pt; line-height:1.2; overflow-wrap:anywhere; }

.chat-card { flex:1.15 1 0; min-height:0; overflow:hidden; padding:1.3mm 1.5mm; border-radius:1.4mm; background:#fff0c9;
  display:flex; flex-direction:column; justify-content:center; }
.chat-card b { display:block; margin-bottom:.3mm; color:#b7762e; font-size:6.9pt; }
.chat-card .chat-en, .chat-card em { display:-webkit-box; -webkit-box-orient:vertical; overflow:hidden; }
.chat-card .chat-en { color:#76553c; font-size:6.3pt; line-height:1.24; -webkit-line-clamp:3; overflow-wrap:anywhere; }
.chat-card em { margin-top:.5mm; color:#9e8061; font-style:normal; font-size:5.9pt; line-height:1.2; -webkit-line-clamp:2; overflow-wrap:anywhere; }

.footer { position:absolute; left:6mm; right:6mm; bottom:2.6mm; display:flex; justify-content:space-between; color:#a48663; font-size:6pt; }
.page-no { color:#69432f; font-weight:800; }
@media print { html,body { background:#fbf2dd; } .page { margin:0; } }
"""


def plant_card(plant):
    family = plant.get("family") or "None"
    specials = special_block(plant)
    return f'''<article class="plant-card" style="--accent:{esc(plant.get("color", "#4e9f66"))}">
  <div class="topline"><div><div class="kicker">PVZ2 · Plant almanac · 属性图鉴</div><div class="title">{esc(plant.get("en", ""))}</div><div class="title-zh">{esc(plant.get("zh", ""))}</div></div><div class="meta"><b>{esc(plant.get("world", "Ancient Egypt"))}</b><br>Unlock: {esc(plant.get("unlock", ""))}<br>解锁：{esc(plant.get("unlock_zh", ""))}</div></div>
  <div class="layout"><aside class="portrait"><img class="art" src="/images/{esc(plant.get("pvzg_file") or plant.get("file", ""))}" onerror="this.onerror=null;this.src='{esc(plant.get("img", ""))}'" alt="{esc(plant.get("en", ""))}"><img class="family" src="/images/families/{esc(family)}_familyicon.webp" alt="{esc(plant.get("family_zh", family))}"><div class="family-name">{esc(plant.get("family_zh", family))}<br>{esc(family)}</div><div class="range"><b>Range · 范围</b>{esc(plant.get("range", ""))} · {esc(plant.get("range_zh", ""))}</div><div class="tagline">{esc(plant.get("sentence", ""))}<br>{esc(plant.get("sentence_zh", ""))}</div></aside>
    <div class="content"><h2 class="section-title">Almanac attributes <span>图鉴属性</span></h2><div class="attr-grid">{attr_block(plant)}</div>
      <div class="copy-row"><div class="copy-card"><b>Introduction · 图鉴介绍</b><p>{esc(plant.get("description", ""))}</p><em>{esc(plant.get("description_zh", ""))}</em></div><div class="copy-card"><b>Plant Food · 叶绿素</b><p>{esc(plant.get("plant_food", ""))}</p><em>{esc(plant.get("plant_food_zh", ""))}</em></div></div>
      {f'<div class="feature-row">{specials}</div>' if specials else ''}
      <div class="chat-card"><b>Character story · 角色趣闻</b><span class="chat-en">{esc(plant.get("chat_en", ""))}</span><em>{esc(plant.get("chat_zh", ""))}</em></div>
    </div></div>
</article>'''


def page(group, number, total):
    return f'<section class="page"><div class="plant-grid">{"".join(plant_card(plant) for plant in group)}</div><div class="footer"><span>Data: pvzg_site · Printable A4 portrait demo</span><span class="page-no">{number} / {total}</span></div></section>'


selected = picked()
groups = [selected[index:index + 4] for index in range(0, len(selected), 4)]
OUTPUT.write_text(
    f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    f'<title>PvZ2 Plant Attributes · Demo</title><link rel="preconnect" href="https://fonts.googleapis.com">'
    f'<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@600;700;800&display=swap" rel="stylesheet">'
    f'<style>{CSS}</style></head><body>{"".join(page(group, i + 1, len(groups)) for i, group in enumerate(groups))}</body></html>\n',
    encoding="utf-8",
)
print(f"wrote {OUTPUT} ({len(selected)} plants, 4/page)")
