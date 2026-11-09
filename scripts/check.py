#!/usr/bin/env python3
"""Static checks for the Necopolymer site. Usage: python3 scripts/check.py

1. No colour literals outside tokens.css (brand SVGs and the theme-color meta are exempt).
2. Required contact data, copy and section anchors are present in index.html.
3. Every local href/src (and CSS url()) points at a file that exists; sprite fragments exist.
4. Every <img> has an alt attribute.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures = []


def fail(msg):
    failures.append(msg)


# 1. Colour literals -------------------------------------------------------------------------
COLOUR = re.compile(r"(?<![\w\"'/&])#[0-9a-fA-F]{3,8}(?![\w-])|\brgba?\(|\bhsla?\(")
scanned = [ROOT / "assets/css/base.css", ROOT / "assets/css/components.css", ROOT / "index.html", ROOT / "404.html"]
scanned += sorted((ROOT / "assets/js").glob("*.js"))
for path in scanned:
    if not path.exists():
        fail(f"missing file {path.relative_to(ROOT)}")
        continue
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if "theme-color" in line:
            continue
        if COLOUR.search(line):
            fail(f"colour literal in {path.relative_to(ROOT)}:{n}: {line.strip()[:80]}")

# 2. Required content --------------------------------------------------------------------------
index = ROOT / "index.html"
html = index.read_text() if index.exists() else ""
REQUIRED = [
    'href="tel:+37498339349"',
    'href="https://wa.me/37498339349"',
    'href="viber://chat?number=%2B37498339349"',
    'href="https://t.me/+37498339349"',
    'href="mailto:varodjana@gmail.com"',
    'href="https://maps.app.goo.gl/LxYBtuq4fgTTaktv6"',
    "I am Varodjan Abramian, founder and CEO of Necopolymer LLC.",
    "Production Worker",
    "Marketing Specialist",
    "Maintained by Vrej Abramian",
    "Polyethylene terephthalate",
    "High-density polyethylene",
    "Polypropylene",
]
for needle in REQUIRED:
    if needle not in html:
        fail(f"index.html is missing: {needle}")
for section in ["top", "products", "about", "gallery", "contacts", "careers"]:
    if f'id="{section}"' not in html:
        fail(f'index.html has no section id="{section}"')
    if f'class="nav__link" href="#{section}"' not in html:
        fail(f"header nav has no link to #{section}")


# 3 + 4. References and alt text ---------------------------------------------------------------
class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.imgs_without_alt = [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if tag == "img" and "alt" not in a:
            self.imgs_without_alt += 1


def check_local(ref, base, source):
    if re.match(r"^(https?:|mailto:|tel:|viber:|data:|#)", ref):
        return
    path_part, _, fragment = ref.partition("#")
    path_part = path_part.split("?")[0]
    if not path_part:
        return
    target = (ROOT / path_part.lstrip("/")) if path_part.startswith("/") else (base / path_part)
    if not target.resolve().exists():
        fail(f"{source}: broken reference {ref}")
    elif fragment and target.suffix == ".svg" and f'id="{fragment}"' not in target.read_text():
        fail(f"{source}: sprite has no symbol #{fragment}")


for page in ("index.html", "404.html"):
    p = ROOT / page
    if not p.exists():
        continue
    parser = Refs()
    parser.feed(p.read_text())
    for ref in parser.refs:
        check_local(ref, ROOT, page)
    if parser.imgs_without_alt:
        fail(f"{page}: {parser.imgs_without_alt} <img> without alt")

for css in sorted((ROOT / "assets/css").glob("*.css")):
    for ref in re.findall(r"url\(\s*[\"']?([^\"')]+)", css.read_text()):
        check_local(ref, css.parent, css.relative_to(ROOT))

if failures:
    print("\n".join(f"FAIL: {f}" for f in failures))
    print(f"\n{len(failures)} problem(s)")
    sys.exit(1)
print("OK: all checks passed")
