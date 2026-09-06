# Repository Guidelines

## Project Structure & Module Organization

This repository is a small, data-driven Plants vs. Zombies 2 plant-book generator.

- `plants_egypt.json` is the canonical bilingual plant dataset (names, stats, text, colors, and image URLs).
- `build_html.py` renders the dataset into `PvZ2_Plants_Ancient_Egypt_Demo.html`, a browser-friendly A4 landscape book.
- `build_pdf.py` renders the dataset into `PvZ2_Plants_Ancient_Egypt_Demo.pdf` using ReportLab.
- `images/` may contain local plant artwork referenced by each record's `file` field; HTML falls back to the remote `img` URL.
- `fonts/` may contain local CJK and rounded display fonts used by the PDF builder.

Generated HTML/PDF files are outputs, not primary source files. Keep edits focused on the JSON data or generator scripts.

## Build, Test, and Development Commands

Run commands from the repository root:

```bash
python3 build_html.py   # Rebuild the HTML book
python3 build_pdf.py    # Rebuild the PDF book (requires reportlab)
python3 -m json.tool plants_egypt.json >/dev/null  # Validate JSON syntax
```

Open the generated HTML in a browser to inspect layout. For PDF output, confirm page count, fonts, and local images. There is no package manager, build system, or automated test suite checked in.

## Coding Style & Naming Conventions

Use Python 3, four-space indentation, descriptive `snake_case` names, and small helper functions. Keep markup readable and preserve UTF-8 bilingual text. Use existing JSON keys; image filenames should be lowercase names such as `iceberg_lettuce.png`.

When changing layout, keep HTML and PDF output visually consistent where practical. Avoid hard-coding plant-specific content in either renderer when it belongs in the dataset.

## Testing Guidelines

Before submitting changes, validate JSON, run both generators, and inspect the HTML/PDF. Check representative pages for missing images, clipped text, broken Chinese glyphs, and page numbers. If adding logic, include a reproducible check or documented manual verification step.

## Commit & Pull Request Guidelines

No Git history or remote workflow is present in this directory. Use concise imperative commit subjects (for example, `Add Ancient Egypt plant data`) and keep unrelated generated-output changes separate. Pull requests should describe the change, list validation commands, and include screenshots or rendered samples for visual changes.

## Data and Asset Safety

Treat plant data and external image URLs as inputs. Preserve attribution/source URLs when replacing artwork, avoid embedding secrets, and do not commit large temporary exports or unrelated downloaded assets.
