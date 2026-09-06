#!/usr/bin/env python3
"""Fetch a PvZ2 plant manifest and its artwork for offline use.

The manifest must be a JSON array. Each plant record needs ``file`` and
``img`` fields. A remote manifest can be supplied with ``--data-url``; when
omitted, the checked-in manifest is used and only artwork is refreshed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import re
from urllib.parse import quote, urlencode
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "plants_egypt.json"
DEFAULT_IMAGES = ROOT / "public" / "images"
USER_AGENT = "pvz2-plant-book/1.0 (offline data updater)"
WIKI_API = "https://plantsvszombies.fandom.com/api.php"


def download(url: str, destination: Path, retries: int = 5, pause: float = 1.5) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size >= 100:
        return
    for attempt in range(1, retries + 1):
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=45) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
            if temporary.stat().st_size < 100:
                raise ValueError("response is unexpectedly small")
            os.replace(temporary, destination)
            return
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            temporary.unlink(missing_ok=True)
            if attempt == retries:
                raise RuntimeError(f"download failed after {retries} attempts: {url}\n{error}") from error
            time.sleep(pause * (2 ** (attempt - 1)))


def load_manifest(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list) or not records:
        raise ValueError("plant manifest must be a non-empty JSON array")
    for index, plant in enumerate(records, 1):
        if not isinstance(plant, dict) or not plant.get("file") or not plant.get("img"):
            raise ValueError(f"record {index} needs non-empty 'file' and 'img' fields")
        if Path(plant["file"]).name != plant["file"]:
            raise ValueError(f"unsafe image filename in record {index}: {plant['file']!r}")
    return records


def api_json(params: dict) -> dict:
    url = f"{WIKI_API}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def fetch_wiki_manifest(existing: Path) -> list[dict]:
    """Build a manifest from the current international PvZ2 Wiki plant table."""
    response = api_json({
        "action": "query", "titles": "Plants (PvZ2)", "prop": "revisions",
        "rvprop": "content", "rvslots": "main", "format": "json",
    })
    page = next(iter(response["query"]["pages"].values()))
    source = page["revisions"][0]["slots"]["main"]["*"]
    blocks = re.findall(r"\{\{PvZ2 Plants Resume(.*?)\}\}", source, re.DOTALL)
    wiki_records = {}
    for block in blocks:
        fields = {
            key.strip().lower(): re.sub(r"\s+", " ", value).strip()
            for key, value in re.findall(r"\|\s*([^=]+?)\s*=\s*(.*?)(?=\|\s*[^=]+\s*=|$)", block, re.DOTALL)
        }
        name = fields.get("plant")
        if name:
            wiki_records[name] = fields
    names = list(wiki_records)
    if not names:
        raise ValueError("Wiki plant table returned no plants")

    old = {}
    if existing.exists():
        try:
            old = {item["en"]: item for item in load_manifest(existing)}
        except (OSError, ValueError, json.JSONDecodeError):
            pass

    images = {}
    for start in range(0, len(names), 50):
        batch = names[start:start + 50]
        pages = api_json({
            "action": "query", "titles": "|".join(batch), "prop": "pageimages",
            "piprop": "original|thumbnail", "pithumbsize": 1200, "format": "json",
        })["query"]["pages"].values()
        for page in pages:
            image = page.get("original", {}).get("source") or page.get("thumbnail", {}).get("source")
            if image:
                images[page["title"]] = image

    records = []
    for name in names:
        item = dict(old.get(name, {}))
        wiki = wiki_records[name]
        safe = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "plant"
        item.update({
            "en": name, "zh": item.get("zh", ""), "file": f"{safe}.png",
            "img": images.get(name, item.get("img", "")), "family": item.get("family", "PvZ2"),
            "unlock": wiki.get("price", item.get("unlock", "International edition")),
            "description": wiki.get("description", item.get("description", "")),
            "plant_food": wiki.get("plant food", item.get("plant_food", "")),
            "sun": wiki.get("sun cost", item.get("sun", "—")), "recharge": wiki.get("recharge", item.get("recharge", "—")),
            "recharge_zh": item.get("recharge_zh", ""), "toughness": item.get("toughness", "—"),
            "damage": item.get("damage", "—"), "range": item.get("range", "—"),
            "range_zh": item.get("range_zh", ""), "sentence": item.get("sentence", name),
            "sentence_zh": item.get("sentence_zh", ""), "words": item.get("words", []),
            "color": item.get("color", "#4e9f66"),
        })
        if not item["img"]:
            # Special:FilePath lets the Wiki resolve the current artwork name
            # even when a page has no explicit lead image.
            item["img"] = f"https://plantsvszombies.fandom.com/wiki/Special:FilePath/{quote(name + ' (PvZ2)')}.png"
        records.append(item)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-url", help="URL of the latest plant JSON manifest")
    parser.add_argument("--wiki", action="store_true", help="refresh from the international PvZ2 Wiki plant table")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--images-dir", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--keep-going", action="store_true", help="continue when one image fails")
    parser.add_argument("--delay", type=float, default=1.5, help="seconds to wait between image requests")
    args = parser.parse_args()

    data_file = args.data_file if args.data_file.is_absolute() else ROOT / args.data_file
    if args.wiki and args.data_url:
        parser.error("--wiki and --data-url cannot be used together")
    if args.wiki:
        records = fetch_wiki_manifest(data_file)
        data_file.parent.mkdir(parents=True, exist_ok=True)
        with data_file.open("w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    elif args.data_url:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            download(args.data_url, temporary_path)
            records = load_manifest(temporary_path)
            data_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(temporary_path, data_file)
        finally:
            temporary_path.unlink(missing_ok=True)
    else:
        records = load_manifest(data_file)

    images_dir = args.images_dir if args.images_dir.is_absolute() else ROOT / args.images_dir
    failures = 0
    for number, plant in enumerate(records, 1):
        target = images_dir / plant["file"]
        try:
            download(plant["img"], target)
            print(f"[{number:>3}/{len(records)}] {plant.get('en', plant['file'])}")
        except RuntimeError as error:
            failures += 1
            print(f"ERROR: {error}", file=sys.stderr)
            if not args.keep_going:
                return 1
        time.sleep(max(0, args.delay))

    print(f"Fetched {len(records) - failures}/{len(records)} plant images into {images_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
