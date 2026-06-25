import sqlite3
from datetime import datetime

DB_NAME = "trades.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades(
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol        TEXT NOT NULL,
        side          TEXT NOT NULL,
        entry_price   REAL NOT NULL,
        exit_price    REAL NOT NULL,
        quantity      REAL NOT NULL,
        pnl           REAL NOT NULL,
        strategy      TEXT,
        timeframe     TEXT,
        emotion       TEXT,
        notes         TEXT,
        trade_date    TEXT,
        before_image  TEXT,
        after_image   TEXT
    )
    """)
    connection.commit()

    # ── Safe migrations ──
    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN trade_grade TEXT")
        connection.commit()
    except:
        pass

    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN source TEXT")
        connection.commit()
    except:
        pass

    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN coindcx_id TEXT")
        connection.commit()
    except:
        pass

    # ── Sync-log table ──
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sync_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        synced_at   TEXT NOT NULL,
        imported    INTEGER DEFAULT 0,
        skipped     INTEGER DEFAULT 0,
        errors      TEXT
    )
    """)
    connection.commit()
    connection.close()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT pnl FROM trades")
    trades = cursor.fetchall()
    connection.close()

    if not trades:
        return {"total_trades": 0, "win_rate": 0.0,
                "total_pnl": 0.0, "avg_pnl": 0.0}

    pnls         = [t[0] for t in trades]
    total_trades = len(pnls)
    total_pnl    = round(sum(pnls), 2)
    wins         = len([p for p in pnls if p > 0])
    win_rate     = round((wins / total_trades) * 100, 2)
    avg_pnl      = round(total_pnl / total_trades, 2)

    return {
        "total_trades": total_trades,
        "win_rate":     win_rate,
        "total_pnl":    total_pnl,
        "avg_pnl":      avg_pnl,
    }


def get_recent_trades():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT symbol, side, pnl, source
        FROM trades
        ORDER BY id DESC
        LIMIT 10
    """)
    trades = cursor.fetchall()
    connection.close()
    return trades


# ── Add Trade (manual) ────────────────────────────────────────────────────────

def add_trade(
    symbol, side,
    entry_price, exit_price, quantity,
    strategy, timeframe, emotion,
    notes,
    before_image=None,
    after_image=None,
    trade_grade=None,
    trade_date=None,
):
    pnl = (exit_price - entry_price) * quantity if side == "Long" \
          else (entry_price - exit_price) * quantity

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO trades (
            symbol, side,
            entry_price, exit_price, quantity,
            pnl,
            strategy, timeframe, emotion,
            notes, trade_date,
            before_image, after_image,
            trade_grade, source
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        symbol, side,
        entry_price, exit_price, quantity,
        round(pnl, 2),
        strategy, timeframe, emotion,
        notes, trade_date,
        before_image, after_image,
        trade_grade, "manual",
    ))
    connection.commit()
    connection.close()


# ── Reads ─────────────────────────────────────────────────────────────────────

def get_all_trades():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id, symbol, side, pnl,
            strategy, emotion,
            trade_grade, trade_date,
            source
        FROM trades
        ORDER BY id DESC
    """)
    trades = cursor.fetchall()
    connection.close()
    return trades


def get_trade_by_id(trade_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM trades WHERE id=?", (trade_id,))
    trade = cursor.fetchone()
    connection.close()
    return trade


def delete_trade(trade_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM trades WHERE id=?", (trade_id,))
    connection.commit()
    connection.close()


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics_data():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT pnl, strategy, emotion, trade_date FROM trades ORDER BY id"
    )
    trades = cursor.fetchall()
    connection.close()

    if not trades:
        return None

    pnl_values = [t[0] for t in trades]
    strategies = [t[1] or "Unknown" for t in trades]
    emotions   = [t[2] or "Unknown" for t in trades]

    # Equity curve
    equity  = []
    running = 0
    for p in pnl_values:
        running += p
        equity.append(round(running, 2))

    wins   = len([p for p in pnl_values if p > 0])
    losses = len([p for p in pnl_values if p < 0])

    # Strategy map
    strategy_map = {}
    for i, s in enumerate(strategies):
        strategy_map.setdefault(s, {"count": 0, "pnl": 0})
        strategy_map[s]["count"] += 1
        strategy_map[s]["pnl"]   += pnl_values[i]
    for s in strategy_map:
        strategy_map[s]["pnl"] = round(strategy_map[s]["pnl"], 2)

    # Emotion map
    emotion_map = {}
    for i, e in enumerate(emotions):
        emotion_map.setdefault(e, 0)
        emotion_map[e] += pnl_values[i]
    for e in emotion_map:
        emotion_map[e] = round(emotion_map[e], 2)

    return {
        "equity":       equity,
        "pnl_values":   pnl_values,
        "wins":         wins,
        "losses":       losses,
        "strategy_map": strategy_map,
        "emotion_map":  emotion_map,
        "best_trade":   round(max(pnl_values), 2),
        "worst_trade":  round(min(pnl_values), 2),
        "total_pnl":    round(sum(pnl_values), 2),
        "win_rate":     round((wins / len(pnl_values)) * 100, 2),
        "total_trades": len(pnl_values),
    }


# ── Sync log ──────────────────────────────────────────────────────────────────

def log_sync(imported: int, skipped: int, errors: list):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO sync_log (synced_at, imported, skipped, errors)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        imported, skipped,
        "; ".join(errors) if errors else "",
    ))
    connection.commit()
    connection.close()


def get_last_sync():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT synced_at, imported, skipped
        FROM sync_log
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    connection.close()

    if not row:
        return None

    synced_at, imported, skipped = row
    return f"{synced_at} — {imported} imported, {skipped} skipped"