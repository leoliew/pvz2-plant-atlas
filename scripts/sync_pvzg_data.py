#!/usr/bin/env python3
"""Sync the plant catalog and artwork from a local pvzg_site checkout."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


WORLD_NAMES = {
    "frontyard": ("Player's House", "玩家小屋"),
    "egypt": ("Ancient Egypt", "古埃及"),
    "pirate": ("Pirate Seas", "海盗海"),
    "cowboy": ("Wild West", "狂野西部"),
    "ice": ("Frostbite Caves", "冰冻洞穴"),
    "lostcity": ("Lost City", "失落之城"),
    "future": ("Far Future", "遥远未来"),
    "dark": ("Dark Ages", "黑暗时代"),
    "dino": ("Jurassic Marsh", "侏罗纪沼泽"),
    "beach": ("Big Wave Beach", "巨浪海滩"),
    "modern": ("Modern Day", "现代世界"),
    "mint": ("Mint family", "薄荷家族"),
    "epic": ("Premium & special", "特殊与高级"),
    "market": ("Premium & special", "特殊与高级"),
    "lod": ("Premium & special", "特殊与高级"),
    "water": ("Premium & special", "特殊与高级"),
    "kongfu": ("Premium & special", "特殊与高级"),
    "eighties": ("Premium & special", "特殊与高级"),
    "sky": ("Premium & special", "特殊与高级"),
    "": ("Premium & special", "特殊与高级"),
}

# Code -> almanac background filename (mirrors WORLD_NAMES' code keys and
# src/world-backgrounds.js on the JS side). Unmapped or empty codes fall
# back to "default" at copy time.
WORLD_BACKGROUND_FILES = {
    "beach": "beach", "boost": "boost", "cowboy": "cowboy", "dark": "dark", "dino": "dino",
    "egypt": "egypt", "eighties": "eighties", "epic": "epic", "frontyard": "frontyard",
    "future": "future", "ice": "iceage", "kongfu": "kongfu", "lod": "lod", "lostcity": "lostcity",
    "market": "market", "mint": "mint", "modern": "modern", "pirate": "pirate", "sky": "sky",
    "water": "beach_watered",
}

FAMILY_NAMES = {
    "Defence": ("Reinforce-mint", "防御家族"), "Shadow": ("Conceal-mint", "暗影家族"),
    "Peashooter": ("Appease-mint", "豌豆家族"), "Fire": ("Pepper-mint", "燃烧家族"),
    "Cold": ("Winter-mint", "寒冰家族"), "Sharp": ("Spear-mint", "锋利家族"),
    "Lobber": ("Arma-mint", "投掷家族"), "Poison": ("Ail-mint", "毒性家族"),
    "Electricity": ("Fila-mint", "电能家族"), "Slow": ("Contain-mint", "滞缓家族"),
    "Magic": ("Enchant-mint", "魔法家族"), "Sun": ("Enlighten-mint", "阳光家族"),
    "Melee": ("Enforce-mint", "健壮家族"), "Explosive": ("Bombard-mint", "爆裂家族"),
    "None": ("None", "无"),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def localized(value, language, fallback=""):
    if isinstance(value, dict):
        return value.get(language) or value.get("en") or fallback
    return value or fallback


def safe_file(codename: str) -> str:
    return f"{re.sub(r'[^a-z0-9]+', '_', codename.lower()).strip('_')}.png"


def words_for(name: str, sentence: str, zh_name: str):
    translations = {
        "shoot": "发射", "shoots": "发射", "fire": "攻击", "fires": "攻击",
        "give": "提供", "gives": "提供", "create": "创造", "creates": "创造",
        "grow": "生长", "grows": "生长", "damage": "伤害", "slow": "减速",
        "slows": "减速", "explode": "爆炸", "explodes": "爆炸", "zombies": "僵尸",
        "zombie": "僵尸", "plant": "植物", "plants": "植物", "peas": "豌豆",
    }
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]+", name)]
    tokens += [t.lower() for t in re.findall(r"[A-Za-z]+", sentence)]
    seen = []
    for token in tokens + ["plant", "zombie"]:
        if token not in seen:
            seen.append(token)
        if len(seen) == 3:
            break
    zh_parts = [part for part in re.findall(r"[\u4e00-\u9fff]{1,4}", zh_name)]
    name_tokens = {t.lower() for t in re.findall(r"[A-Za-z]+", name)}
    return [[token, translations.get(token, zh_name if token in name_tokens else "植物")] for token in seen]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path, help="pvzg_site checkout")
    parser.add_argument("--output", type=Path, default=Path("plants_egypt.json"))
    parser.add_argument("--images", type=Path, default=Path("public/images"))
    args = parser.parse_args()
    root = args.reference
    features = load(root / "src/components/game-data/raw/Features/PlantFeatures.json")
    almanac = {item["aliases"][0]: item["objdata"] for item in load(root / "src/components/game-data/raw/Objects/PlantAlmanac.json")["objects"] if item.get("aliases")}
    props = {item["aliases"][0]: item["objdata"] for item in load(root / "src/components/game-data/raw/Objects/PlantProps.json")["objects"] if item.get("aliases")}
    old = {item["en"]: item for item in load(args.output)} if args.output.exists() else {}
    records = []
    for origin in features["PLANTS"]:
        code = origin["CODENAME"]
        name = origin["NAME"]["en"]
        zh_name = origin["NAME"].get("zh") or old.get(name, {}).get("zh") or name
        p = props.get(code, {})
        a = almanac.get(code, {})
        elements = {e.get("TYPE"): e for e in a.get("Elements", [])}
        family_en, family_zh = FAMILY_NAMES.get(p.get("Family"), (p.get("Family", "None"), "无"))
        world_en, world_zh = WORLD_NAMES.get(origin.get("OBTAINWORLD", ""), WORLD_NAMES[""])
        intro_en = localized(a.get("Introduction"), "en", old.get(name, {}).get("description", "")) or f"{name} is a helpful plant that fights zombies."
        intro_zh = localized(a.get("Introduction"), "zh", "") or f"{zh_name}是一种帮助你对抗僵尸的植物。"
        brief_en = localized(a.get("BriefIntroduction"), "en", intro_en)
        brief_zh = localized(a.get("BriefIntroduction"), "zh", intro_zh)
        sentence_en = brief_en or f"{name} helps you fight zombies!"
        sentence_zh = brief_zh or f"{zh_name}帮助你对付僵尸！"
        range_value = elements.get("RANGE", {}).get("SORT", {}).get("en") or old.get(name, {}).get("range", "Special ability")
        range_zh = elements.get("RANGE", {}).get("SORT", {}).get("zh") or old.get(name, {}).get("range_zh", "特殊能力") or "特殊能力"
        plant_food_element = elements.get("PLANTFOOD", {}).get("SORT", {})
        plant_food_en = localized(a.get("PlantFood"), "en", "") or plant_food_element.get("en") or old.get(name, {}).get("plant_food", "") or "No Plant Food effect."
        plant_food_zh = localized(a.get("PlantFood"), "zh", "") or plant_food_element.get("zh") or old.get(name, {}).get("plant_food_zh", "没有叶绿素效果。")
        record = {
            **old.get(name, {}), "id": origin["ID"], "codename": code, "en": name, "zh": zh_name, "file": old.get(name, {}).get("file", safe_file(code)),
            "pvzg_file": f"plants_{code}_c.webp", "img": old.get(name, {}).get("img", ""),
            "sun": str(elements.get("SUNCOST", {}).get("VALUE", p.get("SunCost", "—"))),
            "recharge": str(elements.get("RECHARGE", {}).get("VALUE", p.get("Cooldown", "—"))),
            "recharge_zh": "快" if float(p.get("Cooldown", 99) or 99) <= 10 else "慢",
            "toughness": elements.get("TOUGHNESS", {}).get("VALUE", p.get("Toughness", "—")),
            "damage": elements.get("DAMAGE", {}).get("VALUE", old.get(name, {}).get("damage", "—")),
            "range": range_value, "range_zh": range_zh, "family": family_en,
            "family_zh": family_zh, "unlock": old.get(name, {}).get("unlock", "International edition"),
            "unlock_zh": f"{world_zh}植物", "sentence": sentence_en, "sentence_zh": sentence_zh,
            "words": words_for(name, sentence_en, zh_name), "color": old.get(name, {}).get("color", "#4e9f66"),
            "description": intro_en, "description_zh": intro_zh, "intro_en": intro_en, "intro_zh": intro_zh,
            "plant_food": plant_food_en, "plant_food_zh": plant_food_zh, "world": world_en,
            "obtain_world_code": origin.get("OBTAINWORLD", ""),
            "learning_sentences": [{"en": sentence_en, "zh": sentence_zh, "words": words_for(name, sentence_en, zh_name)}],
        }
        records.append(record)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_dir = root / "src/.vuepress/public/assets/image/plants"
    args.images.mkdir(parents=True, exist_ok=True)
    copied = 0
    for image in source_dir.glob("*.webp"):
        target = args.images / image.name
        if not target.exists() or target.stat().st_size != image.stat().st_size:
            shutil.copy2(image, target)
            copied += 1

    bg_source_dir = root / "src/.vuepress/public/assets/image/almanac/backgrounds"
    bg_target_dir = args.images / "backgrounds"
    bg_target_dir.mkdir(parents=True, exist_ok=True)
    bg_copied = 0
    for image in bg_source_dir.glob("*.webp"):
        target = bg_target_dir / image.name
        if not target.exists() or target.stat().st_size != image.stat().st_size:
            shutil.copy2(image, target)
            bg_copied += 1

    print(f"synced {len(records)} plants, {copied} artwork files, and {bg_copied} world backgrounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
