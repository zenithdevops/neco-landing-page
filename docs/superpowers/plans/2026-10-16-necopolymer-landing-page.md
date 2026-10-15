# Necopolymer Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a single-page, cinematic business-card site for Necopolymer LLC on GitHub Pages.

**Architecture:** Hand-written static HTML/CSS/JS with no build step. All design values are custom
properties in `assets/css/tokens.css`; text lives in `index.html`; four small vanilla JS files add
behaviour. A Python stdlib script (`scripts/check.py`) is the test suite.

**Tech Stack:** HTML5, CSS (custom properties, `light-dark()`, `@property`), vanilla ES2020,
Python 3 stdlib (checks + icon sprite), ImageMagick + cwebp (one-off image prep), `gh` CLI.

**Spec:** `docs/superpowers/specs/2026-10-16-necopolymer-landing-page-design.md`

## Global Constraints

- No npm, no bundler, no framework, no GitHub Actions. Pages serves `main` from `/`.
- Colour literals only in `assets/css/tokens.css` and `assets/brand/*` (plus the `theme-color` meta).
- All asset paths in `index.html` are **relative** (`assets/...`) so the preview sub-path works.
- Text is in HTML, never injected by JS.
- Every motion effect is disabled under `prefers-reduced-motion: reduce`.
- Git identity is repo-local `vrejabramian <237103231+vrejabramian@users.noreply.github.com>`; `gh` account `vrejabramian`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Pinned third-party assets: `@fontsource-variable/sora@5.3.0`, `@fontsource-variable/inter@5.3.0`, `lucide-static@1.57.0`, `simple-icons@16.35.0`.
- Contact data (exact): phone `+37498886456` (display `+374 98 886456`), email `varodjana@gmail.com`,
  address "Hangar No. 2, 22nd Street, Ptghni, Kotayk Province, Armenia", map `https://maps.app.goo.gl/LxYBtuq4fgTTaktv6`.

Paths below are relative to the repo root `/Users/vrej/myProjects/TEMP/varodjan-necopolymer/neco-landing-page`.
`$SRC` = `/Users/vrej/myProjects/TEMP/varodjan-necopolymer/temp.ignore` (owner photos).
`$STOCK` = `/private/tmp/claude-501/-Users-vrej-myProjects-TEMP-varodjan-necopolymer-temp-ignore/1fcc53d1-0e15-415a-8347-36bc8e80c720/scratchpad/stock` (downloaded CC0 photos).

---

### Task 1: Repo scaffolding and the check script (the failing test)

**Files:**
- Create: `.gitignore`, `.nojekyll`, `scripts/check.py`

**Interfaces:**
- Produces: `python3 scripts/check.py` exits 0 when the site is valid, 1 with `FAIL:` lines otherwise. Later tasks run it.

- [ ] **Step 1: Write `.gitignore` and `.nojekyll`**

<!-- file: .gitignore -->
```gitignore
.DS_Store
*.tmp
*.ignore/
.idea/
.vscode/
node_modules/
```

`.nojekyll` is an empty file (stops Pages running Jekyll).

- [ ] **Step 2: Write the check script**

<!-- file: scripts/check.py -->
```python
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
    'href="tel:+37498886456"',
    'href="https://wa.me/37498886456"',
    'href="viber://chat?number=%2B37498886456"',
    'href="https://t.me/+37498886456"',
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
```

- [ ] **Step 3: Run it and confirm it fails**

Run: `python3 scripts/check.py`
Expected: exit 1, with `FAIL: missing file assets/css/base.css` and missing-content lines.

- [ ] **Step 4: Commit**

```bash
git add .gitignore .nojekyll scripts/check.py
git commit -m "Add repo scaffolding and static site checks"
```

---

### Task 2: Assets: fonts, icon sprite, brand marks, images

**Files:**
- Create: `assets/fonts/sora-latin-wght.woff2`, `assets/fonts/inter-latin-wght.woff2`
- Create: `tools/build-icons.py`, `assets/brand/icons.svg` (generated), `assets/brand/favicon.svg`, `assets/brand/og-image.jpg`
- Create: `assets/img/hero/hero.webp`, `assets/img/products/{pet,hdpe,pp}.webp`, `assets/img/about/varodjan-abramian.webp`, `assets/img/gallery/{varodjan-yerevan,hangar}.webp`

**Interfaces:**
- Produces: sprite symbol ids `mark sun moon menu x arrow-right arrow-left chevron-down phone mail map-pin external-link briefcase recycle clock whatsapp viber telegram`, used as `<use href="assets/brand/icons.svg#ID">`. Font files are referenced by `base.css` (Task 3).

- [ ] **Step 1: Download the fonts**

```bash
mkdir -p assets/fonts
curl -sfL -o assets/fonts/sora-latin-wght.woff2 https://cdn.jsdelivr.net/npm/@fontsource-variable/sora@5.3.0/files/sora-latin-wght-normal.woff2
curl -sfL -o assets/fonts/inter-latin-wght.woff2 https://cdn.jsdelivr.net/npm/@fontsource-variable/inter@5.3.0/files/inter-latin-wght-normal.woff2
file assets/fonts/*.woff2
```
Expected: both reported as `Web Open Font Format (Version 2)`.

- [ ] **Step 2: Write the sprite builder and run it**

<!-- file: tools/build-icons.py -->
```python
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
```

Run: `python3 tools/build-icons.py`
Expected: `wrote assets/brand/icons.svg with 18 symbols`

- [ ] **Step 3: Write the favicon**

<!-- file: assets/brand/favicon.svg -->
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="8" fill="#0A1A13"/>
  <g transform="translate(3.2 3.2) scale(.8)" fill="none" stroke="#B5E655" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M27.5 16A11.5 11.5 0 1 1 22.6 6.6"/>
    <path d="M23.4 2.6l-.6 4.3-4.3-.6"/>
    <path d="M16 23.5c-4.6-2.6-6-7.6-2.4-12.5 1.4 3 3.9 4.4 7.4 4.6.4 4-1.6 6.6-5 7.9z" fill="#B5E655" stroke="none"/>
    <path d="M16 23.5v3"/>
  </g>
</svg>
```

- [ ] **Step 4: Produce the images**

```bash
mkdir -p assets/img/{hero,products,about,gallery}
web() { # $1 src, $2 dest, $3 quality, rest = magick ops
  local src=$1 dest=$2 q=$3; shift 3
  magick "$src" -auto-orient "$@" -strip /tmp/neco-img.png
  cwebp -quiet -q "$q" /tmp/neco-img.png -o "$dest"
  echo "$dest $(magick identify -format '%wx%h %b' "$dest")"
}
web "$STOCK/b_pile.jpg"       assets/img/hero/hero.webp         70
web "$STOCK/a_finnish.jpg"    assets/img/products/pet.webp      78 -resize 900x600^ -gravity center -extent 900x600
web "$STOCK/d_sorting.jpg"    assets/img/products/hdpe.webp     78 -resize 900x600^ -gravity center -extent 900x600
web "$STOCK/g_caps.jpg"       assets/img/products/pp.webp       78 -resize 900x600^ -gravity center -extent 900x600
web "$SRC/Prof0.jpg"          assets/img/about/varodjan-abramian.webp 82 -gravity north -crop 693x693+27+0 +repage -resize 640x640
web "$SRC/pic1.jpg"           assets/img/gallery/varodjan-yerevan.webp 78 -resize 1600x
# pic2: crop the bottom 120px to remove the "REDMI NOTE 9S" camera watermark
web "$SRC/pic2.jpg"           assets/img/gallery/hangar.webp    78 -crop 1440x960+0+0 +repage
magick "$STOCK/b_pile.jpg" -resize 1200x630^ -gravity center -extent 1200x630 \
  \( -size 1200x630 gradient:'rgba(6,18,13,0.35)-rgba(6,18,13,0.92)' \) -composite \
  -font /System/Library/Fonts/Supplemental/Arial\ Bold.ttf -fill '#EAF4EE' -pointsize 84 -gravity southwest -annotate +64+150 'NECOPOLYMER' \
  -font /System/Library/Fonts/Supplemental/Arial.ttf -fill '#B5E655' -pointsize 40 -annotate +68+90 'Giving plastic a second life.' \
  -strip -quality 82 assets/brand/og-image.jpg
```
Expected: 7 `.webp` lines with the stated sizes; `pet/hdpe/pp` are `900x600`, the portrait `640x640`, hangar `1440x960`.
Then open `assets/img/gallery/hangar.webp` and confirm the watermark is gone.

- [ ] **Step 5: Commit**

```bash
git add assets tools
git commit -m "Add fonts, icon sprite, brand marks and optimized images"
```

---

### Task 3: Design tokens and base styles

**Files:**
- Create: `assets/css/tokens.css`, `assets/css/base.css`

**Interfaces:**
- Produces (used by Task 4): tokens `--c-*`, `--g-*`, `--font-*`, `--fs-*`, `--sp-1..8`, `--radius*`, `--dur*`, `--ease`, `--header-h*`, `--film-*`; classes `.container .section .section--alt .section__head .section__title .section__lead .eyebrow .text-gradient .icon .icon--sm .icon--lg .btn .btn--primary .btn--accent .btn--ghost .skip-link .visually-hidden`; `[data-reveal]` + `.is-visible`; `html.js` gate.

- [ ] **Step 1: Write the tokens**

<!-- file: assets/css/tokens.css -->
```css
/* ==========================================================================
   Necopolymer design tokens: THE place to restyle the site.
   Every colour, font, size, radius and duration lives here. Other CSS files
   hold no colour literals (enforced by scripts/check.py).
   Scheme-dependent colours are declared once as light-dark(LIGHT, DARK).
   ========================================================================== */
