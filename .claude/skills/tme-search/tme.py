#!/usr/bin/env python3
"""TME API v2 client.

OAuth2 client_credentials: 50-char token + 20-char secret -> 5-min Bearer.
Access tokens are cached on disk and auto-refreshed.

Credentials: TME_TOKEN / TME_APP_SECRET env vars, or .env next to this script.
Register at https://developers.tme.eu/en/dev .

Usage:
    tme.py categories --name "tht resistor"
    tme.py search-params --category 113714
    tme.py search --category 113714 --param 47:6428 --param 35:6234
    tme.py search --phrase "ne555" --sort cheapest
    tme.py data SYMBOL1 SYMBOL2          # prices + stock (v2 /products/data)
    tme.py details SYMBOL1 SYMBOL2       # product details
    tme.py call GET /products/symbols country=PL category_id=113714
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

API_BASE = "https://api.tme.eu"
DEFAULT_COUNTRY = "PL"
DEFAULT_LANGUAGE = "pl"   # Accept-Language; lowercase per RFC
DEFAULT_CURRENCY = "PLN"

SORT_ALIASES = {
    "cheapest":  ("PRICE_FIRST_QUANTITY", "asc"),
    "expensive": ("PRICE_FIRST_QUANTITY", "desc"),
    "relevance": ("ACCURACY", "desc"),
    "symbol":    ("SYMBOL", "asc"),
    "in-stock":  ("AVAILABLE_IN_STOCK_FIRST", "desc"),
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_CACHE = os.path.join(SCRIPT_DIR, ".token-cache.json")


def _load_env_file():
    """Load TME_TOKEN / TME_APP_SECRET from .env next to this script."""
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):]
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'").strip('"')
                if key and key not in os.environ and val:
                    os.environ[key] = val
    except OSError:
        pass


_load_env_file()


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def product_url(symbol, country=DEFAULT_COUNTRY):
    """Public TME product page URL. Slashes in the symbol slugify to `_`
    (the percent-encoded `%2F` form does not resolve)."""
    slug = urllib.parse.quote(symbol.replace("/", "_"), safe="_")
    return f"https://www.tme.eu/{country.lower()}/details/{slug}/"


# ---------- OAuth ----------

def _read_token_cache():
    try:
        with open(TOKEN_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_token_cache(data):
    try:
        with open(TOKEN_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.chmod(TOKEN_CACHE, 0o600)
    except OSError:
        pass


def _fetch_token(token, secret, grant_type, refresh_token=None):
    body = {"grant_type": grant_type}
    if refresh_token:
        body["refresh_token"] = refresh_token
    encoded = urllib.parse.urlencode(body).encode("utf-8")
    basic = base64.b64encode(f"{token}:{secret}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(
        f"{API_BASE}/auth/token",
        data=encoded,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8"))
        except Exception:
            err = {"http_status": e.code, "reason": e.reason}
        die(f"Auth failed ({e.code}): {json.dumps(err, indent=2, ensure_ascii=False)}")


def get_access_token():
    token = os.environ.get("TME_TOKEN")
    secret = os.environ.get("TME_APP_SECRET")
    if not token or not secret:
        die(
            "Missing credentials. Set TME_TOKEN and TME_APP_SECRET (env or "
            ".claude/skills/tme-search/.env). Register at "
            "https://developers.tme.eu/en/dev"
        )

    cache = _read_token_cache() or {}
    now = int(time.time())
    skew = 15  # refresh slightly before expiry

    if cache.get("token_owner") == token:
        if cache.get("access_token") and cache.get("access_expires_at", 0) > now + skew:
            return cache["access_token"]
        if cache.get("refresh_token"):
            data = _fetch_token(token, secret, "refresh_token", cache["refresh_token"])
            cache.update({
                "access_token": data["access_token"],
                "access_expires_at": now + int(data.get("expires_in", 300)),
                "refresh_token": data.get("refresh_token", cache.get("refresh_token")),
                "token_owner": token,
            })
            _write_token_cache(cache)
            return cache["access_token"]

    data = _fetch_token(token, secret, "client_credentials")
    cache = {
        "access_token": data["access_token"],
        "access_expires_at": now + int(data.get("expires_in", 300)),
        "refresh_token": data.get("refresh_token"),
        "token_owner": token,
    }
    _write_token_cache(cache)
    return cache["access_token"]


# ---------- HTTP ----------

def _encode_query(params):
    """Render dict/list params as repeated-bracket query string used by TME v2.

    {"scope": ["products", "parameters"]} -> scope[]=products&scope[]=parameters
    {"sort": {"property": "X", "direction": "asc"}} -> sort[property]=X&sort[direction]=asc
    {"parameters": [{"id": 2, "values": [156]}]} -> parameters[0][id]=2&parameters[0][values][]=156
    {"filter": {"in_stock": True}} -> filter[in_stock]=true
    """
    out = []

    def walk(prefix, value):
        if isinstance(value, dict):
            for k, v in value.items():
                walk(f"{prefix}[{k}]", v)
        elif isinstance(value, list):
            # list-of-scalars: use [] suffix; list-of-dicts: use indexed
            if value and isinstance(value[0], dict):
                for i, item in enumerate(value):
                    walk(f"{prefix}[{i}]", item)
            else:
                for item in value:
                    walk(f"{prefix}[]", item)
        elif isinstance(value, bool):
            out.append((prefix, "true" if value else "false"))
        elif value is None:
            return
        else:
            out.append((prefix, str(value)))

    for k, v in params.items():
        walk(k, v)
    return "&".join(
        f"{urllib.parse.quote(k, safe='[]')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in out
    )


def request(method, path, params=None, *, language=DEFAULT_LANGUAGE, dry_run=False):
    params = params or {}
    query = _encode_query(params)
    url = f"{API_BASE}{path}"
    if query and method == "GET":
        url = f"{url}?{query}"

    if dry_run:
        print(f"{method} {url}", file=sys.stderr)
        print(f"Accept-Language: {language}", file=sys.stderr)
        print("Authorization: Bearer <token>", file=sys.stderr)
        return None

    access = get_access_token()
    headers = {
        "Authorization": f"Bearer {access}",
        "Accept-Language": language,
        "Accept": "application/json",
    }
    data = None
    if method != "GET":
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = query.encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            die(f"HTTP {e.code}: {e.reason}")
        die(f"API error ({e.code}): {json.dumps(body, indent=2, ensure_ascii=False)}")
    if body.get("status") and body["status"] != "OK":
        die(f"API returned status={body['status']}:\n{json.dumps(body, indent=2, ensure_ascii=False)}")
    return body


# ---------- commands ----------

def _build_search_params(args, *, include_scope=True):
    p = {"country": args.country}
    if args.phrase:
        p["phrase"] = args.phrase
    if args.category is not None:
        p["category_id"] = args.category
    if args.manufacturer is not None:
        p["manufacturer_id"] = args.manufacturer
    if include_scope:
        p["scope"] = list(args.scope)
    p["page"] = args.page
    p["limit"] = args.limit

    flt = {}
    if not args.all_stock:
        flt["in_stock"] = True
    for k in ("new_in_offer", "promoted", "sale"):
        if getattr(args, k.replace("-", "_"), False):
            flt[k] = True
    if flt:
        p["filter"] = flt

    sort_prop, sort_dir = SORT_ALIASES[args.sort]
    p["sort"] = {"property": sort_prop, "direction": sort_dir}

    if args.param:
        params_list = []
        # group by param-id; allow multiple values per param
        by_id = {}
        for kv in args.param:
            pid, val = kv.split(":", 1)
            by_id.setdefault(pid, []).append(val)
        for pid, vals in by_id.items():
            params_list.append({"id": pid, "values": vals})
        p["parameters"] = params_list
    return p


def cmd_search(args):
    if not args.phrase and args.category is None:
        die("Specify --category and/or --phrase. Use `categories --name <pat>` to find a category id.")
    params = _build_search_params(args)
    body = request("GET", "/products/search", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    if args.json:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    data = body.get("data", {})
    prods = (data.get("products") or {}).get("elements") or []
    counters = data.get("counters") or {}
    total = counters.get("total") if isinstance(counters, dict) else None
    print(f"# {total if total is not None else len(prods)} hits — page {args.page} (showing {len(prods)})")
    for p in prods:
        sym = p.get("symbol", "")
        manu = (p.get("manufacturer") or {}).get("name", "")
        desc = (p.get("description") or "").replace("\n", " ")
        print(f"{sym}  [{manu}]")
        print(f"  {desc}")
        print(f"  {product_url(sym, args.country)}")
    print()
    print(f"# Next: tme.py data {' '.join(p.get('symbol','?') for p in prods[:5])}  # live prices+stock")


def cmd_search_params(args):
    """Get faceted filter values for a category (and/or phrase) — uses /products/search with scope[]=parameters."""
    if not args.phrase and args.category is None:
        die("Specify --category and/or --phrase.")
    # reuse search but with scope=parameters only, limit 1 (we only want facets)
    fake = argparse.Namespace(
        phrase=args.phrase, category=args.category, manufacturer=None,
        scope=["parameters"], page=1, limit=1, all_stock=True,
        new_in_offer=False, promoted=False, sale=False,
        sort="relevance", param=[], country=args.country,
    )
    params = _build_search_params(fake)
    body = request("GET", "/products/search", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    if args.json:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    facets = ((body.get("data") or {}).get("parameters") or {}).get("elements") or []
    if not facets:
        print("# No facets returned. Raw response:", file=sys.stderr)
        print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    for f in facets:
        pid = f.get("id")
        name = f.get("name", "")
        print(f"\n# Parameter id={pid}  name={name!r}")
        vals = f.get("values") or f.get("values_list") or []
        for v in vals:
            vid = v.get("id")
            value = v.get("value", v.get("name", ""))
            count = v.get("count", v.get("products_count", ""))
            count_str = f"  ({count} products)" if count != "" else ""
            print(f"  {vid}\t{value}{count_str}")


def cmd_data(args):
    """Prices + stock via /products/data."""
    params = {
        "country": args.country,
        "currency": args.currency,
        "symbols": args.symbols,
        "scope": list(args.scope),
    }
    if "delivery" in args.scope or "delivery_confirmed" in args.scope:
        if not args.amounts or len(args.amounts) != len(args.symbols):
            die("--amounts must match --symbols length when scope includes delivery")
        params["amounts"] = args.amounts
    body = request("GET", "/products/data", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    if args.json:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    elements = ((body.get("data") or {}).get("elements") or [])
    for el in elements:
        sym = el.get("symbol", "")
        stock_qty = el.get("stock_quantity", "")
        unit = (el.get("unit") or {}).get("short_name", "")
        prices_obj = el.get("prices") or {}
        tiers = prices_obj.get("elements") or []
        currency = prices_obj.get("currency", "")
        ptype = prices_obj.get("type", "")
        tier_str = ", ".join(f"{t.get('amount')}@{t.get('price')}" for t in tiers)
        print(f"{sym}  stock={stock_qty} {unit}  [{ptype} {currency}]")
        print(f"  {tier_str}")
        print(f"  {product_url(sym, args.country)}")


def cmd_details(args):
    params = {"country": args.country, "symbols": args.symbols}
    body = request("GET", "/products", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    print(json.dumps(body, indent=2, ensure_ascii=False))


def cmd_parameters(args):
    params = {"country": args.country, "symbols": args.symbols}
    body = request("GET", "/products/parameters", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    print(json.dumps(body, indent=2, ensure_ascii=False))


def cmd_symbols(args):
    params = {
        "country": args.country,
        "paginate": {"page": args.page, "limit": args.limit},
    }
    if args.category is not None:
        params["category_id"] = args.category
    if args.manufacturer is not None:
        params["manufacturer_id"] = args.manufacturer
    body = request("GET", "/products/symbols", params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    print(json.dumps(body, indent=2, ensure_ascii=False))


def cmd_categories(args):
    path = "/products/categories/tree" if (args.tree or args.name) else "/products/categories/list"
    params = {"country": args.country}
    if args.root_category is not None:
        params["root_category_id"] = args.root_category
    if args.manufacturer is not None:
        params["manufacturer_id"] = args.manufacturer
    body = request("GET", path, params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    if args.name:
        needle = args.name.lower()
        matches = []

        def walk(node, path_):
            if not isinstance(node, dict):
                return
            cid = node.get("id")
            cname = node.get("name", "")
            new_path = path_ + ([cname] if cname else [])
            if cname and needle in cname.lower():
                matches.append((cid, " > ".join(new_path), node.get("products_count")))
            for child in node.get("children") or []:
                walk(child, new_path)

        elements = (body.get("data") or {}).get("elements")
        roots = elements if isinstance(elements, list) else [elements] if elements else []
        for r in roots:
            walk(r, [])

        if matches:
            for cid, p, count in matches:
                count_str = f"  ({count} products)" if count is not None else ""
                print(f"{cid}\t{p}{count_str}")
        else:
            print(f"# No category matched /{args.name}/i. Raw response follows:", file=sys.stderr)
            print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    print(json.dumps(body, indent=2, ensure_ascii=False))


def cmd_auth_refresh(args):
    """Force a fresh token (drop cache and re-auth)."""
    try:
        os.remove(TOKEN_CACHE)
    except FileNotFoundError:
        pass
    print(get_access_token())


def cmd_call(args):
    params = {}
    for kv in args.params:
        k, _, v = kv.partition("=")
        params[k] = v
    body = request(args.method, args.path, params, language=args.language, dry_run=args.dry_run)
    if body is None:
        return
    print(json.dumps(body, indent=2, ensure_ascii=False))


# ---------- argparse ----------

def main():
    p = argparse.ArgumentParser(prog="tme.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dry-run", action="store_true",
                        help="Print the request to stderr without sending")
    common.add_argument("--country", default=DEFAULT_COUNTRY,
                        help=f"Country code (default: {DEFAULT_COUNTRY})")
    common.add_argument("--language", default=DEFAULT_LANGUAGE,
                        help=f"Accept-Language (default: {DEFAULT_LANGUAGE})")
    common.add_argument("--json", action="store_true", help="Print raw JSON response")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", parents=[common],
                        help="Faceted product search (default: in-stock, cheapest first)")
    sp.add_argument("--phrase", default="", help="Free-text query (optional with --category)")
    sp.add_argument("--category", type=int, help="Category id")
    sp.add_argument("--manufacturer", type=int, help="Manufacturer id")
    sp.add_argument("--all-stock", action="store_true",
                    help="Include out-of-stock (default: in-stock only)")
    sp.add_argument("--sort", choices=list(SORT_ALIASES), default="cheapest")
    sp.add_argument("--page", type=int, default=1)
    sp.add_argument("--limit", type=int, default=20, help="1-100, default 20")
    sp.add_argument("--param", action="append", default=[], metavar="PARAM_ID:VALUE_ID",
                    help="Faceted filter; repeat. Multiple values per param OK.")
    sp.add_argument("--scope", action="append", default=None,
                    choices=["products", "parameters", "counters"])
    sp.add_argument("--new-in-offer", action="store_true")
    sp.add_argument("--promoted", action="store_true")
    sp.add_argument("--sale", action="store_true")
    sp.set_defaults(func=lambda a: (setattr(a, "scope", a.scope or ["products", "counters"]), cmd_search(a)))

    sp = sub.add_parser("search-params", parents=[common],
                        help="Available faceted filter values for a category and/or phrase")
    sp.add_argument("--phrase", default="")
    sp.add_argument("--category", type=int)
    sp.set_defaults(func=cmd_search_params)

    sp = sub.add_parser("data", parents=[common],
                        help="Prices + stock (+ delivery) via /products/data")
    sp.add_argument("symbols", nargs="+")
    sp.add_argument("--currency", default=DEFAULT_CURRENCY)
    sp.add_argument("--scope", action="append", default=None,
                    choices=["prices", "stock", "delivery", "delivery_confirmed"])
    sp.add_argument("--amounts", type=int, nargs="+",
                    help="Required when scope includes delivery/delivery_confirmed")
    sp.set_defaults(func=lambda a: (setattr(a, "scope", a.scope or ["prices", "stock"]), cmd_data(a)))

    sp = sub.add_parser("details", parents=[common], help="GET /products (by symbols)")
    sp.add_argument("symbols", nargs="+")
    sp.set_defaults(func=cmd_details)

    sp = sub.add_parser("parameters", parents=[common], help="GET /products/parameters")
    sp.add_argument("symbols", nargs="+")
    sp.set_defaults(func=cmd_parameters)

    sp = sub.add_parser("symbols", parents=[common],
                        help="GET /products/symbols (list symbol names by category/manufacturer)")
    sp.add_argument("--category", type=int)
    sp.add_argument("--manufacturer", type=int)
    sp.add_argument("--page", type=int, default=1)
    sp.add_argument("--limit", type=int, default=1000)
    sp.set_defaults(func=cmd_symbols)

    sp = sub.add_parser("categories", parents=[common],
                        help="Category tree (--name finds id by partial match)")
    sp.add_argument("--name", help="Filter by case-insensitive substring")
    sp.add_argument("--root-category", type=int)
    sp.add_argument("--manufacturer", type=int)
    sp.add_argument("--tree", action="store_true", help="Use tree endpoint (auto when --name given)")
    sp.set_defaults(func=cmd_categories)

    sp = sub.add_parser("auth-refresh", parents=[common],
                        help="Drop the cached access token and fetch a fresh one")
    sp.set_defaults(func=cmd_auth_refresh)

    sp = sub.add_parser("call", parents=[common],
                        help="Escape hatch: METHOD /path key=value …")
    sp.add_argument("method", choices=["GET", "POST", "PUT", "DELETE"])
    sp.add_argument("path", help="e.g. /products/symbols")
    sp.add_argument("params", nargs="*")
    sp.set_defaults(func=cmd_call)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
