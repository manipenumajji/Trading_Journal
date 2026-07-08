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
)

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
# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    stats         = get_dashboard_stats()
    recent_trades = get_recent_trades()
    return render_template(
        "index.html",
        stats=stats,
        recent_trades=recent_trades,
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


if __name__ == "__main__":
    app.run(debug=True)