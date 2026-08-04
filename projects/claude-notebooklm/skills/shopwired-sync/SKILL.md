---
name: shopwired-sync
description: >-
  Sync ShopWired e-commerce data with GoHighLevel CRM. Syncs customers and
  newsletter subscribers to GHL contacts, imports orders as pipeline
  opportunities, recovers abandoned carts via email workflows, and polls events
  for real-time changes. Use when user says 'sync ShopWired', 'import customers
  to GHL', 'abandoned cart recovery', 'tag shopwired customers', or invokes
  /shopwired-sync. Do NOT use for writing blog posts or social content — use
  /blog or /distribute instead.
argument-hint: '"contacts" [--location ces] [--since 24h] [--dry-run]'
disable-model-invocation: true
---

# /shopwired-sync — ShopWired + GHL Integration Skill

> **Trigger:** User says `/shopwired-sync`, "sync ShopWired", "import customers to GHL", "abandoned cart recovery", "tag shopwired customers", or similar.

## Role

You synchronize ShopWired e-commerce data (customers, orders, abandoned carts, newsletter subscribers) with GoHighLevel CRM. You create/update GHL contacts, manage pipeline opportunities, and trigger recovery workflows for abandoned baskets.

---

## Constants

```
SW_SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/shopwired-sync/scripts
SW_REFS_DIR:    ${CLAUDE_PLUGIN_ROOT}/skills/shopwired-sync/references
SW_API_BASE:    https://api.ecommerceapi.uk/v1
GHL_API_BASE:   https://services.leadconnectorhq.com
SYNC_STATE_DIR: ~/.notebooklm/shopwired-sync
```

---

## Credentials

ShopWired uses HTTP Basic Auth (API key + secret). Store per-location:

```
# .env
SHOPWIRED_API_KEY_CES=your_api_key
SHOPWIRED_API_SECRET_CES=your_api_secret
```

The skill reads these via `locations.json` fields:
- `shopwiredApiKeyVar` — env var name for API key (e.g., `SHOPWIRED_API_KEY_CES`)
- `shopwiredApiSecretVar` — env var name for API secret (e.g., `SHOPWIRED_API_SECRET_CES`)

If these fields are missing from the location entry, the skill stops and asks the user to configure them.

---

## Subcommands

| Subcommand | Description | Script |
|---|---|---|
| `contacts` | Sync customers + newsletter subscribers to GHL contacts | `sw_sync_contacts.sh` |
| `orders` | Sync orders to GHL pipeline opportunities + tag contacts | `sw_sync_orders.sh` |
| `abandoned` | Fetch incomplete orders, create recovery contacts/tags | `sw_incomplete_orders.sh` |
| `events` | Poll ShopWired events since last sync | `sw_poll_events.sh` |
| `webhooks` | Register ShopWired webhooks for real-time sync | `sw_setup_webhooks.sh` |
| `status` | Show sync state (last run, counts) | Reads `SYNC_STATE_DIR` |

---

## Workflow

### Step 0: Resolve Location + Credentials

1. Parse `--location <shorthand>` (or use default from `locations.json`).
2. Resolve GHL credentials via standard `init.sh`.
3. Resolve ShopWired credentials from location entry:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/init.sh" "$@"

# Read ShopWired creds from locations.json
SW_KEY_VAR=$(jq -r --arg k "$LOCATION_KEY" \
  '.locations[$k].shopwiredApiKeyVar // empty' "$PWD/locations.json")
SW_SECRET_VAR=$(jq -r --arg k "$LOCATION_KEY" \
  '.locations[$k].shopwiredApiSecretVar // empty' "$PWD/locations.json")

if [[ -z "$SW_KEY_VAR" || -z "$SW_SECRET_VAR" ]]; then
  echo "Error: Add shopwiredApiKeyVar and shopwiredApiSecretVar to locations.json for '$LOCATION_KEY'" >&2
  exit 1
fi

SHOPWIRED_API_KEY="${!SW_KEY_VAR}"
SHOPWIRED_API_SECRET="${!SW_SECRET_VAR}"
```

4. All ShopWired API calls use: `curl -u "$SHOPWIRED_API_KEY:$SHOPWIRED_API_SECRET"`

### Step 1: Identify Subcommand

Parse the first positional argument:

```
/shopwired-sync contacts --location ces --since 24h
/shopwired-sync orders --location ces --dry-run
/shopwired-sync abandoned --location ces
/shopwired-sync events --location ces
/shopwired-sync webhooks --location ces --url https://...
/shopwired-sync status --location ces
```

If no subcommand, show available subcommands and ask.

---

### Subcommand: `contacts`

Syncs ShopWired customers + newsletter subscribers into GHL contacts.

```bash
bash "${SW_SCRIPTS_DIR}/sw_sync_contacts.sh" \
  --location <LOCATION> [--since 24h] [--dry-run] [--tag "shopwired"]
