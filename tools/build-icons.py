#!/usr/bin/env python3
"""Regenerate assets/brand/icons.svg, the site's SVG sprite.

UI icons: Lucide (ISC licence). Messenger logos: Simple Icons (CC0). Versions are pinned.
Usage: python3 tools/build-icons.py
"""
import re
import urllib.request
from pathlib import Path

LUCIDE = "https://cdn.jsdelivr.net/npm/lucide-static@1.57.0/icons/{}.svg"
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@16.35.0/icons/{}.svg"
UI = ["sun", "moon", "menu", "x", "arrow-right", "arrow-left", "chevron-down", "phone", "mail",
      "map-pin", "external-link", "briefcase", "recycle", "clock"]
BRANDS = ["whatsapp", "viber", "telegram"]
# The Necopolymer mark: a closing loop (recycling) around a leaf.
MARK = (
    '<symbol id="mark" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M27.5 16A11.5 11.5 0 1 1 22.6 6.6"/>'
    '<path d="M23.4 2.6l-.6 4.3-4.3-.6"/>'
    '<path d="M16 23.5c-4.6-2.6-6-7.6-2.4-12.5 1.4 3 3.9 4.4 7.4 4.6.4 4-1.6 6.6-5 7.9z" '
    'fill="currentColor" stroke="none"/>'
    '<path d="M16 23.5v3"/>'
    '</symbol>'
)
OUT = Path(__file__).resolve().parent.parent / "assets/brand/icons.svg"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "neco-landing-page"})
    with urllib.request.urlopen(request) as response:
        return response.read().decode()


def inner(svg):
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    body = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    return re.sub(r"<title>.*?</title>", "", body, flags=re.S).strip()


parts = [MARK]
for name in UI:
    parts.append(
        f'<symbol id="{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner(fetch(LUCIDE.format(name)))}</symbol>'
    )
for name in BRANDS:
    parts.append(f'<symbol id="{name}" viewBox="0 0 24 24" fill="currentColor">{inner(fetch(SIMPLE.format(name)))}</symbol>')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text('<svg xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(parts) + "\n</svg>\n")
print(f"wrote {OUT.relative_to(OUT.parents[2])} with {len(parts)} symbols")
