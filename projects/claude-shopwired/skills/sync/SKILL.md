# /sync — ShopWired-GHL Sync Skill

Trigger: `/sync`, "sync products", "sync customers", "run product export", "register webhooks"

## Purpose
Manage bidirectional data sync between ShopWired and GoHighLevel:
- **Products:** GHL -> ShopWired (batch export via Edge Function)
- **Customers:** ShopWired -> GHL (real-time via webhook + Edge Function)
- **Orders:** ShopWired -> GHL (future, via webhook)

## Workflow

### Customer Sync (ShopWired -> GHL)
1. ShopWired fires `customer.created` or `customer.updated` webhook
2. Supabase Edge Function `sw-customer-sync` receives the event
3. Maps SW customer fields to GHL contact fields
4. Upserts into GHL via `/contacts/upsert` (dedup by email)
5. Saves ID mapping in `customer_map` table
6. Logs the event in `sync_logs` table

### Product Sync (GHL -> ShopWired)
1. Trigger `ghl-product-export` Edge Function (manual or scheduled)
2. Fetches all GHL products via `/products?locationId=...`
3. For each product: check `product_map` for existing SW mapping
4. If mapped: update existing SW product via `PUT /products/{id}`
5. If new: create SW product via `POST /products`
6. Save/update mapping in `product_map` table
7. Log each sync event in `sync_logs`

### Product Sync (ShopWired -> GHL, via webhook)
1. ShopWired fires `product.created` or `product.updated` webhook
2. Supabase Edge Function `sw-product-sync` receives the event
3. Two-step GHL create: Product (name, desc) then Price (amount, sku, stock)
4. Saves mapping and logs event

## Scripts

| Script | Purpose |
|--------|---------|
| `resolve_location.sh` | Resolve location shorthand to GHL locationId |
| `sw_list_products.sh` | List ShopWired products |
| `sw_list_customers.sh` | List ShopWired customers |
| `sw_get_product.sh` | Get single ShopWired product by ID |
| `sw_create_product.sh` | Create a ShopWired product |
| `sw_register_webhook.sh` | Register a ShopWired webhook |
| `sw_list_webhooks.sh` | List registered ShopWired webhooks |
| `ghl_list_products.sh` | List GHL products |
| `ghl_list_contacts.sh` | List/search GHL contacts |
| `ghl_upsert_contact.sh` | Create or update a GHL contact |

## Environment Variables Required
- `GHL_API_KEY` — GHL Private Integration Token
- `GHL_VERSION` — API version (2021-07-28)
- `SHOPWIRED_API_KEY` — ShopWired Private App API key
- `SHOPWIRED_API_SECRET` — ShopWired Private App secret

## Supabase Edge Functions
- `sw-customer-sync` — Webhook receiver, no JWT (public endpoint)
- `sw-product-sync` — Webhook receiver, no JWT (public endpoint)
- `ghl-product-export` — Batch job, requires JWT (invoke via dashboard or curl with service key)

## Field Mapping

### Customer: ShopWired -> GHL
| ShopWired | GHL |
|-----------|-----|
| firstName / first_name | firstName |
| lastName / last_name | lastName |
| email | email |
| phone / telephone | phone |
| address.line1 | address1 |
| address.city | city |
| address.county | state |
| address.postcode | postalCode |
| address.country | country |
| company | companyName |

### Product: GHL -> ShopWired
| GHL | ShopWired |
|-----|-----------|
| name | title |
| description | description |
| prices[0].amount / 100 | price |
| prices[0].sku | sku |
| prices[0].availableQuantity | stock |
| image | images[0].url |

## Error Handling
- **401 (token expired):** Notify user to update API keys
- **429 (rate limit):** Wait 10s, retry once
- **Webhook signature invalid:** Return 401, log event
- **GHL upsert conflict:** Use upsert endpoint (handles dedup)
- **Partial batch failure:** Log successes, report failures, continue