```

**Flow:**
1. Fetch ShopWired customers (`GET /customers?count=250&offset=0`, paginate).
2. Fetch newsletter subscribers (`GET /newsletter-subscribers?count=50&offset=0`, paginate).
3. Merge by email (subscribers get extra tag `sw-subscriber`).
4. For each unique email, search GHL contacts (`GET /contacts/?query=<email>`).
5. **If exists:** Update with latest ShopWired data, add `shopwired` tag.
6. **If new:** Create GHL contact with tags: `shopwired`, `sw-customer` (or `sw-subscriber`).
7. Write sync state to `SYNC_STATE_DIR/contacts_last_sync.json`.

**GHL Contact Fields Mapping:**
| ShopWired | GHL |
|---|---|
| `firstName` | `firstName` |
| `lastName` | `lastName` |
| `email` | `email` |
| `phone` | `phone` |
| `company` | `companyName` |
| — | `tags`: `["shopwired", "sw-customer"]` |
| customer.id | `customFields.shopwired_customer_id` |

**`--since` filter:** Only fetch customers created after the given time window (e.g., `24h`, `7d`). Converts to UNIX timestamp for the `from` query parameter.

**`--dry-run`:** Show what would be synced without making GHL API calls. Output a table of actions.

**Show user before executing:** "Found [N] ShopWired customers and [M] subscribers. [X] new to GHL, [Y] existing (will update). Proceed?"

---

### Subcommand: `orders`

Syncs ShopWired orders to GHL as pipeline opportunities and tags contacts.

```bash
bash "${SW_SCRIPTS_DIR}/sw_sync_orders.sh" \
  --location <LOCATION> [--since 24h] [--pipeline "shopwired-orders"]
```

**Flow:**
1. Fetch orders (`GET /orders?count=250&offset=0`, paginate, filter by `--since`).
2. For each order:
   a. Find/create GHL contact by customer email.
   b. Tag contact with order info: `sw-buyer`, `sw-order-<status>`.
   c. Create GHL opportunity in the specified pipeline.
3. If `--pipeline` doesn't exist yet, **ask user** if they want to create it with default stages: `New Order` > `Processing` > `Shipped` > `Delivered` > `Completed`.
4. Write sync state.

**GHL Opportunity Mapping:**
| ShopWired | GHL Opportunity |
|---|---|
| `reference` | `name`: "Order #<reference>" |
| `total` (pence / 100) | `monetaryValue` |
| `status` | `stageId` (mapped to pipeline stage) |
| `customer.email` | `contactId` (looked up) |

**Stage Mapping:**
| ShopWired Status | GHL Pipeline Stage |
|---|---|
| `pending` | New Order |
| `processing` | Processing |
| `shipped` | Shipped |
| `completed` | Completed |
| `cancelled` | Lost (mark opportunity as lost) |

---

### Subcommand: `abandoned`

Fetches incomplete orders (abandoned baskets) and creates recovery workflows.

```bash
bash "${SW_SCRIPTS_DIR}/sw_incomplete_orders.sh" \
  --location <LOCATION> [--since 24h] [--recover]
```

**Flow:**
1. Fetch incomplete orders (`GET /incomplete-orders?count=250&sort=date_desc`).
2. Filter out archived orders (`archived: true`).
3. For each incomplete order with a billing email:
   a. Find/create GHL contact.
   b. Tag with `sw-abandoned-cart`.
   c. Store cart details (products, total) in contact notes.
4. If `--recover` flag: trigger the `/newsletter` skill to send a recovery email.
5. Show user: "Found [N] abandoned carts ([M] with email). Total value: [sum]. [X] already tagged in GHL."

**Recovery email content** (generated from cart data):
- Subject: "You left something behind"
- Body: List of products with prices, total, and a call-to-action
- Uses brand voice from `BRAND_DOCS_DIR/email-voice.md`
- Sent via `/newsletter --tag "sw-abandoned-cart"`

---

### Subcommand: `events`

Polls ShopWired's Events API for changes since last sync.

```bash
bash "${SW_SCRIPTS_DIR}/sw_poll_events.sh" \
  --location <LOCATION> [--since 24h] [--subject-type order]