:root {
  color-scheme: light dark;

  /* ---- Palette: page ---- */
  --c-bg:            light-dark(#F3F7F4, #0A1A13);
  --c-bg-alt:        light-dark(#E8F0EB, #0D2119);
  --c-surface:       light-dark(#FFFFFF, #12281E);
  --c-border:        light-dark(#D3E3D9, #23443A);
  --c-text:          light-dark(#0F2419, #EAF4EE);
  --c-text-muted:    light-dark(#4B6458, #A3BCAF);
  --c-primary:       light-dark(#18744C, #1F8A5B);
  --c-primary-hover: light-dark(#125E3D, #27A56D);
  --c-on-primary:    #FFFFFF;
  --c-accent:        light-dark(#4F7D0E, #B5E655);
  --c-accent-2:      light-dark(#167C95, #5CC8E0);
  --c-on-accent:     #0A1A13;
  --c-cta-bg:        light-dark(#18744C, #15603F);
  --c-focus:         light-dark(#167C95, #5CC8E0);
  --c-shadow:        light-dark(rgb(15 36 25 / 0.16), rgb(0 0 0 / 0.5));
  --c-grad-1:        light-dark(#18744C, #B5E655);
  --c-grad-2:        light-dark(#167C95, #5CC8E0);
  --c-header:        light-dark(rgb(243 247 244 / 0.72), rgb(10 26 19 / 0.6));
  --c-header-solid:  light-dark(rgb(243 247 244 / 0.96), rgb(10 26 19 / 0.94));

  /* ---- Palette: always-dark surfaces (hero, film strip, lightbox, footer) ---- */
  --c-hero-text:        #F2FAF5;
  --c-hero-muted:       #C5DBCF;
  --c-hero-grad-1:      #B5E655;
  --c-hero-grad-2:      #5CC8E0;
  --c-hero-chip:        rgb(255 255 255 / 0.08);
  --c-hero-chip-border: rgb(255 255 255 / 0.24);
  --c-film:             #0C110E;
  --c-film-hole:        #EDE6D3;
  --c-film-text:        #D9E6DE;
  --c-scrim:            rgb(4 10 7 / 0.9);

  /* ---- Messenger brand colours ---- */
  --c-whatsapp: #25D366;
  --c-viber:    #7360F2;
  --c-telegram: #26A5E4;

  /* ---- Gradients ---- */
  --g-hero:
    linear-gradient(180deg, rgb(6 18 13 / 0.7) 0%, rgb(6 18 13 / 0.3) 35%, rgb(6 18 13 / 0.6) 70%, rgb(6 18 13 / 0.92) 100%),
    radial-gradient(120% 80% at 10% 60%, rgb(31 138 91 / 0.4), transparent 60%);
  --g-glow: radial-gradient(70% 50% at 50% 0%, light-dark(rgb(31 138 91 / 0.1), rgb(31 138 91 / 0.2)), transparent 70%);

  /* ---- Typography ---- */
  --font-display: "Sora", ui-sans-serif, system-ui, sans-serif;
  --font-body:    "Inter", ui-sans-serif, system-ui, sans-serif;
  --fs-hero:    clamp(2.75rem, 1.2rem + 6.5vw, 6.75rem);
  --fs-h2:      clamp(2rem, 1.2rem + 3vw, 3.5rem);
  --fs-h3:      clamp(1.2rem, 1.05rem + 0.5vw, 1.45rem);
  --fs-lead:    clamp(1.08rem, 1rem + 0.4vw, 1.3rem);
  --fs-body:    1.0625rem;
  --fs-small:   0.9rem;
  --fs-eyebrow: 0.78rem;
  --fs-brand:   1.1rem;
  --lh-tight:   1.04;
  --lh-heading: 1.15;
  --lh-body:    1.65;
  --tracking-tight:   -0.03em;
  --tracking-eyebrow: 0.18em;
  --tracking-brand:   0.12em;

  /* ---- Space & layout ---- */
  --sp-1: 0.25rem; --sp-2: 0.5rem; --sp-3: 0.75rem; --sp-4: 1rem;
  --sp-5: 1.5rem;  --sp-6: 2rem;   --sp-7: 3rem;    --sp-8: 4.5rem;
  --section-pad: clamp(4.5rem, 3rem + 7vw, 9rem);
  --container: 1200px;
  --container-narrow: 760px;
  --gutter: clamp(1rem, 0.5rem + 3vw, 2rem);
  --header-h: 76px;
  --header-h-scrolled: 62px;
  --line: 2px;
  --border-w: 1px;

  /* ---- Shape & depth ---- */
  --radius-sm: 10px;
  --radius: 18px;
  --radius-lg: 28px;
  --radius-pill: 999px;
  --shadow-card: 0 24px 60px -28px var(--c-shadow);
  --blur: 16px;

  /* ---- Icons & controls ---- */
  --icon-sm: 1.1rem;
  --icon: 1.35rem;
  --icon-lg: 1.75rem;
  --control: 42px;
  --badge: 64px;

  /* ---- Motion ---- */
  --dur-fast: 180ms;
  --dur: 420ms;
  --dur-slow: 900ms;
  --dur-kenburns: 26s;
  --dur-ring: 12s;
  --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
  --reveal-shift: 28px;
  --reveal-stagger: 90ms;

  /* ---- Film strip ---- */
  --film-frame-h: clamp(220px, 40vw, 420px);
  --film-edge: 30px;
  --film-hole-h: 10px;
  --film-hole-w: 16px;
  --film-gap: 14px;
}

/* Explicit choice from the theme toggle (saved in localStorage as "neco-theme"). */
:root[data-theme="light"] { color-scheme: light; }
:root[data-theme="dark"]  { color-scheme: dark; }
```

- [ ] **Step 2: Write the base styles**

<!-- file: assets/css/base.css -->
```css
/* Base: fonts, reset, layout primitives, typography, buttons, reveal. Values come from tokens.css. */
@font-face {
  font-family: "Sora";
  src: url("../fonts/sora-latin-wght.woff2") format("woff2");
  font-weight: 100 800;
  font-display: swap;
}
@font-face {
  font-family: "Inter";
  src: url("../fonts/inter-latin-wght.woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}

*, *::before, *::after { box-sizing: border-box; }
* { margin: 0; }
html { scroll-behavior: smooth; scroll-padding-top: var(--header-h-scrolled); -webkit-text-size-adjust: 100%; }
body {
  background: var(--c-bg);
  color: var(--c-text);
  font-family: var(--font-body);
  font-size: var(--fs-body);
  line-height: var(--lh-body);
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}
img, svg { display: block; max-width: 100%; }
img { height: auto; }
a { color: inherit; text-decoration: none; }
button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }
ul { list-style: none; padding: 0; }
h1, h2, h3 { font-family: var(--font-display); font-weight: 700; line-height: var(--lh-heading); letter-spacing: var(--tracking-tight); }
:focus-visible { outline: var(--line) solid var(--c-focus); outline-offset: 3px; border-radius: var(--radius-sm); }
::selection { background: var(--c-primary); color: var(--c-on-primary); }

.skip-link {
  position: absolute; left: var(--sp-4); top: calc(-1 * var(--header-h)); z-index: 100;
  padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm);
  background: var(--c-primary); color: var(--c-on-primary);
}
.skip-link:focus { top: var(--sp-4); }
.visually-hidden {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}

/* ---- Layout ---- */
.container { width: min(100% - 2 * var(--gutter), var(--container)); margin-inline: auto; }
.section { position: relative; padding-block: var(--section-pad); }
.section--alt { background-color: var(--c-bg-alt); }
.section__head { max-width: var(--container-narrow); margin-bottom: var(--sp-7); }
.section__title { font-size: var(--fs-h2); }
.section__lead { margin-top: var(--sp-4); font-size: var(--fs-lead); color: var(--c-text-muted); }
.eyebrow {
  display: inline-flex; align-items: center; gap: var(--sp-2); margin-bottom: var(--sp-4);
  font-size: var(--fs-eyebrow); font-weight: 600; letter-spacing: var(--tracking-eyebrow); text-transform: uppercase;
  color: var(--c-accent);
}
.eyebrow::before { content: ""; width: var(--sp-6); height: var(--line); background: currentColor; }
.text-gradient {
  background-image: linear-gradient(90deg, var(--c-grad-1), var(--c-grad-2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}

/* ---- Icons ---- */
.icon { width: var(--icon); height: var(--icon); flex: none; }
.icon--sm { width: var(--icon-sm); height: var(--icon-sm); }
.icon--lg { width: var(--icon-lg); height: var(--icon-lg); }

/* ---- Buttons ---- */
.btn {
  display: inline-flex; align-items: center; gap: var(--sp-2);
  padding: var(--sp-3) var(--sp-5); border: var(--border-w) solid transparent; border-radius: var(--radius-pill);
  font-weight: 600;
  transition: transform var(--dur-fast) var(--ease), background-color var(--dur-fast) var(--ease),
              border-color var(--dur-fast) var(--ease), color var(--dur-fast) var(--ease);
}
.btn:hover { transform: translateY(-2px); }
.btn--primary { background: var(--c-primary); color: var(--c-on-primary); }
.btn--primary:hover { background: var(--c-primary-hover); }
.btn--accent { background: var(--c-accent); color: var(--c-on-accent); }
.btn--ghost { border-color: var(--c-border); color: var(--c-text); }
.btn--ghost:hover { border-color: var(--c-accent); color: var(--c-accent); }

/* ---- Reveal on scroll: hidden only while html.js is set, so no-JS visitors see everything ---- */
.js [data-reveal] {
  opacity: 0; transform: translateY(var(--reveal-shift));
  transition: opacity var(--dur-slow) var(--ease), transform var(--dur-slow) var(--ease);
  transition-delay: calc(var(--d, 0) * var(--reveal-stagger));
}
.js [data-reveal].is-visible { opacity: 1; transform: none; }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; transition-delay: 0s !important;
  }
  .js [data-reveal] { opacity: 1; transform: none; }
}
```

- [ ] **Step 3: Run the check**

Run: `python3 scripts/check.py`
Expected: still FAIL (no `components.css`, `index.html`), but **no** `colour literal` lines for `base.css`.

- [ ] **Step 4: Commit**

```bash
git add assets/css
git commit -m "Add design tokens and base styles"
```

---

### Task 4: Page markup and component styles

**Files:**
- Create: `index.html`, `assets/css/components.css`

**Interfaces:**
- Consumes: Task 3 classes/tokens; Task 2 sprite ids and image paths.
- Produces (used by Task 5 JS): `[data-header]`, `.nav__link` (href `#id`), `[data-nav-toggle]` (contains `<use>`), `[data-theme-toggle]` (contains `<use>`), `html.nav-open`, `.site-header.is-scrolled`, `[data-film]` with `.film__track`, `[data-film-prev]`, `[data-film-next]`, `.film__open` (button, optional `data-full`), `[data-lightbox]` (`<dialog>` with `img`, `figcaption`, `[data-lightbox-close]`), `[data-reveal]`.

- [ ] **Step 1: Write `index.html`**

<!-- file: index.html -->
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Necopolymer | PET, HDPE &amp; PP Plastic Recycling in Armenia</title>
  <meta name="description" content="Necopolymer LLC recycles PET, HDPE and polypropylene in Kotayk Province, near Yerevan, Armenia. Call +374 98 886456.">
  <link rel="canonical" href="https://necopolymer.com/">
  <meta name="theme-color" content="#0A1A13">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Necopolymer">
  <meta property="og:title" content="Necopolymer: giving plastic a second life">
  <meta property="og:description" content="PET, HDPE and polypropylene recycling in Armenia.">
  <meta property="og:url" content="https://necopolymer.com/">
  <meta property="og:image" content="https://necopolymer.com/assets/brand/og-image.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/brand/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="assets/fonts/sora-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/inter-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/img/hero/hero.webp" as="image" fetchpriority="high">
  <link rel="stylesheet" href="assets/css/tokens.css">
  <link rel="stylesheet" href="assets/css/base.css">
  <link rel="stylesheet" href="assets/css/components.css">
  <script>
    // Inline on purpose: must run before first paint (no theme flash, no reveal flash).
    document.documentElement.classList.add('js');
    try {
      var saved = localStorage.getItem('neco-theme');
      if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
    } catch (e) {}
  </script>
  <script src="assets/js/theme.js" defer></script>
  <script src="assets/js/nav.js" defer></script>
  <script src="assets/js/reveal.js" defer></script>
  <script src="assets/js/gallery.js" defer></script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Necopolymer LLC",
    "description": "PET, HDPE and polypropylene plastic recycling in Armenia.",
    "url": "https://necopolymer.com/",
    "image": "https://necopolymer.com/assets/brand/og-image.jpg",
    "telephone": "+37498886456",
    "email": "varodjana@gmail.com",
    "founder": { "@type": "Person", "name": "Varodjan Abramian" },
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "22nd Street, Hangar No. 2",
      "addressLocality": "Ptghni",
      "addressRegion": "Kotayk Province",
      "addressCountry": "AM"
    },
    "hasMap": "https://maps.app.goo.gl/LxYBtuq4fgTTaktv6"
  }
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header" data-header>
    <div class="container header__inner">
      <a class="brand" href="#top" aria-label="Necopolymer, back to top">
        <svg class="brand__mark" aria-hidden="true"><use href="assets/brand/icons.svg#mark"></use></svg>
        <span>NECOPOLYMER</span>
      </a>
      <nav class="nav" aria-label="Main">
        <ul class="nav__list" id="nav-list">
          <li><a class="nav__link" href="#top">Home</a></li>
          <li><a class="nav__link" href="#products">Products</a></li>
          <li><a class="nav__link" href="#about">About</a></li>
          <li><a class="nav__link" href="#gallery">Gallery</a></li>
          <li><a class="nav__link" href="#contacts">Contacts</a></li>
          <li><a class="nav__link" href="#careers">Careers</a></li>
        </ul>
        <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-label="Switch to light theme">
          <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#sun"></use></svg>
        </button>
        <button class="icon-btn nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="nav-list" aria-label="Open menu">
          <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#menu"></use></svg>
        </button>
      </nav>
    </div>
  </header>

  <main id="main">
    <!-- ============ HOME ============ -->
    <section class="hero" id="top" aria-labelledby="hero-title">
      <img class="hero__media" src="assets/img/hero/hero.webp" alt="" width="1024" height="768" fetchpriority="high">
      <div class="hero__overlay" aria-hidden="true"></div>
      <div class="container">
        <div class="hero__content">
          <p class="eyebrow hero__eyebrow" data-reveal>Plastic recycling · Yerevan, Armenia</p>
          <h1 class="hero__title" id="hero-title" data-reveal style="--d:1">Giving plastic <span class="text-gradient">a second life.</span></h1>
          <p class="hero__lead" data-reveal style="--d:2">PET, HDPE and polypropylene recycling in Armenia. We turn post-consumer plastic into clean, reusable raw material for industry.</p>
          <div class="hero__actions" data-reveal style="--d:3">
            <a class="btn btn--accent" href="#contacts">Contact us
              <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#arrow-right"></use></svg></a>
            <a class="btn btn--ghost" href="#products">Our products</a>
          </div>
          <ul class="hero__chips" data-reveal style="--d:4" aria-label="Materials we recycle">
            <li class="chip"><span class="chip__code">01</span>PET</li>
            <li class="chip"><span class="chip__code">02</span>HDPE</li>
            <li class="chip"><span class="chip__code">05</span>PP</li>
          </ul>
        </div>
      </div>
      <a class="hero__scroll" href="#products" aria-label="Scroll to products">
        <span>Scroll</span>
        <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#chevron-down"></use></svg>
      </a>
    </section>

    <!-- ============ PRODUCTS ============ -->
    <section class="section products" id="products" aria-labelledby="products-title">
      <div class="container">
        <header class="section__head" data-reveal>
          <p class="eyebrow">Products</p>
          <h2 class="section__title" id="products-title">Three polymers. <span class="text-gradient">One purpose.</span></h2>
          <p class="section__lead">We specialise in the three plastics that matter most in everyday packaging, and return them to the production cycle.</p>
        </header>
        <div class="product-grid">
          <article class="product-card" data-reveal>
            <div class="product-card__media">
              <img src="assets/img/products/pet.webp" alt="Clear PET drinking bottles marked with resin code 1" width="900" height="600" loading="lazy">
              <span class="resin-badge" role="img" aria-label="Resin identification code 1">
                <svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#recycle"></use></svg>
                <span class="resin-badge__num" aria-hidden="true">1</span>
              </span>
            </div>
            <div class="product-card__body">
              <h3><span class="product-card__abbr">PET</span><span class="product-card__name">Polyethylene terephthalate</span></h3>
              <p class="product-card__text">Clear, strong and fully recyclable. We collect and process PET bottles and packaging into clean material ready for a new production cycle.</p>
              <ul class="tags" aria-label="Typical sources">
                <li class="tag">Beverage bottles</li><li class="tag">Food containers</li><li class="tag">Packaging</li>
              </ul>
            </div>
          </article>
          <article class="product-card" data-reveal style="--d:1">
            <div class="product-card__media">
              <img src="assets/img/products/hdpe.webp" alt="Used HDPE milk and detergent jugs at a recycling yard" width="900" height="600" loading="lazy">
              <span class="resin-badge" role="img" aria-label="Resin identification code 2">
                <svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#recycle"></use></svg>
                <span class="resin-badge__num" aria-hidden="true">2</span>
              </span>
            </div>
            <div class="product-card__body">
              <h3><span class="product-card__abbr">HDPE</span><span class="product-card__name">High-density polyethylene</span></h3>
              <p class="product-card__text">Tough and chemical-resistant. Rigid HDPE is sorted, shredded and prepared for reuse in pipes, containers and household goods.</p>
              <ul class="tags" aria-label="Typical sources">
                <li class="tag">Milk &amp; detergent bottles</li><li class="tag">Canisters</li><li class="tag">Crates</li>
              </ul>
            </div>
          </article>
          <article class="product-card" data-reveal style="--d:2">
            <div class="product-card__media">
              <img src="assets/img/products/pp.webp" alt="Colourful polypropylene bottle caps" width="900" height="600" loading="lazy">
              <span class="resin-badge" role="img" aria-label="Resin identification code 5">
                <svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#recycle"></use></svg>
                <span class="resin-badge__num" aria-hidden="true">5</span>
              </span>
            </div>
            <div class="product-card__body">
              <h3><span class="product-card__abbr">PP</span><span class="product-card__name">Polypropylene</span></h3>
              <p class="product-card__text">Lightweight and heat-resistant. We recover polypropylene from caps, tubs and industrial parts and return it to manufacturing.</p>
              <ul class="tags" aria-label="Typical sources">
                <li class="tag">Bottle caps</li><li class="tag">Food tubs</li><li class="tag">Industrial parts</li>
              </ul>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ============ ABOUT ============ -->
    <section class="section section--alt about" id="about" aria-labelledby="about-title">
      <div class="container about__grid">
        <div class="portrait" data-reveal>
          <img src="assets/img/about/varodjan-abramian.webp" alt="Portrait of Varodjan Abramian, founder and CEO of Necopolymer LLC" width="640" height="640" loading="lazy">
        </div>
        <div class="about__text" data-reveal style="--d:1">
          <p class="eyebrow">About</p>
          <h2 class="section__title" id="about-title">Waste is a <span class="text-gradient">resource.</span></h2>
          <p class="about__quote">I am Varodjan Abramian, founder and CEO of Necopolymer LLC.</p>
          <p>For years I have worked to keep plastic out of Armenia's landfills and return it to industry as a valuable raw material.</p>
          <p>At Necopolymer we collect, sort and process PET, HDPE and polypropylene at our facility in Kotayk Province, just outside Yerevan.</p>
          <p>Our goal is simple: a cleaner country, and dependable recycled material for the businesses that build it.</p>
          <div class="signature">
            <svg class="brand__mark" aria-hidden="true"><use href="assets/brand/icons.svg#mark"></use></svg>
            <div><strong>Varodjan Abramian</strong><span>Founder &amp; CEO, Necopolymer LLC</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ GALLERY ============ -->
    <section class="section gallery" id="gallery" aria-labelledby="gallery-title">
      <div class="container">
        <header class="section__head" data-reveal>
          <p class="eyebrow">Gallery</p>
          <h2 class="section__title" id="gallery-title">Inside <span class="text-gradient">Necopolymer.</span></h2>
          <p class="section__lead">Our people and our facility. Drag, swipe or use the arrows, and select a frame to enlarge it.</p>
        </header>
        <div class="film" data-film data-reveal>
          <button class="film__nav film__nav--prev" type="button" data-film-prev aria-label="Previous photos">
            <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#arrow-left"></use></svg>
          </button>
          <div class="film__track" role="region" aria-label="Photo strip" tabindex="0">
            <figure class="film__frame">
              <button class="film__open" type="button" aria-label="Enlarge photo: Varodjan Abramian in Yerevan">
                <img src="assets/img/gallery/varodjan-yerevan.webp" alt="Varodjan Abramian standing in front of his recycling billboard in Yerevan" width="1600" height="901" loading="lazy" draggable="false">
              </button>
              <figcaption>Varodjan Abramian in Yerevan</figcaption>
            </figure>
            <figure class="film__frame">
              <button class="film__open" type="button" aria-label="Enlarge photo: inside our processing hangar">
                <img src="assets/img/gallery/hangar.webp" alt="Recycling equipment and bulk bags of plastic inside the Necopolymer hangar" width="1440" height="960" loading="lazy" draggable="false">
              </button>
              <figcaption>Inside our processing hangar, Kotayk</figcaption>
            </figure>
          </div>
          <button class="film__nav film__nav--next" type="button" data-film-next aria-label="Next photos">
            <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#arrow-right"></use></svg>
          </button>
        </div>
      </div>
    </section>

    <!-- ============ CONTACTS ============ -->
    <section class="section section--alt contacts" id="contacts" aria-labelledby="contacts-title">
      <div class="container">
        <header class="section__head" data-reveal>
          <p class="eyebrow">Contacts</p>
          <h2 class="section__title" id="contacts-title">Let's talk <span class="text-gradient">recycling.</span></h2>
          <p class="section__lead">Whether you have plastic to supply or need recycled material, we'd be glad to hear from you.</p>
        </header>
        <div class="contact-grid">
          <article class="contact-card" data-reveal>
            <span class="contact-card__icon"><svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#phone"></use></svg></span>
            <h3 class="contact-card__label">Phone</h3>
            <a class="contact-card__value" href="tel:+37498886456">+374 98 886456</a>
            <p class="contact-card__note">Also available on WhatsApp, Viber and Telegram:</p>
            <div class="messengers">
              <a class="messenger messenger--whatsapp" href="https://wa.me/37498886456" target="_blank" rel="noopener" aria-label="Chat on WhatsApp" title="WhatsApp">
                <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#whatsapp"></use></svg></a>
              <a class="messenger messenger--viber" href="viber://chat?number=%2B37498886456" aria-label="Chat on Viber" title="Viber">
                <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#viber"></use></svg></a>
              <a class="messenger messenger--telegram" href="https://t.me/+37498886456" target="_blank" rel="noopener" aria-label="Chat on Telegram" title="Telegram">
                <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#telegram"></use></svg></a>
            </div>
          </article>
          <article class="contact-card" data-reveal style="--d:1">
            <span class="contact-card__icon"><svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#mail"></use></svg></span>
            <h3 class="contact-card__label">Email</h3>
            <a class="contact-card__value" href="mailto:varodjana@gmail.com">varodjana@gmail.com</a>
            <p class="contact-card__note">For enquiries, partnerships and quotes.</p>
            <a class="link-arrow" href="mailto:varodjana@gmail.com">Write to us
              <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#arrow-right"></use></svg></a>
          </article>
          <article class="contact-card" data-reveal style="--d:2">
            <span class="contact-card__icon"><svg class="icon" aria-hidden="true"><use href="assets/brand/icons.svg#map-pin"></use></svg></span>
            <h3 class="contact-card__label">Address</h3>
            <p class="contact-card__value">Hangar No. 2, 22nd Street</p>
            <p class="contact-card__note">Ptghni, Kotayk Province, Armenia</p>
            <a class="link-arrow" href="https://maps.app.goo.gl/LxYBtuq4fgTTaktv6" target="_blank" rel="noopener">Open in Google Maps
              <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#external-link"></use></svg></a>
          </article>
        </div>
      </div>
    </section>

    <!-- ============ CAREERS ============ -->
    <section class="section careers" id="careers" aria-labelledby="careers-title">
      <div class="container">
        <header class="section__head" data-reveal>
          <p class="eyebrow">Careers</p>
          <h2 class="section__title" id="careers-title">Grow <span class="text-gradient">with us.</span></h2>
          <p class="section__lead">We are building a team that takes pride in doing things properly. Open positions:</p>
        </header>
        <div class="job-grid">
          <article class="job-card" data-reveal>
            <ul class="job-card__meta"><li class="tag">Operations</li><li class="tag">Ptghni, Kotayk</li></ul>
            <h3 class="job-card__title">Production Worker</h3>
            <p>Hands-on work sorting, shredding and processing recyclable plastic at our facility. Training is provided.</p>
          </article>
          <article class="job-card" data-reveal style="--d:1">
            <ul class="job-card__meta"><li class="tag">Marketing</li><li class="tag">Yerevan region</li></ul>
            <h3 class="job-card__title">Marketing Specialist</h3>
            <p>Help us tell the Necopolymer story, build relationships with suppliers and buyers, and grow our presence online.</p>
          </article>
        </div>
        <div class="careers__cta" data-reveal>
          <div>
            <h3>Interested? Please contact us.</h3>
            <p>Call or email us and tell us a little about yourself.</p>
          </div>
          <div class="careers__actions">
            <a class="btn btn--light" href="tel:+37498886456">
              <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#phone"></use></svg>Call us</a>
            <a class="btn btn--outline-light" href="mailto:varodjana@gmail.com?subject=Job%20application">
              <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#mail"></use></svg>Email us</a>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <a class="brand" href="#top">
            <svg class="brand__mark" aria-hidden="true"><use href="assets/brand/icons.svg#mark"></use></svg>
            <span>NECOPOLYMER</span>
          </a>
          <p>PET, HDPE and polypropylene recycling in Armenia. Giving plastic a second life.</p>
        </div>
        <div>
          <h2 class="footer__title">Explore</h2>
          <ul class="footer__list">
            <li><a href="#products">Products</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#gallery">Gallery</a></li>
            <li><a href="#contacts">Contacts</a></li>
            <li><a href="#careers">Careers</a></li>
          </ul>
        </div>
        <div>
          <h2 class="footer__title">Contact</h2>
          <ul class="footer__list">
            <li><a href="tel:+37498886456"><svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#phone"></use></svg>+374 98 886456</a></li>
            <li><a href="mailto:varodjana@gmail.com"><svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#mail"></use></svg>varodjana@gmail.com</a></li>
            <li><a href="https://maps.app.goo.gl/LxYBtuq4fgTTaktv6" target="_blank" rel="noopener"><svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#map-pin"></use></svg>Hangar No. 2, 22nd Street, Ptghni, Kotayk Province, Armenia</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p>© 2026 Necopolymer LLC. All rights reserved.</p>
        <p class="footer__credit">Maintained by Vrej Abramian</p>
      </div>
    </div>
  </footer>

  <dialog class="lightbox" data-lightbox aria-label="Photo viewer">
    <button class="icon-btn lightbox__close" type="button" data-lightbox-close aria-label="Close photo">
      <svg class="icon icon--sm" aria-hidden="true"><use href="assets/brand/icons.svg#x"></use></svg>
    </button>
    <figure class="lightbox__figure">
      <img class="lightbox__img" alt="">
      <figcaption class="lightbox__caption"></figcaption>
    </figure>
  </dialog>
</body>
</html>
```

- [ ] **Step 2: Write `components.css`**

<!-- file: assets/css/components.css -->
```css
/* Components, in page order. Values come from tokens.css. */

/* ================= Header ================= */
/* The glass background lives on ::before so the header itself does not become a containing
   block for the fixed-position mobile menu (backdrop-filter would do that). */
.site-header {
  position: fixed; inset: 0 0 auto 0; z-index: 50;
  height: var(--header-h); display: flex; align-items: center;
  transition: height var(--dur) var(--ease), color var(--dur) var(--ease);
}
.site-header::before {
  content: ""; position: absolute; inset: 0; z-index: -1;
  background: var(--c-header);
  -webkit-backdrop-filter: blur(var(--blur)) saturate(1.4); backdrop-filter: blur(var(--blur)) saturate(1.4);
  border-bottom: var(--border-w) solid var(--c-border);
  transition: opacity var(--dur) var(--ease), background-color var(--dur) var(--ease);
}
.site-header.is-scrolled { height: var(--header-h-scrolled); }
.site-header.is-scrolled::before { background: var(--c-header-solid); }
.header__inner { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-5); }

.brand {
  display: inline-flex; align-items: center; gap: var(--sp-3);
  font-family: var(--font-display); font-size: var(--fs-brand); font-weight: 700; letter-spacing: var(--tracking-brand);
}
.brand__mark { width: var(--icon-lg); height: var(--icon-lg); color: var(--c-accent); }

.nav { display: flex; align-items: center; gap: var(--sp-2); }
.nav__list { display: flex; gap: var(--sp-1); margin-right: var(--sp-2); }
.nav__link {
  position: relative; display: block; padding: var(--sp-2) var(--sp-3);
  font-size: var(--fs-small); font-weight: 500; opacity: 0.8;
  transition: opacity var(--dur-fast) var(--ease);
}
.nav__link::after {
  content: ""; position: absolute; left: var(--sp-3); right: var(--sp-3); bottom: var(--sp-1);
  height: var(--line); border-radius: var(--radius-pill); background: var(--c-accent);
  transform: scaleX(0); transform-origin: left; transition: transform var(--dur) var(--ease);
}
.nav__link:hover, .nav__link.is-active { opacity: 1; }
.nav__link:hover::after, .nav__link.is-active::after { transform: scaleX(1); }

.icon-btn {
  display: inline-grid; place-items: center; width: var(--control); height: var(--control);
  border: var(--border-w) solid var(--c-border); border-radius: var(--radius-pill);
  transition: border-color var(--dur-fast) var(--ease), color var(--dur-fast) var(--ease);
}
.icon-btn:hover { border-color: var(--c-accent); color: var(--c-accent); }
.theme-toggle, .nav-toggle { display: none; }
.js .theme-toggle { display: inline-grid; }

/* Transparent over the hero until the visitor scrolls (only when JS can add .is-scrolled). */
.js .site-header:not(.is-scrolled) { color: var(--c-hero-text); }
.js .site-header:not(.is-scrolled)::before { opacity: 0; }
.js .site-header:not(.is-scrolled) .brand__mark,
.js .site-header:not(.is-scrolled) .icon-btn:hover { color: var(--c-hero-grad-1); }
.js .site-header:not(.is-scrolled) .nav__link::after { background: var(--c-hero-grad-1); }
.js .site-header:not(.is-scrolled) .icon-btn { border-color: var(--c-hero-chip-border); }

@media (max-width: 900px) {
  .js .nav-toggle { display: inline-grid; }
  .nav__list {
    position: fixed; inset: 0; z-index: -1; margin: 0;
    flex-direction: column; justify-content: center; align-items: center; gap: var(--sp-3);
    background: var(--c-header-solid);
    -webkit-backdrop-filter: blur(var(--blur)); backdrop-filter: blur(var(--blur));
    opacity: 0; visibility: hidden;
    transition: opacity var(--dur) var(--ease), visibility var(--dur);
  }
  .nav__link { font-family: var(--font-display); font-size: var(--fs-h3); }
  .nav-open .nav__list { opacity: 1; visibility: visible; }
  .nav-open body { overflow: hidden; }
  .js.nav-open .site-header { color: var(--c-text); }
  .js.nav-open .site-header .brand__mark { color: var(--c-accent); }
  .js.nav-open .site-header .icon-btn { border-color: var(--c-border); }
}
/* Without JS the menu cannot open, so keep the links visible and scrollable instead. */
@media (max-width: 900px) {
  html:not(.js) .nav__list {
    position: static; flex-direction: row; overflow-x: auto; opacity: 1; visibility: visible;
    background: none; -webkit-backdrop-filter: none; backdrop-filter: none; z-index: auto;
  }
  html:not(.js) .nav__link { font-size: var(--fs-small); }
}

/* ================= Hero ================= */
.hero {
  position: relative; isolation: isolate; overflow: hidden;
  min-height: 100svh; display: grid; align-items: center;
  padding-block: calc(var(--header-h) + var(--sp-7)) var(--sp-8);
  background: var(--c-film); color: var(--c-hero-text);
}
.hero__media {
  position: absolute; inset: 0; z-index: -2; width: 100%; height: 100%; object-fit: cover;
  transform-origin: 60% 40%; animation: kenburns var(--dur-kenburns) ease-in-out infinite alternate;
}
.hero__overlay { position: absolute; inset: 0; z-index: -1; background: var(--g-hero); }
@keyframes kenburns {
  from { transform: scale(1.05); }
  to   { transform: scale(1.2) translate3d(-2%, -1.5%, 0); }
}
.hero__content { max-width: 880px; }
.hero__eyebrow { color: var(--c-hero-grad-1); }
.hero__title { font-size: var(--fs-hero); line-height: var(--lh-tight); }
.hero__title .text-gradient { background-image: linear-gradient(90deg, var(--c-hero-grad-1), var(--c-hero-grad-2)); }
.hero__lead { margin-top: var(--sp-5); max-width: 36rem; font-size: var(--fs-lead); color: var(--c-hero-muted); }
.hero__actions { margin-top: var(--sp-6); display: flex; flex-wrap: wrap; gap: var(--sp-3); }
.hero .btn--accent { background: var(--c-hero-grad-1); }
.hero .btn--ghost { border-color: var(--c-hero-chip-border); color: var(--c-hero-text); }
.hero .btn--ghost:hover { border-color: var(--c-hero-grad-1); color: var(--c-hero-grad-1); }
.hero__chips { margin-top: var(--sp-7); display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.chip {
  display: inline-flex; align-items: center; gap: var(--sp-2); padding: var(--sp-1) var(--sp-4);
  border: var(--border-w) solid var(--c-hero-chip-border); border-radius: var(--radius-pill);
  background: var(--c-hero-chip); font-size: var(--fs-small); font-weight: 600;
}
.chip__code { font-family: var(--font-display); color: var(--c-hero-grad-1); }
.hero__scroll {
  position: absolute; left: 50%; bottom: var(--sp-5); translate: -50% 0;
  display: grid; justify-items: center; gap: var(--sp-1);
  font-size: var(--fs-eyebrow); letter-spacing: var(--tracking-eyebrow); text-transform: uppercase; color: var(--c-hero-muted);
}
.hero__scroll .icon { animation: bob 2.2s var(--ease) infinite; }
@keyframes bob { 50% { transform: translateY(6px); } }
@media (max-height: 640px) { .hero__scroll { display: none; } }

/* ================= Products ================= */
.products { background-image: var(--g-glow); }
.product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: var(--sp-5); }
.product-card {
  display: flex; flex-direction: column; overflow: hidden;
  background: var(--c-surface); border: var(--border-w) solid var(--c-border); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.product-card:hover { transform: translateY(-6px); border-color: var(--c-primary); }
.product-card__media { position: relative; aspect-ratio: 3 / 2; overflow: hidden; background: var(--c-bg-alt); }
.product-card__media img { width: 100%; height: 100%; object-fit: cover; transition: transform var(--dur-slow) var(--ease); }
.product-card:hover .product-card__media img { transform: scale(1.06); }
.resin-badge {
  position: absolute; top: var(--sp-4); left: var(--sp-4);
  display: grid; place-items: center; width: var(--badge); height: var(--badge);
  border: var(--border-w) solid var(--c-hero-chip-border); border-radius: var(--radius-pill);
  background: var(--c-scrim); color: var(--c-hero-grad-1);
}
.resin-badge > * { grid-area: 1 / 1; }
.resin-badge .icon { width: 70%; height: 70%; }
.resin-badge__num { font-family: var(--font-display); font-size: var(--fs-small); font-weight: 700; color: var(--c-hero-text); translate: 0 1px; }
.product-card__body { display: grid; gap: var(--sp-3); padding: var(--sp-5) var(--sp-5) var(--sp-6); }
.product-card__abbr { display: block; font-size: var(--fs-h2); line-height: 1; color: var(--c-accent); }
.product-card__name {
  display: block; margin-top: var(--sp-2);
  font-family: var(--font-body); font-size: var(--fs-small); font-weight: 600; letter-spacing: var(--tracking-eyebrow);
  text-transform: uppercase; color: var(--c-text-muted);
}
.product-card__text { color: var(--c-text-muted); }
.tags { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.tag {
  padding: var(--sp-1) var(--sp-3); border: var(--border-w) solid var(--c-border); border-radius: var(--radius-pill);
  background: var(--c-bg-alt); font-size: var(--fs-small);
}

/* ================= About ================= */
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
@keyframes ring { to { --angle: 360deg; } }
.about__grid { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: var(--sp-8); align-items: center; }
.portrait { position: relative; justify-self: center; width: 100%; max-width: 440px; }
.portrait::before {
  content: ""; position: absolute; inset: calc(-1 * var(--sp-2)); border-radius: calc(var(--radius-lg) + var(--sp-2));
  background: conic-gradient(from var(--angle), var(--c-grad-1), var(--c-grad-2), var(--c-primary), var(--c-grad-1));
  animation: ring var(--dur-ring) linear infinite;
}
.portrait img { position: relative; width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: var(--radius-lg); }
.about__text .section__title { margin-bottom: var(--sp-5); }
.about__text p { color: var(--c-text-muted); }
.about__text p + p { margin-top: var(--sp-4); }
.about__text .about__quote { font-family: var(--font-display); font-size: var(--fs-h3); line-height: var(--lh-heading); color: var(--c-text); }
.signature { display: flex; align-items: center; gap: var(--sp-3); margin-top: var(--sp-6); }
.signature strong { display: block; font-family: var(--font-display); }
.signature span { font-size: var(--fs-small); color: var(--c-text-muted); }
@media (max-width: 860px) { .about__grid { grid-template-columns: 1fr; gap: var(--sp-7); } }

/* ================= Gallery: film strip ================= */
.film {
  position: relative; padding-block: var(--film-edge);
  background: var(--c-film); color: var(--c-film-text); border-radius: var(--radius); box-shadow: var(--shadow-card);
}
.film::before, .film::after {
  content: ""; position: absolute; left: var(--film-gap); right: var(--film-gap); height: var(--film-hole-h);
  background: repeating-linear-gradient(90deg, var(--c-film-hole) 0 var(--film-hole-w), transparent var(--film-hole-w) calc(2 * var(--film-hole-w)));
  opacity: 0.85; pointer-events: none;
}
.film::before { top: calc((var(--film-edge) - var(--film-hole-h)) / 2); }
.film::after { bottom: calc((var(--film-edge) - var(--film-hole-h)) / 2); }
.film__track {
  display: flex; gap: var(--film-gap); padding-inline: var(--film-gap);
  overflow-x: auto; scroll-snap-type: x mandatory; overscroll-behavior-x: contain;
  scrollbar-width: none; cursor: grab;
}
.film__track::-webkit-scrollbar { display: none; }
.film__track.is-dragging { cursor: grabbing; scroll-snap-type: none; }
.film__frame { position: relative; flex: none; height: var(--film-frame-h); overflow: hidden; border-radius: var(--radius-sm); scroll-snap-align: center; }
.film__open { display: block; height: 100%; padding: 0; }
.film__open img {
  width: auto; height: 100%; max-width: none; user-select: none; -webkit-user-drag: none;
  filter: grayscale(0.3) contrast(1.05);
  transition: transform var(--dur-slow) var(--ease), filter var(--dur) var(--ease);
}
.film__frame:hover img, .film__open:focus-visible img { transform: scale(1.04); filter: none; }
.film__frame figcaption {
  position: absolute; inset: auto 0 0 0; padding: var(--sp-6) var(--sp-4) var(--sp-3);
  background: linear-gradient(transparent, var(--c-scrim)); font-size: var(--fs-small); pointer-events: none;
}
.film__nav {
  position: absolute; top: 50%; translate: 0 -50%; z-index: 2;
  display: grid; place-items: center; width: var(--control); height: var(--control);
  border: var(--border-w) solid var(--c-hero-chip-border); border-radius: var(--radius-pill);
  background: var(--c-scrim); color: var(--c-film-text);
  transition: opacity var(--dur-fast) var(--ease), color var(--dur-fast) var(--ease);
}
.film__nav:hover { color: var(--c-hero-grad-1); }
.film__nav[disabled] { opacity: 0; pointer-events: none; }
.film__nav--prev { left: var(--sp-3); }
.film__nav--next { right: var(--sp-3); }
html:not(.js) .film__nav { display: none; }

.lightbox {
  width: 100vw; height: 100vh; max-width: 100vw; max-height: 100vh; padding: 0; border: 0;
  background: transparent; color: var(--c-film-text);
}
.lightbox[open] { display: grid; place-items: center; }
.lightbox::backdrop { background: var(--c-scrim); }
.lightbox__figure { display: grid; justify-items: center; gap: var(--sp-3); }
.lightbox__img { width: auto; max-width: 92vw; max-height: 84vh; border-radius: var(--radius-sm); box-shadow: var(--shadow-card); }
.lightbox__caption { font-size: var(--fs-small); text-align: center; }
.lightbox__close { position: fixed; top: var(--sp-4); right: var(--sp-4); border-color: var(--c-hero-chip-border); }

/* ================= Contacts ================= */
.contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr)); gap: var(--sp-5); }
.contact-card {
  display: flex; flex-direction: column; align-items: flex-start; gap: var(--sp-3); padding: var(--sp-6);
  background: var(--c-surface); border: var(--border-w) solid var(--c-border); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.contact-card:hover { transform: translateY(-4px); border-color: var(--c-primary); }
.contact-card__icon {
  display: grid; place-items: center; width: var(--badge); height: var(--badge); margin-bottom: var(--sp-2);
  border: var(--border-w) solid var(--c-border); border-radius: var(--radius); background: var(--c-bg-alt); color: var(--c-accent);
}
.contact-card__label {
  font-family: var(--font-body); font-size: var(--fs-eyebrow); font-weight: 600;
  letter-spacing: var(--tracking-eyebrow); text-transform: uppercase; color: var(--c-text-muted);
}
.contact-card__value { font-family: var(--font-display); font-size: var(--fs-h3); font-weight: 600; overflow-wrap: anywhere; }
a.contact-card__value:hover { color: var(--c-accent); }
.contact-card__note { font-size: var(--fs-small); color: var(--c-text-muted); }
.messengers { display: flex; gap: var(--sp-2); margin-top: auto; }
.messenger {
  display: grid; place-items: center; width: var(--control); height: var(--control); border-radius: var(--radius-pill);
  color: var(--c-on-primary); transition: transform var(--dur-fast) var(--ease);
}
.messenger:hover { transform: translateY(-2px) scale(1.06); }
.messenger--whatsapp { background: var(--c-whatsapp); }
.messenger--viber { background: var(--c-viber); }
.messenger--telegram { background: var(--c-telegram); }
.link-arrow { display: inline-flex; align-items: center; gap: var(--sp-2); margin-top: auto; font-weight: 600; color: var(--c-accent); }
.link-arrow .icon { transition: transform var(--dur-fast) var(--ease); }
.link-arrow:hover .icon { transform: translateX(4px); }

/* ================= Careers ================= */
.careers { background-image: var(--g-glow); }
.job-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: var(--sp-5); }
.job-card {
  position: relative; overflow: hidden; display: grid; align-content: start; gap: var(--sp-3); padding: var(--sp-6);
  background: var(--c-surface); border: var(--border-w) solid var(--c-border); border-radius: var(--radius-lg);
}
.job-card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: var(--sp-1); background: linear-gradient(var(--c-grad-1), var(--c-grad-2)); }
.job-card__meta { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.job-card__title { font-size: var(--fs-h3); }
.job-card p { color: var(--c-text-muted); }
.careers__cta {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--sp-5);
  margin-top: var(--sp-7); padding: var(--sp-6); border-radius: var(--radius-lg);
  background: var(--c-cta-bg); color: var(--c-on-primary);
}
.careers__cta h3 { font-size: var(--fs-h3); }
.careers__cta p { margin-top: var(--sp-1); opacity: 0.88; }
.careers__actions { display: flex; flex-wrap: wrap; gap: var(--sp-3); }
.btn--light { background: var(--c-on-primary); color: var(--c-cta-bg); }
.btn--outline-light { border-color: currentColor; color: inherit; }

/* ================= Footer (always dark) ================= */
.site-footer { padding-block: var(--sp-8) var(--sp-5); background: var(--c-film); color: var(--c-film-text); }
.site-footer .brand__mark { color: var(--c-hero-grad-1); }
.footer__grid { display: grid; grid-template-columns: 2fr 1fr 1.6fr; gap: var(--sp-7); }
.footer__brand p { max-width: 22rem; margin-top: var(--sp-4); color: var(--c-hero-muted); }
.footer__title {
  margin-bottom: var(--sp-4); font-size: var(--fs-small); letter-spacing: var(--tracking-eyebrow);
  text-transform: uppercase; color: var(--c-hero-grad-1);
}
.footer__list { display: grid; gap: var(--sp-2); }
.footer__list a { display: inline-flex; align-items: flex-start; gap: var(--sp-2); color: var(--c-hero-muted); transition: color var(--dur-fast) var(--ease); }
.footer__list a:hover { color: var(--c-hero-text); }
.footer__list .icon { margin-top: var(--sp-1); }
.footer__bottom {
  display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--sp-3);
  margin-top: var(--sp-7); padding-top: var(--sp-5); border-top: var(--border-w) solid var(--c-hero-chip-border);
  font-size: var(--fs-small); color: var(--c-hero-muted);
}
.footer__credit { opacity: 0.75; }
@media (max-width: 760px) { .footer__grid { grid-template-columns: 1fr; gap: var(--sp-6); } }

/* ================= 404 ================= */
.notfound { min-height: 100svh; display: grid; place-content: center; justify-items: start; gap: var(--sp-4); }
```

- [ ] **Step 3: Run the check**

Run: `python3 scripts/check.py`
Expected: only `missing file assets/js/...` / `404.html` failures remain.

- [ ] **Step 4: Commit**

```bash
git add index.html assets/css/components.css
git commit -m "Build the single-page layout and component styles"
```

---

### Task 5: Behaviour (JS)

**Files:**
- Create: `assets/js/theme.js`, `assets/js/nav.js`, `assets/js/reveal.js`, `assets/js/gallery.js`

**Interfaces:**
- Consumes: hooks listed in Task 4 "Produces". localStorage key `neco-theme` (`"light"|"dark"`), shared with the inline `<head>` snippet.

- [ ] **Step 1: Write the four scripts**

<!-- file: assets/js/theme.js -->
```js
// Dark/light toggle. The inline <head> snippet applies a saved choice before paint; this file
// only runs the button. No colour is touched here: data-theme flips color-scheme in tokens.css.
(() => {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  if (!button) return;
  const icon = button.querySelector('use');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)');
  const current = () => root.dataset.theme || (prefersLight.matches ? 'light' : 'dark');

  const render = () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    button.setAttribute('aria-label', `Switch to ${next} theme`);
    icon.setAttribute('href', `assets/brand/icons.svg#${next === 'light' ? 'sun' : 'moon'}`);
  };

  button.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('neco-theme', next); } catch (e) { /* storage blocked: lasts this visit */ }
    render();
  });
  prefersLight.addEventListener('change', render);
  render();
})();
```

<!-- file: assets/js/nav.js -->
```js
// Header: solid after scrolling, active-section highlight, and the mobile menu.
(() => {
  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('[data-nav-toggle]');
  const links = [...document.querySelectorAll('.nav__link')];

  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const linkFor = new Map(links.map((link) => [link.getAttribute('href').slice(1), link]));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((link) => { link.classList.remove('is-active'); link.removeAttribute('aria-current'); });
      const active = linkFor.get(entry.target.id);
      if (active) { active.classList.add('is-active'); active.setAttribute('aria-current', 'location'); }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  linkFor.forEach((_, id) => { const section = document.getElementById(id); if (section) observer.observe(section); });

  const setOpen = (open) => {
    root.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    toggle.querySelector('use').setAttribute('href', `assets/brand/icons.svg#${open ? 'x' : 'menu'}`);
  };
  toggle.addEventListener('click', () => setOpen(!root.classList.contains('nav-open')));
  links.forEach((link) => link.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setOpen(false); });
  window.matchMedia('(min-width: 901px)').addEventListener('change', (event) => { if (event.matches) setOpen(false); });
})();
```

<!-- file: assets/js/reveal.js -->
```js
// Fade-up on scroll for [data-reveal]. Elements are hidden only while html.js is set (base.css),
// and reduced-motion visitors get everything immediately.
(() => {
  const items = document.querySelectorAll('[data-reveal]');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  items.forEach((el) => observer.observe(el));
})();
```

<!-- file: assets/js/gallery.js -->
```js
// Film-strip gallery: arrow buttons, mouse drag-to-scroll (touch scrolls natively), and a
// <dialog> lightbox. Esc closing comes free with showModal().
(() => {
  const film = document.querySelector('[data-film]');
  const dialog = document.querySelector('[data-lightbox]');
  if (!film || !dialog) return;
  const track = film.querySelector('.film__track');
  const prev = film.querySelector('[data-film-prev]');
  const next = film.querySelector('[data-film-next]');
  const dialogImg = dialog.querySelector('img');
  const dialogCaption = dialog.querySelector('figcaption');

  const step = () => track.clientWidth * 0.8;
  prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
  next.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));

  const updateButtons = () => {
    prev.disabled = track.scrollLeft <= 1;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 1;
  };
  track.addEventListener('scroll', updateButtons, { passive: true });
  window.addEventListener('resize', updateButtons);
  window.addEventListener('load', updateButtons);
  track.querySelectorAll('img').forEach((img) => img.addEventListener('load', updateButtons));
  updateButtons();

  let down = false;
  let dragged = false;
  let startX = 0;
  let startScroll = 0;
  track.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse') return;
    down = true; dragged = false; startX = event.clientX; startScroll = track.scrollLeft;
  });
  window.addEventListener('pointermove', (event) => {
    if (!down) return;
    const dx = event.clientX - startX;
    if (!dragged && Math.abs(dx) > 5) { dragged = true; track.classList.add('is-dragging'); }
    if (dragged) track.scrollLeft = startScroll - dx;
  });
  window.addEventListener('pointerup', () => { down = false; track.classList.remove('is-dragging'); });

  track.addEventListener('click', (event) => {
    const opener = event.target.closest('.film__open');
    if (!opener) return;
    if (dragged) { dragged = false; return; }
    const img = opener.querySelector('img');
    dialogImg.src = opener.dataset.full || img.currentSrc || img.src;
    dialogImg.alt = img.alt;
    dialogCaption.textContent = opener.closest('figure').querySelector('figcaption')?.textContent || '';
    dialog.showModal();
  });
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog || event.target.closest('[data-lightbox-close]')) dialog.close();
  });
})();
```

- [ ] **Step 2: Syntax-check the scripts**

Run: `for f in assets/js/*.js; do node --check "$f" && echo "ok $f"; done`
Expected: four `ok` lines.

- [ ] **Step 3: Commit**

```bash
git add assets/js
git commit -m "Add header, reveal, theme and gallery behaviour"
```

---

### Task 6: 404, SEO files, README, CLAUDE.md

**Files:**
- Create: `404.html`, `robots.txt`, `sitemap.xml`, `README.md`, `CLAUDE.md`

- [ ] **Step 1: Write the files**

<!-- file: 404.html -->
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page not found | Necopolymer</title>
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#0A1A13">
  <!-- Root-absolute paths: GitHub Pages serves this file for any missing path on necopolymer.com. -->
  <link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/base.css">
  <link rel="stylesheet" href="/assets/css/components.css">
  <script>
    try {
      var saved = localStorage.getItem('neco-theme');
      if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
    } catch (e) {}
  </script>
</head>
<body>
  <main class="container notfound">
    <p class="eyebrow">404</p>
    <h1 class="section__title">This page has been <span class="text-gradient">recycled.</span></h1>
    <p class="section__lead">The page you are looking for does not exist.</p>
    <a class="btn btn--primary" href="/">Back to Necopolymer</a>
  </main>
</body>
</html>
```

<!-- file: robots.txt -->
```text
User-agent: *
Allow: /

Sitemap: https://necopolymer.com/sitemap.xml
```

<!-- file: sitemap.xml -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://necopolymer.com/</loc>
    <lastmod>2026-10-16</lastmod>
  </url>
</urlset>
```

<!-- file: README.md -->
~~~markdown
# neco-landing-page

The single-page website of **Necopolymer LLC**, a PET, HDPE and polypropylene recycling
company in Kotayk Province, Armenia. Live at **https://necopolymer.com** (GitHub Pages).

Plain HTML, CSS and JavaScript. **No build step, no npm, no dependencies.** Push to `main`
and GitHub Pages publishes it within about a minute.

## Run it locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
python3 scripts/check.py      # static checks; run before every push
```

## Layout

| Path | What it is |
|---|---|
| `index.html` | The whole page: all text and contact details live here |
| `assets/css/tokens.css` | **Every colour, font, size, radius and duration.** Restyle here |
| `assets/css/base.css` | Fonts, reset, layout primitives, buttons, reveal animation |
| `assets/css/components.css` | Header, hero, products, about, film strip, contacts, careers, footer |
| `assets/js/` | `nav.js` header and menu · `reveal.js` scroll fade-ins · `gallery.js` film strip and lightbox · `theme.js` dark/light toggle |
| `assets/brand/` | `icons.svg` sprite (generated), `favicon.svg`, `og-image.jpg` (link-preview card) |
| `assets/img/` | WebP images: `hero/`, `products/`, `about/`, `gallery/` |
| `scripts/check.py` | Checks: no stray colours, contacts present, no broken links, alt text |
| `tools/build-icons.py` | Rebuilds `icons.svg` from pinned Lucide and Simple Icons versions |
| `404.html`, `robots.txt`, `sitemap.xml`, `.nojekyll`, `CNAME` | GitHub Pages and SEO plumbing |

## Common changes

**Colours and fonts.** Edit `assets/css/tokens.css` only. Scheme-dependent colours are written
`light-dark(LIGHT, DARK)`, so each one is a single-line edit for both themes.

**Contact details** appear in three places in `index.html`: the *Contacts* section, the
footer, and the JSON-LD block in `<head>`. Phone also appears in the Careers call-to-action
and the meta description. Search for `37498886456` and `varodjana@gmail.com`.

**Product photos.** Replace `assets/img/products/pet.webp`, `hdpe.webp` or `pp.webp` with a
900×600 WebP (keep the file name), and update that image's `alt` text in `index.html`:

```bash
magick photo.jpg -resize 900x600^ -gravity center -extent 900x600 /tmp/p.png && cwebp -q 78 /tmp/p.png -o assets/img/products/pet.webp
```

**Gallery frames.** Add a WebP to `assets/img/gallery/` (about 1600 px wide) and copy one
`<figure class="film__frame">` block in `index.html`.

**Icons.** Add the name to `UI` or `BRANDS` in `tools/build-icons.py`, run it, then use
`<svg class="icon"><use href="assets/brand/icons.svg#NAME"></use></svg>`.

## Hosting and domain

- Repository: `zenithdevops/neco-landing-page` (public; Pages: `main` / root).
- Custom domain: `necopolymer.com` (registered at GoDaddy). DNS at GoDaddy:

| Type | Name | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | zenithdevops.github.io |

## Credits

- Fonts: [Sora](https://fonts.google.com/specimen/Sora) and [Inter](https://rsms.me/inter/), SIL Open Font License, via Fontsource.
- Icons: [Lucide](https://lucide.dev) (ISC) and [Simple Icons](https://simpleicons.org) (CC0).
- Stock photos, all public-domain (CC0), found via [Openverse](https://openverse.org):
  hero and HDPE/PP placeholders from [rawpixel](https://www.rawpixel.com) ("Free pile plastic bottles image",
  "Recycling sorting", "Plastic bottle caps"); PET placeholder
  ["Recyclable finnish plastic bottles with deposit"](https://commons.wikimedia.org/wiki/File:Recyclable_finnish_plastic_bottles_with_deposit.jpg), Wikimedia Commons.
- Portrait and gallery photos © Necopolymer LLC.

Maintained by Vrej Abramian.
~~~

<!-- file: CLAUDE.md -->
```markdown
# Working agreement: neco-landing-page

## What this repo is

The one-page website of Necopolymer LLC (plastic recycling, Armenia), served by GitHub Pages
from `main` at https://necopolymer.com. Hand-written static HTML/CSS/JS.

**No build step. No npm. No dependencies. No GitHub Actions.** Do not add a framework,
bundler, preprocessor or CI build. The site must keep deploying for years untouched.

## Deliberate decisions: do not "fix" these

| Decision | Why |
|---|---|
| All design values in `tokens.css` | The owner restyles by editing one file. `scripts/check.py` fails on colour literals anywhere else (brand SVGs and the `theme-color` meta excepted). |
| `light-dark()` tokens, no second palette block | Each colour is declared once for both schemes; the toggle only flips `color-scheme`. |
| Text in HTML, not JS | Search engines index it. JS only adds behaviour. |
| Inline `<head>` script | Must run before first paint (theme + `html.js` gate). Do not move it to a file. |
| `[data-reveal]` hidden only under `html.js` | Without JS everything is visible. |
| Header glass on `::before` | `backdrop-filter` on the header itself would trap the fixed mobile menu inside it. |
| Relative asset paths in `index.html` | Works at the github.io preview sub-path and at the domain root. `404.html` uses root-absolute paths on purpose. |
| No stats/counters, no testimonials, no form, no analytics | No verified figures exist; nothing is invented. No cookies, no banner. |
| Stock photos are placeholders | Real product photos replace them with the same file names (see README). |

## Copy rules

- Formal, plain English. Short sentences. No invented numbers, certifications or clients.
- Contact data must match exactly: `+37498886456` (shown `+374 98 886456`), `varodjana@gmail.com`,
  "Hangar No. 2, 22nd Street, Ptghni, Kotayk Province, Armenia".
- Footer keeps "Maintained by Vrej Abramian".

## Git

- Commit as the personal account only: repo-local `user.name vrejabramian`,
  `user.email 237103231+vrejabramian@users.noreply.github.com`. `gh` account: `vrejabramian`.
  Never use the `vrej-abramian` work identity here.

## Before you finish

1. `python3 scripts/check.py` passes.
2. `python3 -m http.server` and look at desktop and mobile widths, in both themes, with the console clear.
3. Every new motion effect respects `prefers-reduced-motion`.
```

- [ ] **Step 2: Run the check (should now pass)**

Run: `python3 scripts/check.py`
Expected: `OK: all checks passed`

- [ ] **Step 3: Commit**

```bash
git add 404.html robots.txt sitemap.xml README.md CLAUDE.md
git commit -m "Add 404 page, SEO files, README and working agreement"
```

---

### Task 7: Browser verification

- [ ] **Step 1:** `python3 -m http.server 8765` (background) from the repo root.
- [ ] **Step 2:** In Chrome, open `http://localhost:8765/` at about 1440×900. Screenshot hero, products, about, gallery, contacts, careers and footer. Confirm: header transparent over hero → glass after scroll; active tab follows the section; reveals play.
- [ ] **Step 3:** Toggle the theme and screenshot products and contacts in light mode; reload and confirm the choice persists.
- [ ] **Step 4:** Resize to 390×844: open and close the hamburger menu, check nothing scrolls horizontally, and the film strip swipes.
- [ ] **Step 5:** Click a film frame: the lightbox opens; Esc and a backdrop click close it.
- [ ] **Step 6:** Read the console: no errors, no 404s.
- [ ] **Step 7:** Fix anything found, re-run `python3 scripts/check.py`, commit `Polish after browser review`.

---

### Task 8: Publish to GitHub Pages

- [ ] **Step 1: Create the repo and push (as vrejabramian)**

```bash
gh auth switch -u vrejabramian
gh repo create zenithdevops/neco-landing-page --public \
  --description "Necopolymer LLC: PET, HDPE & PP plastic recycling, Armenia. Static site on GitHub Pages." \
  --homepage https://necopolymer.com --source . --remote origin --push
```

- [ ] **Step 2: Enable Pages from `main` / root**

```bash
gh api -X POST repos/zenithdevops/neco-landing-page/pages -f 'source[branch]=main' -f 'source[path]=/'
gh api repos/zenithdevops/neco-landing-page/pages --jq '.html_url, .status'
```

- [ ] **Step 3: Wait for the build, then verify the preview URL**

```bash
gh api repos/zenithdevops/neco-landing-page/pages/builds/latest --jq '.status'   # until "built"
curl -sI "$(gh api repos/zenithdevops/neco-landing-page/pages --jq .html_url)" | head -1   # HTTP/2 200
```
Open the preview URL in Chrome and repeat a quick pass of Task 7 Steps 2 and 6.

---

### Task 9: Custom domain (after the owner adds the GoDaddy DNS records)

- [ ] **Step 1:** Confirm DNS: `dig +short necopolymer.com A` returns the four `185.199.10x.153` addresses; `dig +short www.necopolymer.com` returns `zenithdevops.github.io.`
- [ ] **Step 2:** `printf 'necopolymer.com\n' > CNAME`, commit `Point the site at necopolymer.com`, push.
- [ ] **Step 3:** `gh api -X PUT repos/zenithdevops/neco-landing-page/pages -f cname=necopolymer.com`
- [ ] **Step 4:** When `gh api repos/zenithdevops/neco-landing-page/pages --jq .https_certificate.state` is `approved`, run `gh api -X PUT repos/zenithdevops/neco-landing-page/pages -F https_enforced=true`.
- [ ] **Step 5:** `curl -sI https://necopolymer.com | head -1` → `HTTP/2 200`; `curl -sI http://www.necopolymer.com | grep -i location` → `https://necopolymer.com/`.
