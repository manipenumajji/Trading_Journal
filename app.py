import os
import threading
from datetime import datetime

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, jsonify
from dotenv import load_dotenv

from database import (
    initialize_database,
    add_trade,
    get_all_trades,
    get_dashboard_stats,
    get_recent_trades,
    get_trade_by_id,
    delete_trade,
    get_analytics_data,
    log_sync,
    get_last_sync,
)
from sync import sync_trades, test_connection

# ── Init ──────────────────────────────────────────────────────────────────────
load_dotenv()
app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

initialize_database()


# ── Helpers ───────────────────────────────────────────────────────────────────

def save_image(file):
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return filename
    return None


def get_api_keys():
    """Read keys from .env at runtime so changes take effect without restart."""
    load_dotenv(override=True)
    return (
        os.getenv("COINDCX_API_KEY",    ""),
        os.getenv("COINDCX_API_SECRET", ""),
    )


# ── Background auto-sync (every 15 min) ──────────────────────────────────────

def _run_sync():
    key, secret = get_api_keys()
    if not key or not secret:
        print("[scheduler] No API keys set — skipping auto-sync.")
        return
    print(f"[scheduler] Auto-sync starting at {datetime.now():%H:%M:%S}")
    result = sync_trades(key, secret)
    log_sync(result["imported"], result["skipped"], result["errors"])


def start_scheduler():
    """Start a simple background thread that syncs every 15 minutes."""
    import time

    def loop():
        while True:
            try:
                _run_sync()
            except Exception as e:
                print(f"[scheduler] Error: {e}")
            time.sleep(15 * 60)   # 15 minutes

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print("[scheduler] Auto-sync thread started (every 15 min).")


start_scheduler()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    stats         = get_dashboard_stats()
    recent_trades = get_recent_trades()
    last_sync     = get_last_sync()
    return render_template(
        "index.html",
        stats=stats,
        recent_trades=recent_trades,
        last_sync=last_sync,
    )


@app.route("/add_trade", methods=["GET", "POST"])
def add_trade_page():
    if request.method == "POST":
        before_image = save_image(request.files.get("before_image"))
        after_image  = save_image(request.files.get("after_image"))
        add_trade(
            request.form["symbol"],
            request.form["side"],
            float(request.form["entry_price"]),
            float(request.form["exit_price"]),
            float(request.form["quantity"]),
            request.form.get("strategy", ""),
            request.form.get("timeframe", ""),
            request.form.get("emotion", ""),
            request.form.get("notes", ""),
            before_image,
            after_image,
            trade_grade=request.form.get("trade_grade", ""),
            trade_date=request.form.get("trade_date", ""),
        )
        return redirect("/")
    return render_template("add_trade.html")


@app.route("/trades")
def trades_page():
    trades = get_all_trades()
    return render_template("trades.html", trades=trades)


@app.route("/analytics")
def analytics_page():
    data = get_analytics_data()
    return render_template("analytics.html", data=data)


@app.route("/delete_trade/<int:trade_id>")
def delete_trade_page(trade_id):
    delete_trade(trade_id)
    return redirect("/trades")


@app.route("/trade/<int:trade_id>")
def trade_details(trade_id):
    trade = get_trade_by_id(trade_id)
    return render_template("trade_details.html", trade=trade)


# ── Settings ──────────────────────────────────────────────────────────────────

@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    saved   = False
    key, _  = get_api_keys()
    masked  = ("•" * 20 + key[-4:]) if len(key) > 4 else ""

    if request.method == "POST":
        new_key    = request.form.get("api_key",    "").strip()
        new_secret = request.form.get("api_secret", "").strip()

        if new_key and new_secret:
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            with open(env_path, "w") as f:
                f.write(f"COINDCX_API_KEY={new_key}\n")
                f.write(f"COINDCX_API_SECRET={new_secret}\n")
            load_dotenv(override=True)
            saved  = True
            masked = "•" * 20 + new_key[-4:]

    last_sync = get_last_sync()
    return render_template(
        "settings.html",
        saved=saved,
        masked_key=masked,
        last_sync=last_sync,
    )


# ── API: Test connection ──────────────────────────────────────────────────────

@app.route("/api/test_connection", methods=["POST"])
def api_test_connection():
    key, secret = get_api_keys()
    if not key or not secret:
        return jsonify({"ok": False, "message": "No API keys saved yet."})
    result = test_connection(key, secret)
    return jsonify(result)


# ── API: Manual sync ──────────────────────────────────────────────────────────

@app.route("/api/sync", methods=["POST"])
def api_sync():
    key, secret = get_api_keys()
    if not key or not secret:
        return jsonify({
            "ok": False,
            "message": "API keys not set. Go to Settings first."
        })
    try:
        result = sync_trades(key, secret)
        log_sync(result["imported"], result["skipped"], result["errors"])
        return jsonify({
            "ok":       True,
            "imported": result["imported"],
            "skipped":  result["skipped"],
            "errors":   result["errors"],
            "message":  f"✓ Imported {result['imported']} new trades, skipped {result['skipped']} duplicates.",
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True)