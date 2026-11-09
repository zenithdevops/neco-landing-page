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
and the meta description. Search for `37498339349` and `varodjana@gmail.com`.

**Product photos.** Replace `assets/img/products/pet.webp`, `hdpe.webp` or `pp.webp` with a
900×600 WebP (keep the file name), and update that image's `alt` text in `index.html`:

```bash
magick photo.jpg -resize 900x600^ -gravity center -extent 900x600 /tmp/p.png && cwebp -q 78 /tmp/p.png -o assets/img/products/pet.webp
```

**Gallery frames.** Add a WebP to `assets/img/gallery/` (about 1600 px wide) and copy one
`<figure class="film__frame">` block in `index.html`.

**Gallery videos.** Videos stay on YouTube or Instagram and nothing from those sites loads until a
visitor clicks. Save the preview image as a WebP in `assets/img/gallery/` and copy one
`film__open--video` block in `index.html`, changing its link, image, labels and caption.

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
- Video preview images belong to the videos' publishers: Ministry of Environment of Armenia, EcoLur and Hayern Aysor.

Maintained by Vrej Abramian.
