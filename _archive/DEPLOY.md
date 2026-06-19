# v2 deployment plan

The `v2/` directory holds the redesigned site. Current root holds v1.

## What stays at root (do not move)

- `CNAME` — GitHub Pages custom domain config
- `robots.txt`
- `sitemap.xml` — update `lastmod` dates after swap
- `README.md`
- `scripts/`

## What gets swapped

| Path                 | v1 (current)     | v2 (target)     |
|----------------------|-------------------|------------------|
| `/index.html`        | v1 hero           | v2 hero          |
| `/research/`         | v1 research       | v2 research      |
| `/publications/`     | v1 publications   | v2 publications  |
| `/talks/`            | v1 talks          | v2 talks         |
| `/cv/`               | v1 CV page + PDFs | v2 CV page + PDFs |
| `/contact/`          | v1 contact        | v2 contact       |
| `/assets/`           | v1 CSS only       | v2 CSS + fonts + svg |
| `/404.html`          | v1 404            | v2 404           |

## Steps (one-shot, reviewable)

```bash
cd /Users/js/personal/joonsukbae.github.io

# 1. archive v1
mkdir -p _archive/v1
mv index.html 404.html _archive/v1/
mv research publications talks cv contact assets _archive/v1/

# 2. promote v2 to root
mv v2/index.html .
mv v2/404.html .
mv v2/research v2/publications v2/talks v2/cv v2/contact .
mv v2/assets .
mv v2/DEPLOY.md _archive/

# 3. cleanup empty v2/
rmdir v2

# 4. verify
ls -la
ls assets/css assets/fonts assets/svg cv

# 5. update sitemap.xml lastmod dates to today
# (manual edit)

# 6. commit
git add -A
git commit -m "Redesign: v2 site to root, archive v1"

# 7. (do NOT push without confirmation)
# git push origin main  ← decision pending
```

## Roll-back

If something is broken after deploy:

```bash
cd /Users/js/personal/joonsukbae.github.io
rm index.html 404.html
rm -rf research publications talks cv contact assets
cp -r _archive/v1/* .
```
