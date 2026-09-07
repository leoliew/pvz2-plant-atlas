#!/usr/bin/env python3
"""Rewrite plant learning sentences/words for printable English cards."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "plants_egypt.json"

STOP = set(
    """
    a an the of to and or you it up on in for is at but your other that with from
    its as by into than then when who which this these those be are was were been
    being do does did can lets let have has had will would their them they his her
    him over out back down itself themselves also not no if so too very more most
    all each every both few some any nor because while about after before between
    through during without against among across behind ahead under above once twice
    until unless though although such same own just even still already only
    takes time times much where new left one duty several many entire whole
    helpful un non x object most
    """.split()
)
# Meaningful particles may be target words.
STOP -= {"off", "away"}

SKIP_AS_TARGET = STOP | {"appease", "enforce", "enlighten", "winter", "bombard", "conceal", "enchant", "fila", "contain", "reinforce", "pepper", "spear"}

TOKEN_RE = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")

GLOSSARY = {
    "additional": "额外", "ahead": "前方", "angle": "角度", "area": "范围",
    "arm": "装填", "arming": "装填", "attracts": "吸引", "away": "离开", "balls": "球",
    "barriers": "障碍", "bashes": "猛击", "beats": "打击", "berry": "浆果",
    "blasts": "爆破", "block": "挡住", "blocks": "挡住", "blows": "吹动",
    "bolts": "光束", "boosts": "强化", "bounce": "弹跳", "bouncing": "弹跳",
    "bowling": "保龄", "breathe": "喷出", "buds": "花蕾", "burning": "燃烧",
    "burns": "焚烧", "burst": "爆发", "butter": "黄油", "butters": "涂黄油",
    "cabbages": "卷心菜", "charges": "冲撞", "charms": "魅惑", "chews": "咀嚼",
    "chickens": "小鸡", "chilling": "寒冷", "chills": "冰冻", "click": "点击",
    "coins": "金币", "cold": "寒冷", "contact": "接触", "corn": "玉米",
    "cores": "核心", "creates": "制造", "damage": "伤害", "damages": "伤害",
    "dark": "黑暗", "defeated": "被击败", "defence": "防御", "diagonal": "斜向",
    "dinosaurs": "恐龙", "directions": "方向", "disables": "使失效",
    "dropping": "掉落", "drops": "掉落", "eat": "啃食", "eaten": "被吃",
    "electric": "带电", "electricity": "电", "electrocute": "电击",
    "enemies": "敌人", "energies": "能量", "explodes": "爆炸", "explosive": "爆炸",
    "extra": "额外", "falling": "落下", "farthest": "最远", "fast": "快",
    "fences": "电网", "fight": "对抗", "fights": "对抗", "fire": "火",
    "fireballs": "火球", "fires": "发射", "firm": "牢固", "flame": "火焰",
    "flames": "火焰", "flaming": "燃烧", "flyable": "可飞行", "forth": "向前",
    "forward": "向前", "freeze": "冻结", "freezes": "冻结", "frozen": "冰冻",
    "full": "全力", "fumes": "烟雾", "gas": "气体", "gives": "提供",
    "graves": "墓碑", "ground": "地面", "groups": "成群", "grows": "生长",
    "gum": "口香糖", "heals": "治疗", "heavy": "沉重", "helmets": "头盔",
    "hides": "隐藏", "hits": "击中", "holly": "冬青", "home": "家里",
    "huge": "巨大", "hurls": "投掷", "hypnotizes": "催眠", "icy": "冰冷",
    "illuminates": "照亮", "increases": "增加", "infatuate": "迷惑",
    "invisible": "隐身", "jets": "喷射", "kernels": "玉米粒", "lane": "一行",
    "lanes": "几行", "large": "巨大", "launches": "发射", "lawn": "草坪",
    "leaves": "叶子", "lobs": "投掷", "lobbing": "投掷", "machines": "机器",
    "magical": "魔法", "make": "制造", "makes": "变成", "melee": "近战",
    "medium": "中等", "metal": "金属", "mine": "地雷", "mist": "雾",
    "murk": "暗雾", "nearby": "附近", "obstacles": "障碍", "off": "隔开",
    "pass": "穿过", "pea": "豌豆", "peanuts": "花生", "peas": "豌豆",
    "peppers": "辣椒", "pierces": "穿透", "piercing": "穿透", "planting": "种植",
    "plants": "植物", "poison": "毒素", "poisons": "使中毒", "powered": "供能",
    "powers": "能力", "production": "产量", "projectiles": "弹体",
    "protects": "保护", "pulls": "拉近", "punches": "拳击", "pushes": "推开",
    "quick": "快速", "random": "随机", "randomly": "随机", "range": "范围",
    "rapidly": "快速", "regains": "恢复", "remove": "清除", "removes": "清除",
    "resists": "抵抗", "reveals": "显露", "rhythm": "节奏", "rightward": "右侧",
    "rolls": "滚向", "rush": "冲刺", "scatters": "散开", "seconds": "秒",
    "seed": "种子", "seeds": "种子", "shadow": "暗影", "shooter": "射手",
    "shooters": "射手", "shoots": "发射", "shots": "射击", "slappy": "拍打",
    "slowing": "减速", "small": "小的", "spawning": "生成", "speed": "速度",
    "speeds": "加速", "spend": "花费", "spits": "喷吐", "spore": "孢子",
    "step": "踩到", "sticky": "黏性", "straight": "直线", "strikes": "打击",
    "stronger": "更强", "stunning": "击晕", "sun": "阳光", "suns": "阳光",
    "surrounding": "周围", "surrounds": "包围", "swapped": "对换",
    "targets": "目标", "thorn": "尖刺", "three": "三个", "tile": "格子",
    "tougher": "更坚固", "toughness": "生命", "towards": "朝向",
    "transforms": "变成", "two": "两发", "warms": "温暖", "weaker": "较弱",
    "whips": "抽打", "wind": "风", "zombie": "僵尸", "zombies": "僵尸",
    "zomboids": "小僵尸", "eight": "八个", "butter": "黄油",
    "explodes": "爆炸", "basket": "篮子", "bamboo": "竹子",
    "barrier": "屏障", "creates": "制造", "grows": "生长",
    "hides": "隐藏", "invisible": "隐身", "rolls": "滚动",
    "ball": "球", "charged": "充能", "freezes": "冻结",
    "scatters": "散开", "seeds": "种子", "random": "随机",
    "copies": "复制", "double": "双倍", "four": "四发",
    "glowing": "发光", "tall": "高的", "tough": "坚硬",
    "nut": "坚果", "plant": "植物", "quickly": "快速",
    "adjusts": "调整", "allows": "允许", "along": "沿着",
    "amphibious": "水陆", "aquatic": "水生", "attacking": "进攻",
    "attacks": "攻击", "banana": "香蕉", "board": "滑板",
    "breaks": "打破", "breaths": "吐息", "brings": "带来",
    "cannon": "大炮", "close": "靠近", "conjures": "召唤",
    "crushes": "压碎", "deploys": "部署", "destroys": "摧毁",
    "devours": "吞掉", "digs": "挖掘", "diverts": "引开",
    "drags": "拖走", "drains": "吸走", "drop": "掉落",
    "erupts": "喷发", "flings": "甩出", "flying": "飞行",
    "fogs": "放雾", "food": "养分", "gold": "金色",
    "gourd": "葫芦", "gulps": "吞下", "haunts": "缠绕",
    "heavily": "猛烈", "heavy-duty": "重型", "hp": "生命",
    "hurts": "伤害", "ice": "冰", "laser": "激光",
    "lasts": "持续", "lightning": "闪电", "meteor": "流星",
    "multiple": "多个", "non-aquatic": "陆地", "penetrating": "穿透",
    "pops": "爆开", "power": "能量", "powerful": "强大",
    "produce": "生产", "produces": "生产", "puddles": "水洼",
    "puff-shrooms": "小喷菇", "quick-planting": "快种",
    "rolling": "滚动", "sends": "送出", "shoot": "射击",
    "short-range": "近距", "shrinks": "缩小", "slows": "减速",
    "smacks": "拍打", "snips": "剪断", "snow": "雪",
    "spawns": "生成", "spore-shrooms": "孢子菇", "spot": "位置",
    "squashes": "碾压", "stands": "站立", "stars": "星星",
    "started": "开始", "stuns": "击晕", "sunbomb": "阳光弹",
    "tap": "点击", "target": "目标", "throw": "投掷",
    "thumps": "捶打", "turn": "变成", "turns": "变成",
    "un-flyable": "落地", "wall": "墙", "zaps": "电击",
    "zombies-slowing": "减速", "wall-nut": "坚果墙",
}

SENTENCE_OVERRIDES = {
    "Sunflower": ("Gives extra sun", "提供额外的阳光"),
    "Pumpkin": ("Surrounds plants and protects them", "包围并保护格子里的植物"),
    "Gloom Vine": ("Shoots zombies in eight directions", "向八个方向射击僵尸"),
    "Squash": ("Squashes groups of zombies", "碾压一群僵尸"),
    "Explode-O-Nut": ("Explodes when eaten by zombies", "被僵尸啃食后爆炸"),
    "Pyre Vine": ("Warms plants and shoots flames", "温暖植物并喷出火焰"),
    "Wasabi Whip": ("Whips enemies in both directions", "抽打两个方向的敌人"),
    "Grave Buster": ("Removes graves on the lawn", "清除草坪上的墓碑"),
    "Pea Vine": ("Boosts pea plants nearby", "强化附近的豌豆植物"),
    "Potato Mine": ("Explodes on contact after arming", "装填完成后接触即爆炸"),
    "Potion of Speed": ("Gives extra speed to plants", "让植物获得额外速度"),
    "Potion of Toughness": ("Gives extra toughness to plants", "让植物变得更耐打"),
    "Potion of Invisibility": ("Hides plants from zombies", "让植物对僵尸隐身"),
    "Aquamarine Bowling": ("Rolls a bowling ball at zombies", "把保龄球滚向僵尸"),
    "Blue Bowling": ("Rolls a bowling ball at zombies", "把保龄球滚向僵尸"),
    "Orange Bowling": ("Rolls a bowling ball at zombies", "把保龄球滚向僵尸"),
    "Charged Bowling": ("Rolls a charged ball at zombies", "把充能球滚向僵尸"),
    "Bowling Wall-nut": ("Rolls a tough nut at zombies", "把坚果滚向僵尸"),
    "Bowling Explode-O-Nut": ("Rolls and explodes on zombies", "滚向僵尸并爆炸"),
    "Bowling Infi-nut": ("Rolls a glowing nut at zombies", "把发光坚果滚向僵尸"),
    "Bowling Primal Wall-nut": ("Rolls a tough nut at zombies", "把坚果滚向僵尸"),
    "Iceberg Bowling": ("Rolls and freezes zombies", "滚向僵尸并冻结它们"),
    "Bowling Tall-nut": ("Rolls a tall nut at zombies", "把高坚果滚向僵尸"),
    "Rhythm Phat Beet": ("Beats zombies with rhythm", "跟着节奏打击僵尸"),
    "Bamboo Busket": ("Drops bamboo on zombies", "把竹子砸向僵尸"),
    "Seedling": ("Grows into a random plant", "长成一株随机植物"),
    "Atomic Bombegranate": ("Explodes and scatters seeds", "爆炸并散出种子"),
    "Holly Barrier Leaf": ("Creates a holly barrier", "制造冬青屏障"),
    "Plantfood Holly Barrier Leaf": ("Creates a stronger holly barrier", "制造更强的冬青屏障"),
    "Mega Gatling Pea": ("Fires peas very fast", "快速向僵尸发射豌豆"),
    "Zoybean Pod": ("Grows zomboids that fight zombies", "长出帮你打架的小僵尸"),
    "Murkadamia Nut": ("Powered murk damages zombies", "供能后的暗雾伤害僵尸"),
    "Red Stinger": ("Fires shots close to home", "在靠近家里时全力射击"),
    "Imitater": ("Copies a plant on the lawn", "变成草坪上的另一种植物"),
    "Sun-shroom": ("Gives extra sun as it grows", "长大后提供更多阳光"),
    "Twin Sunflower": ("Gives double sun", "提供双倍阳光"),
    "Gatling Pea": ("Shoots four peas quickly", "快速发射四发豌豆"),
    "Shadow-shroom": ("Poisons nearby zombies", "让附近的僵尸中毒"),
    "Marigold": ("Gives extra coins", "提供额外金币"),
    "Red Marigold": ("Gives extra coins", "提供额外金币"),
    "Orange Marigold": ("Gives extra coins", "提供额外金币"),
    "Yellow Marigold": ("Gives extra coins", "提供额外金币"),
    "Green Marigold": ("Gives extra coins", "提供额外金币"),
    "Blue Marigold": ("Gives extra coins", "提供额外金币"),
    "Pink Marigold": ("Gives extra coins", "提供额外金币"),
    "Purple Marigold": ("Gives extra coins", "提供额外金币"),
}


def norm(text: str) -> str:
    return re.sub(r"[^a-z]+", "", text.lower())


def tokens(sentence: str) -> list[str]:
    return TOKEN_RE.findall(sentence)


def is_full_name(word: str, plant_name: str) -> bool:
    return norm(word) == norm(plant_name)


def pick_words(sentence: str, plant_name: str) -> list[str]:
    chosen: list[str] = []
    seen: set[str] = set()
    for token in tokens(sentence):
        key = token.lower()
        if key in SKIP_AS_TARGET:
            continue
        if is_full_name(token, plant_name):
            continue
        if key in seen:
            continue
        seen.add(key)
        chosen.append(key)
        if len(chosen) == 3:
            break
    return chosen


def translate(word: str) -> str:
    if word in GLOSSARY:
        return GLOSSARY[word]
    if word.endswith("s") and word[:-1] in GLOSSARY:
        return GLOSSARY[word[:-1]]
    if word.endswith("es") and word[:-2] in GLOSSARY:
        return GLOSSARY[word[:-2]]
    raise KeyError(word)


def word_in_sentence(word: str, sentence: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", sentence, flags=re.I) is not None


def main() -> None:
    plants = json.loads(DATA.read_text())
    missing: set[str] = set()
    short: list[str] = []
    for plant in plants:
        name = plant["en"]
        if name in SENTENCE_OVERRIDES:
            sentence, sentence_zh = SENTENCE_OVERRIDES[name]
            plant["sentence"] = sentence
            plant["sentence_zh"] = sentence_zh
        words = pick_words(plant["sentence"], name)
        if len(words) < 3:
            short.append(f"{name}: {plant['sentence']} -> {words}")
        pairs = []
        for word in words:
            try:
                pairs.append([word, translate(word)])
            except KeyError:
                missing.add(word)
                pairs.append([word, "??"])
        plant["words"] = pairs
        plant["learning_sentences"] = [{
            "en": plant["sentence"],
            "zh": plant["sentence_zh"],
            "words": pairs,
        }]

    if missing or short:
        print("SHORT")
        for line in short:
            print(" ", line)
        print("MISSING", sorted(missing))
        raise SystemExit("fix glossary / overrides first")

    for plant in plants:
        assert len(plant["words"]) == 3, plant["en"]
        for en, _zh in plant["words"]:
            assert word_in_sentence(en, plant["sentence"]), (plant["en"], en, plant["sentence"])
            assert en not in STOP, (plant["en"], en)
            assert not is_full_name(en, plant["en"]), (plant["en"], en)

    DATA.write_text(json.dumps(plants, ensure_ascii=False, indent=2) + "\n")
    print(f"rewrote {len(plants)} plants")


if __name__ == "__main__":
    main()
