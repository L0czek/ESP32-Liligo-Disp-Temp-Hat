---
name: tme-search
description: Use when picking electronic components for this PCB project — finding a part on TME (Transfer Multisort Elektronik, tme.eu) by category + parameter filters (e.g. "cheapest 200Ω 1/4W THT resistor in stock"), comparing prices, checking stock, or browsing the api.tme.eu v2 catalog. Triggers on mentions of TME, "find a part", "BOM", or any part-spec query that names a value and a package.
---

# Searching the TME catalog (API v2)

REST API at `https://api.tme.eu/` documented at <https://api-doc.tme.eu/v2>. Auth is OAuth2 client_credentials with a 5-minute Bearer token. A ready-to-use helper is at `.claude/skills/tme-search/tme.py` — it handles OAuth (with on-disk token cache + auto-refresh), query encoding, and pagination. Use it; don't reimplement.

By default it returns **in-stock parts sorted cheapest-first**, matching how we build BOMs.

## Credentials

`TME_TOKEN` (50-char) + `TME_APP_SECRET` (20-char), from env vars or auto-loaded from `.claude/skills/tme-search/.env` (gitignored). Register at <https://developers.tme.eu/en/dev>. Defaults: `Country=PL`, `Language=pl`, `Currency=PLN`.

## Primary workflow: faceted browsing

This is how to use TME 90% of the time. Free-text matches the catalog poorly; everything is organised by **category → parameter facets**, mirroring the website.

```bash
# 1. Find the category id by name (responses are in Polish since Language=pl)
./tme.py categories --name "rezystory tht"
# Output (tab-separated): <id>\t<full path>  (<count> products)
# e.g. 112312    Elementy pasywne > Rezystory > Rezystory THT  (15105 products)

# 2. Discover filter parameters + value ids inside that category
./tme.py search-params --category 112312
# Prints, per parameter: id, name, then <ValueId>\t<label>  (<count>)
# e.g. under "Rezystancja" (id=38) you'll find 200Ω = 1436632
#      under "Moc"        (id=36) you'll find 0,25W = 1436573

# 3. Search the category with --param PARAM_ID:VALUE_ID (repeat per filter).
#    Defaults: in-stock only, sort=cheapest. --limit 1-100 (default 20).
./tme.py search --category 112312 --param 38:1436632 --param 36:1436573 --limit 5

# 4. Confirm live prices + stock for the top 3-5 Symbols
./tme.py data MF0W4FF0201B2 CF1/4W-200R 1/4W200R
```

The `data` output gives the full quantity-break ladder per symbol (`100@0.03766, 500@0.02583, 1000@0.01946, ...`) plus a `stock_quantity` and the price type (`GROSS PLN` = with VAT). Pick the symbol whose price at *your* target quantity is lowest with enough stock — `sort=cheapest` ranks by the first quantity break, which can mislead at low or very high volumes.

Both `search` and `data` print a TME product-page URL under each row: `https://www.tme.eu/{country}/details/{symbol}/`. Slashes in symbols slugify to `_` (`CF1/4W-200R` → `…/CF1_4W-200R/`); the percent-encoded `%2F` form does not resolve.

## Other commands

```bash
./tme.py search --phrase "ne555"                  # free-text (rare)
./tme.py search --category 112312 --all-stock     # include out-of-stock
./tme.py search --category 112312 --sort relevance --page 2
./tme.py search --category 112312 --param 38:1436632 38:1436578   # multiple values per param

./tme.py details <Symbol> [<Symbol> ...]          # GET /products
./tme.py parameters <Symbol>                      # GET /products/parameters (all parameter values for a symbol)
./tme.py symbols --category 112312 --limit 1000   # list raw symbol names in a category
./tme.py categories --tree                        # full tree (huge)

./tme.py search --category 112312 --dry-run       # show the request without sending
./tme.py auth-refresh                             # force a fresh access token
./tme.py call GET /utils/languages                # escape hatch for any v2 endpoint
```

Sort aliases: `cheapest` (default) → `PRICE_FIRST_QUANTITY asc`, `expensive`, `relevance` → `ACCURACY desc`, `symbol`, `in-stock` → `AVAILABLE_IN_STOCK_FIRST desc`.

## Things that will bite you

- **Never invent `Symbol` values.** TME symbols are catalog-internal (e.g. `MF0W4FF0201B2`, not the manufacturer P/N you'd see on Digi-Key). Always copy from a real `search` result.
- **`tme.eu` 403 ≠ broken URL.** The storefront sits behind bot protection and will 403 nearly any automated request (curl, WebFetch, etc.), regardless of UA. Do **not** conclude from a 403 that a URL is wrong — verify via the API (`./tme.py data <symbol>`) instead, or ask the user to load it in their browser.
- **Localisation.** With `Language=pl` the category and parameter names come back in Polish (`Rezystory THT`, `Rezystancja`, `Moc`). Use those substrings with `--name`. Switch to English for any single call with `--language en`.
- **Token cache.** `.token-cache.json` (gitignored, mode 0600) holds the Bearer for ~5 min and a refresh_token for re-issuing. If you ever see persistent `auth failed`, run `./tme.py auth-refresh`.
- **Quantity-break trap.** `sort=cheapest` uses TME's `PRICE_FIRST_QUANTITY` — the price at the *smallest* sellable quantity. For commodity parts (SMD R/C) full reels (MOQ 4000+) dominate the first pages, while MOQ=1–10 offers (e.g. Yageo `RC1206*`, Vishay `CRCW*FKTABC`) rank near the bottom despite being 10-20× cheaper *in total* at prototype quantities. Pull `data` for the top ~20 candidates and compare the total cost of obtaining your real BOM quantity (`max(MOQ, need) × unit price at that tier`), not the unit price. `details` returns `minimal_amount`/`multiples` to confirm a low MOQ is real.
- **Search response has no live prices.** Search → `data` pipeline is mandatory for any real pricing question.
- **`--dry-run` writes to stderr.** Stdout stays clean for piping; redirect 2>&1 if you want to see it via `| head`.
- **No `/v2/` URL prefix.** All paths are bare: `/products/search`, `/products/data`, `/auth/token`. v2 is a host-level version, not a path segment.

## v2 endpoints the helper covers

`POST /auth/token` (OAuth), `GET /products/search`, `GET /products/data`, `GET /products`, `GET /products/parameters`, `GET /products/symbols`, `GET /products/categories/{list,tree}`. For anything else (`/products/manufacturers`, `/products/files`, `/products/related`, `/products/similar`, `/utils/*`), use `./tme.py call GET /<path> key=value …`.
