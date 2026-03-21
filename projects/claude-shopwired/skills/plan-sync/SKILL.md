# /plan-sync — Sync Setup Planning Skill

Trigger: `/plan-sync`, "set up sync", "configure integration", "deploy edge functions"

## Purpose
Plan and execute the full setup of ShopWired-GHL sync infrastructure. Walks through each step interactively.

## Setup Workflow

### Step 1: Verify Environment
- Check that all required env vars are set: `GHL_API_KEY`, `SHOPWIRED_API_KEY`, `SHOPWIRED_API_SECRET`
- Verify GHL API connectivity: run `ghl_list_products.sh`
- Verify ShopWired API connectivity: run `sw_list_products.sh`

### Step 2: Database Setup
- Run `001_create_mapping_tables.sql` in Supabase SQL Editor
- Verify tables exist: `customer_map`, `product_map`, `sync_logs`
- Check RLS policies are enabled

### Step 3: Configure Supabase Secrets
Set these via Supabase Dashboard > Project Settings > Edge Functions > Secrets:
```
SHOPWIRED_API_KEY=<from ShopWired Private App>
SHOPWIRED_API_SECRET=<from ShopWired Private App>
SHOPWIRED_WEBHOOK_SECRET=<generate a random string>
GHL_API_KEY=<your GHL Private Integration Token>
GHL_LOCATION_ID=<your GHL location ID>
```

Or via CLI:
```bash
supabase secrets set SHOPWIRED_API_KEY=xxx SHOPWIRED_API_SECRET=xxx SHOPWIRED_WEBHOOK_SECRET=xxx GHL_API_KEY=xxx GHL_LOCATION_ID=xxx --project-ref rkibpzmsmrskoxqoheuf
```

### Step 4: Deploy Edge Functions
```bash
cd supabase
supabase functions deploy sw-customer-sync --no-verify-jwt --project-ref rkibpzmsmrskoxqoheuf
supabase functions deploy sw-product-sync --no-verify-jwt --project-ref rkibpzmsmrskoxqoheuf
supabase functions deploy ghl-product-export --project-ref rkibpzmsmrskoxqoheuf
```

### Step 5: Register ShopWired Webhooks
```bash
bash .claude/skills/sync/scripts/sw_register_webhook.sh \
  --event customer.created \
  --url https://rkibpzmsmrskoxqoheuf.supabase.co/functions/v1/sw-customer-sync

bash .claude/skills/sync/scripts/sw_register_webhook.sh \
  --event customer.updated \
  --url https://rkibpzmsmrskoxqoheuf.supabase.co/functions/v1/sw-customer-sync

bash .claude/skills/sync/scripts/sw_register_webhook.sh \
  --event product.created \
  --url https://rkibpzmsmrskoxqoheuf.supabase.co/functions/v1/sw-product-sync

bash .claude/skills/sync/scripts/sw_register_webhook.sh \
  --event product.updated \
  --url https://rkibpzmsmrskoxqoheuf.supabase.co/functions/v1/sw-product-sync
```

### Step 6: Test
1. **Customer sync test:** Create a test customer in ShopWired. Check GHL contacts and `customer_map` table.
2. **Product export test:** Invoke `ghl-product-export` function. Check ShopWired products and `product_map` table.
3. **Monitoring:** Query `sync_logs` for recent events:
   ```sql
   SELECT * FROM sync_logs ORDER BY created_at DESC LIMIT 20;
   ```

### Step 7: Verify and Log
- Confirm all webhooks registered: run `sw_list_webhooks.sh`
- Confirm all Edge Functions deployed: check Supabase Dashboard
- Log setup completion in `sync_log.md`

## Troubleshooting
- **Edge Function not receiving webhooks:** Check the function URL matches what was registered. Check Supabase logs: `supabase functions logs sw-customer-sync --project-ref rkibpzmsmrskoxqoheuf`
- **HMAC verification failing:** Confirm `SHOPWIRED_WEBHOOK_SECRET` matches what ShopWired is using to sign payloads
- **GHL 401:** Token expired, update `GHL_API_KEY` in Supabase secrets
- **ShopWired 401:** Check API key/secret pair, ensure Private App is still active