```

**Flow:**
1. Read last event ID from `SYNC_STATE_DIR/events_cursor.json`.
2. Fetch events (`GET /events?count=250`), filter by `--subject-type` if given.
3. Process each event by subject type:
   - `customer` — trigger contact sync for that customer
   - `order` — trigger order sync for that order
   - `newsletter_subscriber` — add/tag in GHL
   - `order_refund` — update GHL opportunity stage to "Refunded"
4. Save latest event ID as cursor.

**Supported subject types:** `product`, `category`, `brand`, `tag`, `customer`, `order`, `newsletter_subscriber`, `wishlist`, `sale`, `order_refund`, `stock_request`

---

### Subcommand: `webhooks`

Registers ShopWired webhooks for real-time sync.

```bash
bash "${SW_SCRIPTS_DIR}/sw_setup_webhooks.sh" \
  --location <LOCATION> --url "https://your-receiver.com/shopwired"
```

**Flow:**
1. List existing webhooks (`GET /webhooks`).
2. Show current registrations.
3. For each recommended topic, check if already registered:
   - `order.created`, `order.updated`
   - `customer.created`, `customer.updated`
   - `newsletter_subscriber.created`
4. Ask user which to register. Require HTTPS URL.
5. Create webhooks (`POST /webhooks`).
6. Verify each (`POST /webhooks/{id}/verify`).

---

## Flags Reference

| Flag | Applies To | Description |
|---|---|---|
| `--location <key>` | All | GHL + ShopWired location |
| `--since <window>` | contacts, orders, abandoned, events | Time filter: `1h`, `24h`, `7d`, `30d` |
| `--dry-run` | contacts, orders | Preview without writing to GHL |
| `--tag <name>` | contacts | Extra tag to apply (default: `shopwired`) |
| `--pipeline <name>` | orders | GHL pipeline name (default: `shopwired-orders`) |
| `--recover` | abandoned | Trigger recovery email via /newsletter |
| `--subject-type <type>` | events | Filter events by type |
| `--url <https://...>` | webhooks | Webhook receiver URL |

---

## Error Handling

| Error | Cause | Action |
|---|---|---|
| 401 from ShopWired | Bad API key/secret | Stop, tell user to check `.env` credentials |
| 401 from GHL | GHL token expired | Stop, tell user to refresh GHL API key |
| 429 from ShopWired | Rate limited (2 req/s) | Wait for `Retry-After` header, then retry |
| 429 from GHL | GHL rate limit | Wait 10s, retry |
| Missing `shopwiredApiKeyVar` | Not configured | Stop, show how to add to `locations.json` |
| No billing email on cart | Anonymous abandon | Skip, log count of skipped |
| Duplicate contact | Email already in GHL | Update instead of create |
| Pipeline not found | First run | Offer to create default pipeline |

---

## Sync State

State files in `~/.notebooklm/shopwired-sync/<LOCATION_KEY>/`:

| File | Contents |
|---|---|
| `contacts_last_sync.json` | `{"timestamp": "...", "synced": 42, "created": 10, "updated": 32}` |
| `orders_last_sync.json` | `{"timestamp": "...", "synced": 15, "opportunities_created": 8}` |
| `abandoned_last_sync.json` | `{"timestamp": "...", "found": 7, "tagged": 5, "recovered": 3}` |
| `events_cursor.json` | `{"last_event_id": 12345, "timestamp": "..."}` |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading `locations.json` and resolving credentials
- Fetching data from ShopWired API (read-only)
- Reading sync state files
- Searching existing GHL contacts (lookup only)

**Ask before running:**
- Creating or updating GHL contacts
- Creating GHL pipeline or opportunities
- Tagging contacts in GHL
- Registering webhooks in ShopWired
- Sending recovery emails (delegates to `/newsletter`)
- Writing to sync state files

---

## Examples

**Sync all customers:**
```
/shopwired-sync contacts --location ces
```

**Sync recent orders (last 24 hours):**
```
/shopwired-sync orders --location ces --since 24h
```

**Preview abandoned carts without acting:**
```
/shopwired-sync abandoned --location ces --dry-run
```

**Recover abandoned carts with email:**
```
/shopwired-sync abandoned --location ces --recover
```

**Poll events since last check:**
```
/shopwired-sync events --location ces
```

**Set up real-time webhooks:**
```
/shopwired-sync webhooks --location ces --url https://hooks.example.com/sw
```

**Check sync status:**
```
/shopwired-sync status --location ces
```
