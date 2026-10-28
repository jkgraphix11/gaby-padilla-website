# Gaby’s product shop — first local pilot

## What is built

- Spanish/English storefront at `/tienda/` matching the existing site's cream, cocoa, Italiana, and DM Sans visual style.
- Category filters, available-only filter, product details, fixed size/shade display, stock-limited quantity selection, WhatsApp product inquiry with MXN subtotal and a stable product link.
- Published zero-stock products remain visible with a restock inquiry instead of a purchase button. Hidden and draft products never appear in the public catalog.
- Management page at `/tienda/manage.html`: photo upload, draft editing, explicit review/publish, sold-out/hide actions and restock via editing the same record.
- A Python/SQLite local catalog service. Writes require bearer authorization. Approval requires the exact current revision. Draft and live snapshots are separate. Each successful mutation adds an audit event. Original live text stays unchanged when a pending edit exists.
- `/tienda/?preview=1` and `manage.html?preview=1` are a safe design demo using generic fictional product illustrations, example prices and browser-session state. They do not call the mutation API or send WhatsApp messages. Same-tab navigation preserves simulated edits. These examples are not Gaby's inventory.
- Source website navigation links to the staged shop. The existing `output/namecheap-production/` and production zip are unchanged. Nothing has been deployed to `gabypadillamakeup.com`.

## Run locally

Use Python 3.9+ and Pillow (see requirements.txt). Keep data outside `website/`. Set a private random `GABY_SHOP_TOKEN` environment variable of at least 32 characters through your normal secret-management process. Never put it in a URL or commit it.

```
python3 -B shop-service/server.py
```

Default address: `http://127.0.0.1:8765/tienda/?preview=1`.
The ordinary local `/tienda/` reads live SQLite data. The default database is `shop-data/catalog.sqlite3`, outside the public website. The server listens only on loopback. This is a local pilot, not a production web server.

For real local management, open `/tienda/manage.html` and enter the session token. It stays in page memory, not browser storage. In demo mode no token is needed because mutations only simulate changes in sessionStorage.

## API

All responses disable caching. All mutation/read-management requests use `Authorization: Bearer ...`. No CORS headers are emitted. The public catalog exposes only approved public product fields.

| Method / path | Behavior |
| --- | --- |
| GET /api/catalog | Public approved products and WhatsApp configuration |
| GET /api/products | Private list, current revision and pending-draft flag |
| GET /api/products/{id} | Private draft and approved snapshot |
| POST /api/products | Create draft only |
| POST /api/products/{id} | Replace draft; require current revision |
| POST /api/products/{id}/publish | Publish reviewed draft; require current revision and approved=true |
| POST /api/products/{id}/sold-out | Set draft/live quantities to zero without publishing pending copy; require revision and approval |
| POST /api/products/{id}/hide | Remove from public catalog without deleting history; require revision and approval |

Draft fields: name, brand, size, description, price (MXN), quantity (whole units), category (skincare/makeup), image. Optional name_en and description_en. Uploaded images can be data URLs from the management page; image files are decoded, EXIF orientation corrected, metadata removed, size constrained, and re-encoded to JPEG. This is normalization, not AI background cleanup. Runtime uploads must be durable and backed up.

For an eventual Actions integration, `openaiFileIdRefs` can contain one documented ChatGPT file-reference object. The server fetches only HTTPS `files.oaiusercontent.com` attachments, does not follow redirects, caps downloads, and validates/re-encodes images. Other download hosts fail closed and require a deliberate integration update. Never use arbitrary URL image downloads.

## Photo → chat → approval → publication

See ASSISTANT-INSTRUCTIONS.md for the exact workflow and guardrails. The intended minimum input is a clear product photo, MXN price, and unit count. Confirm unreadable brand/name/size/shade and any relevant condition or expiry information. Photo retouching must preserve the actual package and label. No real product photo was supplied in this build, so no real listing or AI-cleaned sales image has been generated.

The local service provides inventory and approval behavior. The ChatGPT account connection, public hosting, and automatic image generation are still not configured. Do not promise a free shared chat or a particular paid plan will publish directly without testing its supported tool connection. New custom app/MCP integration should wrap the catalog methods with account-bound authentication; the REST routes are an implementation base, not a completed MCP server.

## Production connection still required

1. Confirm the existing Namecheap hosting plan's supported application runtime. Static hosting alone cannot run this service. Keep the public shop on the existing domain and route `/api/` to a supported private service, or implement the equivalent storage API in the host's supported runtime. Do not upload server.py to public_html expecting it to run.
2. Deploy behind HTTPS using a supported production app server, restrictive authorization, request limits, persistent database/media storage and backups. Keep database and credentials outside the public web root. Introduce per-user identity/OAuth for more than one administrative user; do not share the pilot bearer key broadly.
3. Verify Gaby's ChatGPT account supports a private custom app connection; install and test authenticated tools and file transfer. A shared conversation alone is not an authorization mechanism. Do not use a public shared GPT with a merchant-wide secret.
4. Run one real product through photo review, draft, exact-revision approval, public listing, WhatsApp inquiry, sale confirmation, sold-out, hide, and restock. Verify image cleanup and label accuracy.
5. Confirm payment/delivery/return information and actual inventory with Gaby. Approve the first real listings. Remove staging noindex metadata only for the approved public shop. Demo files and admin demo links should not be included in the public launch package.
6. Put final non-preview Shop links into both languages' production navigation only after the production catalog route works. The staging navigation currently intentionally links to sample mode.

No automatic payment collection, stock reservation, stock decrement from WhatsApp, or checkout has been implemented or implied.
