# joonsukbae.github.io

Personal homepage for Joonsuk Bae. PhD candidate, Sungkyunkwan University. ALICE Run 3 jet physics and ePIC BIC calorimeter R&D.

## Stack

Hand-rolled static HTML + CSS. No build step. A tiny Python script converts the BibTeX file used by the CV into the publications page.

- Zero runtime dependencies
- Zero JS on the live site
- Self-hosted system font stack (Inter / system-ui sans, Newsreader / system serif)
- Deploys to GitHub Pages directly (`.nojekyll` present)

## Local development

Serve the site with any static server. Python 3 ships on macOS:

```bash
cd /Users/js/personal/joonsukbae.github.io
python3 -m http.server 4173
# open http://localhost:4173/
```

That's it. No watcher needed; reload the browser after each edit.

## Updating publications

The publications page is generated from the same `publications.bib` the CV uses. Re-run when the bib changes:

```bash
python3 scripts/build_publications.py
```

The script reads:

- `/Users/js/Library/Mobile Documents/com~apple~CloudDocs/Lab./CV/source/publications.bib`

and writes:

- `publications/index.html`

Per-entry role notes are curated by BibTeX key inside `scripts/build_publications.py` (see `CURATED`).

## Refreshing the CV PDF

```bash
cd "/Users/js/Library/Mobile Documents/com~apple~CloudDocs/Lab./CV/source"
latexmk -pdf main.tex
cp main.pdf "/Users/js/personal/joonsukbae.github.io/cv/joonsuk-bae-cv.pdf"
```

## Layout

```
/                  home / bio
/research/         research narrative
/publications/     generated from publications.bib
/talks/            talks, posters, seminars
/cv/               CV summary + embedded PDF
/contact/          contact links
assets/css/        style.css (single stylesheet)
assets/img/        portraits, figures
scripts/           build_publications.py
```

## Design

Off-white paper, near-black ink, a single hanko-red mark used sparingly. Sans-serif body, serif headings. Asymmetric two-column at wide widths with a slim left rail for section labels. Strict 8px vertical rhythm. No animations beyond 90 ms link-hover transitions. Light and dark via `prefers-color-scheme`.

## Deployment

Push to GitHub. Repository name `joonsukbae.github.io` triggers GitHub Pages on the default branch. The `.nojekyll` file disables Jekyll processing so paths like `/research/` are served correctly.

Custom domain (planned): `joonsukbae.com`.
