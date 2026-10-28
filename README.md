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


## WhatsApp shop — development preview

The shop is being developed on a separate branch. Do not merge this branch or run the Namecheap deployment until the shop is ready for launch: main has an existing production workflow.

- Storefront design: `tienda/?preview=1`; add `&lang=en` for English.
- Inventory demonstration: `tienda/manage.html?preview=1`. This changes browser-session sample data only. It is not an authenticated live admin panel.
- Persistent inventory and approval service: `shop-service/`. See its README for local setup and production requirements. GitHub Pages cannot execute this Python service.
- Live catalog starts empty. Illustrated demo products, prices and counts are fictional. Real product photos and confirmed details will be added as drafts for Gaby's approval.
- Database, originals, uploaded inventory photos and credentials are excluded from source control.
- Automatic ChatGPT photo editing/publishing is not yet connected. A separate authorized account connection and suitable production hosting are required.
- No production catalog or admin link has been launched on Gaby's public domain.

### Local preview from this repository

Use Python 3.9+ with `shop-service/requirements.txt` installed. Set `GABY_SHOP_TOKEN` privately to a random secret of at least 32 characters and run `python3 -B shop-service/server.py`. Open the printed loopback preview URL. The service supports both this repository's root layout and the original local `website/` layout. Do not expose this development server to the Internet.

### Before launch

Confirm real inventory and product imagery; configure production authentication, persistent storage and backups; connect and test the authorized ChatGPT workflow; replace preview navigation with ordinary shop links; omit the demo pages/controls from the deployment; verify WhatsApp ordering, sold-out/hide/restock behavior and shop metadata. Publish only after approval.
