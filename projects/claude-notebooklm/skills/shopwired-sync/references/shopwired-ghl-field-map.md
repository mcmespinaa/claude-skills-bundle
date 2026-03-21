# ShopWired to GHL Field Mapping Reference

## Contact Sync

| ShopWired Customer | GHL Contact | Notes |
|---|---|---|
| `firstName` | `firstName` | Direct map |
| `lastName` | `lastName` | Direct map |
| `email` | `email` | Lowercase, used as dedup key |
| `phone` | `phone` | Direct map |
| `company` | `companyName` | Field name differs |
| `id` | `customFields.shopwired_customer_id` | For cross-reference |
| — | `tags` | `shopwired`, `sw-customer` |

## Newsletter Subscriber Sync

| ShopWired Subscriber | GHL Contact | Notes |
|---|---|---|
| `emailAddress` | `email` | Field name differs |
| `name` | `firstName` | Single name field, no split |
| `createdAt` | — | Not mapped (info only) |
| — | `tags` | `shopwired`, `sw-subscriber` |

## Order to Opportunity Mapping

| ShopWired Order | GHL Opportunity | Notes |
|---|---|---|
| `reference` | `name` | Prefixed: "Order #123" |
| `total` | `monetaryValue` | Pence to pounds: divide by 100 if > 1000 |
| `status` | `stageId` | Mapped via stage table below |
| `customer.email` | `contactId` | Looked up by email |
| `createdAt` | — | Not mapped (GHL uses own timestamp) |

### Pipeline Stage Mapping

| ShopWired Status | GHL Stage Name | GHL Opportunity Status |
|---|---|---|
| `pending` | New Order | open |
| `processing` | Processing | open |
| `shipped` | Shipped | open |
| `delivered` | Delivered | open |
| `completed` | Completed | won |
| `cancelled` | Cancelled | lost |

Default pipeline name: `shopwired-orders`

## Abandoned Cart (Incomplete Order) Mapping

| ShopWired Incomplete Order | GHL Contact | Notes |
|---|---|---|
| `billingAddress.emailAddress` | `email` | Dedup key |
| `billingAddress.name` | `firstName` / `lastName` | Split on first space |
| `total` | Contact note | Cart value in note body |
| `products[].title` | Contact note | Product list in note body |
| `id` | Contact note | Cart reference number |
| — | `tags` | `shopwired`, `sw-abandoned-cart` |

## Event Subject Types

| ShopWired Event `subjectType` | Sync Action |
|---|---|
| `customer` | Trigger contact sync for `subjectId` |
| `order` | Trigger order sync for `subjectId` |
| `newsletter_subscriber` | Add/tag subscriber in GHL |
| `order_refund` | Update opportunity to "Refunded" stage |
| `product` | Info only (no GHL action) |
| `category` | Info only |
| `brand` | Info only |
| `wishlist` | Future: intent signals for campaigns |
| `stock_request` | Info only |

## ShopWired API Quirks

- **Prices in pence:** 9999 = £99.99. Divide by 100 for display/GHL.
- **Product field is `title`**, not `name`.
- **Status via `active` boolean** (0/1), not a status string.
- **Pagination:** `offset` + `count` (max 250), NOT `page` + `limit`.
- **Search:** Separate `/products/search` endpoint, not a query param.
- **Subscriber email field:** `emailAddress`, not `email`.
- **Incomplete order email:** `billingAddress.emailAddress`.

## Credential Configuration

Add to `locations.json` for each location:

```json
{
  "ces": {
    "locationId": "...",
    "apiKeyVar": "GHL_API_KEY_CES",
    "shopwiredApiKeyVar": "SHOPWIRED_API_KEY_CES",
    "shopwiredApiSecretVar": "SHOPWIRED_API_SECRET_CES",
    ...
  }
}
```

Add to `.env`:

```
SHOPWIRED_API_KEY_CES=your_shopwired_api_key
SHOPWIRED_API_SECRET_CES=your_shopwired_api_secret
```
