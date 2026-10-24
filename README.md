# Gaby Padilla Makeup Artist — GitHub Pages staging

This repository is a **preview/staging** copy of website version 6. It is not the final production website.

## Publish on GitHub Pages

1. Create a **public** repository named `gaby-padilla-website` in your GitHub account. The user can then authorize a connected app to commit this site to the repo (or upload the files manually).
2. Upload/commit the files and folders **at the repository root** (so `index.html` is at root).
3. Go to **Settings → Pages** and choose **Deploy from a branch → main → /(root)**; save.
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
