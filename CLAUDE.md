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
- Contact data must match exactly: `+37498339349` (shown `+374 98 339349`), `varodjana@gmail.com`,
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
