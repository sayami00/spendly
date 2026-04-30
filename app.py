import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import init_db, get_db

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
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name":         session.get("user_name", "Demo User"),
        "email":        "nitish@example.com",
        "member_since": "January 2025",
        "initials":     "".join(
            w[0].upper() for w in session.get("user_name", "Demo User").split()
        )[:2],
    }

    stats = {
        "total_spent":       "₹12,480",
        "transaction_count": 10,
        "top_category":      "Food",
    }

    transactions = [
        {"date": "28 Apr 2026", "description": "Lunch at Cafe",       "category": "Food",          "category_class": "cat-food",          "amount": "₹450"},
        {"date": "25 Apr 2026", "description": "Flight to Delhi",      "category": "Travel",        "category_class": "cat-travel",        "amount": "₹4,500"},
        {"date": "22 Apr 2026", "description": "Electricity bill",     "category": "Bills",         "category_class": "cat-bills",         "amount": "₹1,800"},
        {"date": "19 Apr 2026", "description": "Netflix subscription", "category": "Entertainment", "category_class": "cat-entertainment", "amount": "₹649"},
        {"date": "15 Apr 2026", "description": "Weekend market",       "category": "Groceries",     "category_class": "cat-groceries",     "amount": "₹1,182"},
        {"date": "10 Apr 2026", "description": "Dinner with family",   "category": "Food",          "category_class": "cat-food",          "amount": "₹780"},
        {"date": "07 Apr 2026", "description": "Movie tickets",        "category": "Entertainment", "category_class": "cat-entertainment", "amount": "₹600"},
        {"date": "03 Apr 2026", "description": "Internet plan",        "category": "Bills",         "category_class": "cat-bills",         "amount": "₹999"},
        {"date": "02 Apr 2026", "description": "Ola ride",             "category": "Travel",        "category_class": "cat-travel",        "amount": "₹320"},
        {"date": "01 Apr 2026", "description": "Grocery run",          "category": "Groceries",     "category_class": "cat-groceries",     "amount": "₹1,200"},
    ]

    categories = [
        {"name": "Food",          "class": "cat-food",          "amount": "₹2,430"},
        {"name": "Travel",        "class": "cat-travel",        "amount": "₹4,820"},
        {"name": "Bills",         "class": "cat-bills",         "amount": "₹2,799"},
        {"name": "Entertainment", "class": "cat-entertainment", "amount": "₹1,249"},
        {"name": "Groceries",     "class": "cat-groceries",     "amount": "₹1,182"},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
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
    app.run(debug=True, port=5001)
