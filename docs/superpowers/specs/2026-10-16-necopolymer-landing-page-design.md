# Necopolymer landing page — design

Date: 2026-10-16 · Status: approved

## Goal

A single-page, cinematic, professional "business card" site for **Necopolymer LLC**, a
plastic recycling company (PET, HDPE, polypropylene) based in Yerevan, Armenia. Ship fast;
copy and sections will be refined later.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Stack | Hand-written HTML/CSS/JS, no build, no npm, no Actions | Mirrors the proven `zenith-landing-page` pattern; nothing to rot |
| Configurability | All design values in `assets/css/tokens.css` (`light-dark()` tokens) | One file to restyle; `base.css`, `components.css`, JS and HTML hold no colour literals (checked by `scripts/check.py`); tunable sizes and durations are tokens too |
| Content | Written in `index.html`, not JS-rendered | Indexable by search engines |
| Language | English only at launch | `/hy/` and `/ru/` pages may be added later; fonts chosen to allow it |
| Direction | "Cinematic Evergreen", dark-first, with a light scheme | Chosen by the owner |
| Imagery | Free-licence stock (Unsplash/Pexels), downloaded, compressed, self-hosted; credited in README | Owner's own product photos replace them later |
| Fonts | Sora (headings), Inter (body), self-hosted WOFF2 | No third-party requests |
| Hosting | GitHub Pages from `main` / root, public repo `zenithdevops/neco-landing-page` | Free org plan requires public |
| Domain | `necopolymer.com` (apex) + `www` via GoDaddy DNS | See "Domain" |

## Palette (dark scheme; light scheme derived in `tokens.css`)

| Token | Value |
|---|---|
| bg | `#0A1A13` |
| surface | `#12281E` |
| primary | `#1F8A5B` |
| accent | `#B5E655` |
| accent-2 | `#5CC8E0` |
| text | `#EAF4EE` |

## Page structure

Fixed glass header (blur, solidifies on scroll; hamburger drawer on mobile; theme toggle).
Tabs **Home · Products · About · Gallery · Contacts · Careers** smooth-scroll to their section;
the active section's tab is highlighted.

1. **Home (hero)**: full-viewport stock image, slow Ken Burns zoom, green gradient overlay.
   Headline "Giving plastic a second life." Subline "PET, HDPE and polypropylene recycling
   in Armenia." CTAs: Contact us → #contacts, Our products → #products.
2. **Products**: three cards: PET (♳ 1), HDPE (♴ 2), Polypropylene (♷ 5). Each has a resin-code
   badge, a placeholder image (one file to swap), a two-line description and typical sources.
3. **About**: `Prof0.jpg` (resized, WebP + JPEG fallback). "I am Varodjan Abramian, founder and
   CEO of Necopolymer LLC." plus about three generated lines.
4. **Gallery**: a "film roll" strip with sprocket borders; horizontal scroll (drag/swipe/arrow
   buttons); click opens a lightbox. Frames: `pic1` (resized), `pic2` (cropped to remove the
   phone-camera watermark). Adding a frame means adding a `<figure>`.
5. **Contacts**:
   - Phone `+374 98 886456` (`tel:+37498886456`) with WhatsApp (`https://wa.me/37498886456`),
     Viber (`viber://chat?number=%2B37498886456`) and Telegram (`https://t.me/+37498886456`) icons.
   - Email `varodjana@gmail.com` (`mailto:`).
   - Address "Ptghni, 22nd Street, Hangar No. 2, Kotayk Province, Armenia", with a map pin linking
     to `https://maps.app.goo.gl/LxYBtuq4fgTTaktv6`.
6. **Careers**: Production Worker, Marketing Specialist. "Interested? Get in touch." CTAs to phone/email.
7. **Footer**: wordmark, one-line mission, quick links, contacts, "© 2026 Necopolymer LLC",
   small "Maintained by Vrej Abramian".

Contact data appears in Contacts and the footer; README lists both locations.

## Behaviour (vanilla JS, no libraries)

`nav.js` (header state, active tab, mobile drawer), `reveal.js` (IntersectionObserver
fade-up), `gallery.js` (film-strip drag/arrows, lightbox), `theme.js` (dark/light toggle; an
inline pre-paint snippet in `<head>`). All motion is disabled under `prefers-reduced-motion`.
Every interaction also works with the keyboard; the lightbox closes on Esc.

## Repository layout

```
index.html 404.html CNAME .nojekyll robots.txt sitemap.xml
assets/css/{tokens,base,components}.css
assets/js/{nav,reveal,gallery,theme}.js
assets/fonts/  assets/img/{hero,products,about,gallery}/  assets/brand/{logo.svg,favicon.svg}
README.md CLAUDE.md .gitignore docs/superpowers/{specs,plans}/
```

## Git / GitHub

- Local repo: `/Users/vrej/myProjects/TEMP/varodjan-necopolymer/neco-landing-page/`.
- Repo-local identity `vrejabramian <237103231+vrejabramian@users.noreply.github.com>`; the
  global work identity is never used here. `gh` is active on `vrejabramian`.
- Original photos stay in `temp.ignore/`; only optimized derivatives are committed.

## Domain

`CNAME` contains `necopolymer.com`. It is committed only after the GoDaddy records exist:
adding it earlier makes Pages redirect the preview URL to a domain that does not resolve yet.
All asset paths are relative so the site works both under the preview sub-path and at the
domain root. GoDaddy DNS: four apex A records
(185.199.108.153, .109, .110, .111), `www` CNAME → `zenithdevops.github.io`; remove the
parked `@` record and forwarding. Optional org-level domain verification TXT record. Enforce
HTTPS once the certificate is issued.

## Verification

- Chrome at desktop and mobile widths, in both schemes, with no console errors.
- grep: no hex/rgb colour literals outside `tokens.css`.
- Every link target checked (tel, WhatsApp, Viber, Telegram, mailto, Maps).
- Live check on the Pages URL, then on `necopolymer.com`.

## Out of scope (for now)

Contact form, analytics, translations, real product photos, statistics/counters (no
verified figures exist; none will be invented).
