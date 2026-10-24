GABY PADILLA MAKEUP ARTIST — WEBSITE VERSION 3 · SEO & LOCAL SEARCH

OPEN THE SITE
Open index.html (Spanish) and en/index.html (English). For hosting, upload the entire folder to your website root. Use a local static HTTP server to test navigation and video reliably.

WHAT CHANGED
Two search-engine-visible Spanish/English pages; local service coverage section for Playas de Tijuana, Tijuana, and Valle de Guadalupe; localized SEO titles and descriptions, improved photo names and alt text, social share image, appropriate local business structured data, performance/accessibility improvements. No personal home address is disclosed.

BEFORE LAUNCH
See SEO-LAUNCH-CHECKLIST.md. Once the real domain is determined, run: python prepare_launch.py https://YOUR-REAL-DOMAIN.mx
This adds canonical and hreflang URLs (cannot be guessed now), absolute social URLs, and the XML sitemap.

EDIT BOOKING
Change BOOKING_URL at the top of script.js once your final AgendaPro link is ready. Use find/replace on the fallback HTML href values if needed.

RESTRICTIONS
No fake testimonials, ratings, business hours, phone numbers, or street addresses were added. Prices are in MXN. Ask about on-location coverage and any event travel fees.

V5 - SPECIALIZED BRIDAL AND XV PAGES:
ES: /novias/ and /xv-anos/
EN: /en/bridal/ and /en/quinceanera/
Home feature cards link to these real service pages (no longer booking directly).
Bridal and XV booking buttons use the working general AgendaPro booking URL for now.
To use verified service-specific AgendaPro URLs, edit BOOKING_URLS.bridal and BOOKING_URLS.xv in script.js.
Current source of text: package details supplied by Gaby. No travel-fee assumptions.
New photos from Gaby added to home portfolio; service page images can be refreshed anytime.
The preview is a standalone HTML file for review. Publish website contents using a proper static host so the real /novias/ etc. pages have distinct crawlable URLs.

V6 — VERIFIED SERVICE CATALOG / AGENDA PRO
Source: https://agendapro.com/site/mx/gabypadillamakeupartist/578261 (verified October 23 2026).
Services and appointment durations now match the AgendaPro listing in ES and EN.
Booking links on all six pages point to the exact verified AgendaPro page.
The $2,000 MXN deposit and two remaining payments are as stated there;
do not assume the two installments are required to be equal unless Gaby confirms.
180/150 minutes are AgendaPro scheduling durations, not the aggregate time across all package appointments.
Direct service-specific AgendaPro links were not available for verification; BOOKING_URLS in script.js can be updated when available.
For SEO, keep service names, prices and descriptions consistent with Gaby's active AgendaPro catalog.
