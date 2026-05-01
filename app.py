import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import (
    init_db, get_db, get_expenses_for_user, get_expense_stats,
    get_top_category, get_category_breakdown
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-spendly")

with app.app_context():
    init_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm]):
            flash("All fields are required.", "error")
            return render_template("register.html")
        if "@" not in email:
            flash("Enter a valid email address.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            conn.close()
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        with conn:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
        conn.close()

        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("All fields are required.", "error")
            return render_template("login.html")

        conn = get_db()
        user = conn.execute(
            "SELECT id, name, password FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"]   = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    today = date.today()
    default_start = today.replace(day=1).isoformat()
    default_end = today.isoformat()

    start_date = request.args.get("start_date", default_start)
    end_date = request.args.get("end_date", default_end)

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        if start > end:
            flash("Start date cannot be after end date.", "error")
            return redirect(url_for("profile"))
    except ValueError:
        return redirect(url_for("profile"))

    conn = get_db()

    user_row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if not user_row:
        conn.close()
        return redirect(url_for("login"))

    initials = "".join(word[0].upper() for word in user_row["name"].split())
    member_since = user_row["created_at"][:10] if user_row["created_at"] else "Unknown"

    expenses = get_expenses_for_user(conn, user_id, start_date, end_date)
    stats_row = get_expense_stats(conn, user_id, start_date, end_date)
    top_cat = get_top_category(conn, user_id, start_date, end_date)
    categories_data = get_category_breakdown(conn, user_id, start_date, end_date)

    conn.close()

    total_spent = stats_row["total_spent"]
    tx_count = stats_row["tx_count"]
    top_category = top_cat["name"] if top_cat else "None"

    formatted_expenses = [
        {
            "date": exp["date"],
            "description": exp["description"],
            "category": exp["category"],
            "amount": f"{exp['amount']:.2f}"
        }
        for exp in expenses
    ]

    if categories_data:
        max_amount = max(cat["total"] for cat in categories_data)
    else:
        max_amount = 1

    formatted_categories = [
        {
            "name": cat["name"],
            "amount": f"{cat['total']:.2f}",
            "percent": int((cat["total"] / max_amount * 100)) if max_amount > 0 else 0
        }
        for cat in categories_data
    ]

    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "initials": initials,
        "member_since": member_since,
    }

    stats = {
        "total": f"{total_spent:.2f}",
        "count": tx_count,
        "top_category": top_category,
    }

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        expenses=formatted_expenses,
        categories=formatted_categories,
        start_date=start_date,
        end_date=end_date,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5001)
