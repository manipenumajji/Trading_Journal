import hmac
import hashlib
import json
import time
import requests
import os
from database import get_connection
from datetime import datetime

BASE_URL = "https://api.coindcx.com"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _sign(secret: str, body: dict) -> tuple[str, str]:
    """Return (json_body, signature)"""
    body_str = json.dumps(body, separators=(",", ":"))
    sig = hmac.new(
        secret.encode("utf-8"),
        body_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return body_str, sig


def _headers(key: str, sig: str) -> dict:
    return {
        "Content-Type":   "application/json",
        "X-AUTH-APIKEY":  key,
        "X-AUTH-SIGNATURE": sig,
    }


def _post(endpoint: str, key: str, secret: str, body: dict) -> dict | None:
    body_str, sig = _sign(secret, body)
    try:
        r = requests.post(
            BASE_URL + endpoint,
            data=body_str,
            headers=_headers(key, sig),
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"[sync] API error on {endpoint}: {e}")
        return None


# ── Connection Test ───────────────────────────────────────────────────────────

def test_connection(key: str, secret: str) -> dict:
    body = {"timestamp": int(time.time() * 1000)}
    body_str, sig = _sign(secret, body)
    
    response = requests.post(
        BASE_URL + "/exchange/v1/users/info",
        data=body_str,
        headers=_headers(key, sig),
        timeout=10
    )
    
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    
    data = response.json()
    if data and "coindcx_id" in data:
        return {"ok": True, "message": f"Connected as {data.get('email', 'unknown')}"}
    return {"ok": False, "message": "Invalid API keys or CoinDCX unreachable"}


# ── DB helpers ────────────────────────────────────────────────────────────────

def _already_exists(cursor, coindcx_id: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM trades WHERE coindcx_id = ?", (coindcx_id,)
    )
    return cursor.fetchone() is not None


def _insert_trade(cursor, t: dict):
    cursor.execute("""
        INSERT INTO trades (
            symbol, side,
            entry_price, exit_price, quantity,
            pnl,
            strategy, timeframe, emotion,
            notes, trade_date,
            before_image, after_image,
            trade_grade, source, coindcx_id
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        t["symbol"],
        t["side"],
        t["entry_price"],
        t["exit_price"],
        t["quantity"],
        round(t["pnl"], 2),
        t.get("strategy", ""),
        t.get("timeframe", ""),
        "",             # emotion – user fills later
        t.get("notes", "Auto-imported from CoinDCX"),
        t.get("trade_date", ""),
        None,           # before_image
        None,           # after_image
        "",             # trade_grade – user fills later
        "coindcx",
        t["coindcx_id"],
    ))


# ── Spot Orders ───────────────────────────────────────────────────────────────

def _fetch_futures_trades(key: str, secret: str) -> list[dict]:
    body = {
        "timestamp": int(time.time() * 1000),
        "stage": "all",
        "page": "1",
        "size": "100"
    }
    data = _post(
        "/exchange/v1/derivatives/futures/positions/transactions",
        key, secret, body
    )

    print("=== RAW API RESPONSE ===")
    print(type(data), repr(data)[:500])
    print("========================")

    if not data or not isinstance(data, list):
        print(f"[sync] Futures API returned unexpected: {type(data)} — {repr(data)[:200]}")
        return []

    print(f"[sync] Got {len(data)} raw futures transactions")
    if len(data) > 0:
        print("=== FIRST TRANSACTION ===")
        print(json.dumps(data[0], indent=2))
        print("=========================")

    results = []
    for t in data:
        trade_id   = str(t.get("parent_id", ""))
        pair       = t.get("pair", "")
        symbol     = pair.replace("B-", "").replace("_", "/") if pair else ""
        amount     = float(t.get("amount", 0) or 0)
        fee        = float(t.get("fee_amount", 0) or 0)
        pnl        = round(amount - fee, 4)
        ts         = t.get("created_at", 0)
        trade_date = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d") if ts else ""
        stage      = t.get("stage", "")

        if stage == "funding":
            continue
        if not trade_id:
            continue

        results.append({
            "coindcx_id":  f"fut_{trade_id}",
            "symbol":      symbol,
            "side":        "Long",
            "entry_price": 0,
            "exit_price":  float(t.get("price_in_usdt", 0) or 0),
            "quantity":    0,
            "pnl":         pnl,
            "trade_date":  trade_date,
            "strategy":    "Futures",
            "notes":       f"Futures closed | gross: {amount} | fee: {fee} | pair: {pair}",
        })

    print(f"[sync] Parsed {len(results)} futures trades after filtering")
    return results
# ── Main Sync ─────────────────────────────────────────────────────────────────

def sync_trades(key: str, secret: str) -> dict:


    futures_trades = _fetch_futures_trades(key, secret)

    all_trades =  futures_trades
    

    imported = 0
    skipped = 0
    errors = []

    conn = get_connection()
    cursor = conn.cursor()

    for t in all_trades:
        try:
            if _already_exists(cursor, t["coindcx_id"]):
                skipped += 1
                continue

            _insert_trade(cursor, t)
            imported += 1

        except Exception as e:
            errors.append(str(e))

    conn.commit()
    conn.close()

    print(
        f"[sync] Done — imported: {imported}, "
        f"skipped: {skipped}, errors: {len(errors)}"
    )

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors
    }

