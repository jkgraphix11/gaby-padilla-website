# Gaby Padilla — local SEO launch checklist (V3)

## Built into the site
- Separate, **server-rendered** Spanish (`/`) and English (`/en/`) HTML pages. The language switch follows direct links; all content is legible to crawlers with JavaScript disabled.
- Specific localized `<title>` tags, unique meta descriptions, OG/Twitter sharing metadata, large 1200 × 630 share image from Gaby's original photography.
- Semantic H1 / H2 / H3 markup, accessible links and image alt text, descriptive image filenames, lazy-loaded gallery images, restrained font/media load, mobile-first layout and keyboard-accessible menu.
- Visible original content about studio in Playas de Tijuana, local appointments across Tijuana, and event services subject to availability in Valle de Guadalupe.
- `BeautySalon` structured data for business name, Instagram, service area, and published services/prices (MXN), without inventing private address, telephone, ratings, opening hours or fabricated reviews.
- `robots.txt` allows crawling; **canonical, hreflang and sitemap require a real public website URL** and are handled by the launch script.

## Before publishing — required
1. Verify all services, **especially bridal / quinceañera packages, trial inclusions, treatment names and pricing**.
2. Verify that Gaby serves on-location events in Valle de Guadalupe, and confirm any travel fees/deposits; website currently invites inquiries rather than promising availability.
3. Verify the public booking URL (currently the provided AgendaPro link). To update all buttons, edit `BOOKING_URL` at the top of `script.js`, and also update the fallback `href` attributes in both `index.html` and `en/index.html` if no-JS support matters.
4. Decide and point a real domain at hosting (e.g. `https://actual-domain.mx`). **Before uploading**, run `python prepare_launch.py https://actual-domain.mx` in the website folder. This writes fully-qualified canonical/hreflang/OG URLs on both pages, updates structured data URLs, and produces `sitemap.xml` and `robots.txt`.
5. Test both paths (`/` and `/en/`), booking links, video playback, and forms on the live HTTPS domain; make sure `robots.txt` and sitemap both return HTTP 200, with no staging password or `noindex` headers.
6. Add the verified domain to **Google Search Console**; submit `/sitemap.xml` and inspect indexing for both language URLs. Optional Bing Webmaster Tools.
7. Create/claim and verify an accurate **Google Business Profile** in the appropriate category. Set service areas in Playas/Tijuana and Valle if actually served. Because the studio is home-based, carefully follow Google's storefront vs. service-area eligibility rules; avoid exposing the home address unless she meets storefront requirements and intentionally chooses to show it.
8. Keep NAP (Name / Address if intentionally public / Phone) and social website URLs consistent; consider a separate business WhatsApp / contact channel if she wants to display one. **No home-studio street address has been included.**
9. Obtain permission for any client photos and testimonials; add real reviews / before-and-after galleries when available. Never add self-serving review star schema.
10. Validate pages using Google Rich Results Test + Schema Markup Validator and benchmark the deployed URL with PageSpeed Insights. Review Google Search Console monthly; adjust content based on real search queries rather than repeating keywords.

## No domain yet?
Upload and test the site; both HTML pages are crawlable. **Do not paste an invented domain into the canonical or sitemap fields**. Contact us once the public domain is known for final SEO validation. Local-business rich results are not guaranteed, and Google may require an address to qualify for some LocalBusiness features.

## Google guidance consulted
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/appearance/google-images
- https://developers.google.com/search/docs/appearance/structured-data/organization
- https://support.google.com/business/answer/9157481
- https://support.google.com/business/answer/2853879

## V5 local service landing pages
- [ ] Publish six indexable pages: /, /en/, /novias/, /xv-anos/, /en/bridal/, /en/quinceanera/.
- [ ] Run `python prepare_launch.py https://YOUR-VERIFIED-DOMAIN` on a pre-deployment copy. Generates unique self-canonicals, reciprocal language tags and six sitemap URLs.
- [ ] Verify /novias/ and /xv-anos/ appear in Google Search Console, and submit /sitemap.xml.
- [ ] Replace general AgendaPro links for bridal/XV with exact *verified* service-specific links in script.js, if provided.
- [ ] Confirm the $2,000 MXN reservation deposit/remaining balance and terms shown are current.
- [ ] Add true client galleries and legitimate testimonials later; never invent reviews or customer identities.
- [ ] Optimize real wedding/XV service photos before upload and add relevant, descriptive alt text.
- [ ] Avoid using the home address in public structured data; clarify service area and travel terms.

## V6 listing consistency
- [ ] Verify the AgendaPro service menu after any owner-side changes; update both language homepages and JSON-LD offers.
- [ ] Do not present the 180/150-minute booking slot as total multi-visit package time.
- [ ] Update BOOKING_URLS when individual AgendaPro service deep links are confirmed working.
- [ ] Check reservation and installment terms with Gaby before publishing changes to either system.
