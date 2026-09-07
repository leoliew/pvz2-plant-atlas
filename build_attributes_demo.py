#!/usr/bin/env python3
"""The attributes almanac is rendered in the browser.

The live page is `PvZ2_Plants_Ancient_Egypt_Attributes.html`, which loads
every plant from `plants_egypt.json` via `src/attributes-book.js`
(4 plants per A4 page) and can export a selected page range to PDF.

Do not overwrite that HTML from here — it is a Vite entry, not generated output.
"""
from __future__ import annotations

print(
    "attributes almanac is Vite-driven: open "
    "/PvZ2_Plants_Ancient_Egypt_Attributes.html after `npm run dev`"
)
