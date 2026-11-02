# Gaby Padilla Makeup Artist — GitHub Pages staging

This repository contains the website and WhatsApp shop preview. GitHub Pages serves the `shop-whatsapp-staging` branch. Production deploys separately from `main` to Namecheap.

## Hosted staging

- English shop: https://jkgraphix11.github.io/gaby-padilla-website/tienda/?preview=1&lang=en
- Spanish shop: https://jkgraphix11.github.io/gaby-padilla-website/tienda/?preview=1&lang=es
- Pages source: `shop-whatsapp-staging`, repository root. Pushes to this branch refresh the preview through GitHub Pages. Do not merge to `main` to update staging.
- Use the full preview URLs above. Admin changes are browser-session simulations, and WhatsApp buttons preview an unsent inquiry; this static host has no catalog service or real inventory management.

## Publish on GitHub Pages

1. Create a **public** repository named `gaby-padilla-website` in your GitHub account. The user can then authorize a connected app to commit this site to the repo (or upload the files manually).
2. Upload/commit the files and folders **at the repository root** (so `index.html` is at root).
3. Go to **Settings → Pages** and choose **Deploy from a branch → shop-whatsapp-staging → /(root)**; save.
4. Open **Settings → Pages → Visit site** after the deployment succeeds. The staging URL typically follows the `https://USERNAME.github.io/gaby-padilla-website/` pattern. Do not assume it is live until confirmed.
5. Test `novias/`, `xv-anos/`, `en/`, `en/bridal/`, `en/quinceanera/`, buttons, images, videos, and language links.

## Staging safety

- All six pages are marked with `meta name="robots" content="noindex, nofollow, noarchive"`. **This is only a request to search engines, not privacy or access control.**
- The site remains visible to anyone who has the staging URL. Do not upload confidential photos/data.
- `robots.txt` permits crawlers to read the noindex meta tag. Do **not** block them with Disallow for staging.
- Do not run `prepare_launch.py` against the staging site; that script installs production canonical/hreflang/sitemap tags for a production domain.
- SEO in the production package remains unchanged.
- Existing general AgendaPro booking links are preserved; update them as needed when dedicated booking URLs are confirmed.

## When launching production

Remove `noindex`, use a production domain in `prepare_launch.py`, and validate canonicals/hreflang/sitemap; then migrate the photos and copy to the production host.

GitHub Pages does not enforce password protection for a public staging website. For access-controlled previews, choose a host with authentication instead.

## Responsive images

Original photos stay in `assets/images/` for full-size gallery viewing. Responsive
WebP copies use `-responsive-WIDTH.webp` names and are referenced by the page
`srcset` attributes. With Pillow installed, regenerate these copies with
`python scripts/optimize_images.py`. The script reads originals, preserves alpha
transparency, verifies each encoded image, and prints the output dimensions and
byte sizes. Keep each `srcset` width descriptor equal to the file's actual width.

The production workflow runs `prepare_launch.py` and changes the six service
pages from staging `noindex` to `index, follow` in its build. Keep that staging
protection in source; review branches must not trigger a production deployment.
