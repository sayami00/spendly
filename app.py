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
        return redirect(url_for("landing"))

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
        "name": "Nitish Kumar",
        "email": "nitish@example.com",
        "initials": "NK",
        "member_since": "2 Jan 2026"
    }

    stats = {
        "total_spent": "₹12,451",
        "transaction_count": 10,
        "top_category": "Food"
    }

    transactions = [
        {
            "date": "15 Apr 2026",
            "description": "Lunch at Cafe",
            "category": "Food",
            "amount": "₹450",
            "color_class": "badge-food"
        },
        {
            "date": "14 Apr 2026",
            "description": "Flight to Delhi",
            "category": "Travel",
            "amount": "₹4,500",
            "color_class": "badge-travel"
        },
        {
            "date": "10 Apr 2026",
            "description": "Netflix subscription",
            "category": "Entertainment",
            "amount": "₹649",
            "color_class": "badge-entertainment"
        },
        {
            "date": "8 Apr 2026",
            "description": "Grocery run",
            "category": "Groceries",
            "amount": "₹1,200",
            "color_class": "badge-groceries"
        },
        {
            "date": "5 Apr 2026",
            "description": "Electricity bill",
            "category": "Bills",
            "amount": "₹1,800",
            "color_class": "badge-bills"
        }
    ]

    categories = [
        {
            "name": "Food",
            "total_spent": "₹3,200",
            "percentage": 45,
            "color_class": "category-food"
        },
        {
            "name": "Travel",
            "total_spent": "₹4,820",
            "percentage": 70,
            "color_class": "category-travel"
        },
        {
            "name": "Bills",
            "total_spent": "₹2,799",
            "percentage": 40,
            "color_class": "category-bills"
        },
        {
            "name": "Entertainment",
            "total_spent": "₹1,249",
            "percentage": 18,
            "color_class": "category-entertainment"
        },
        {
            "name": "Groceries",
            "total_spent": "₹1,182",
            "percentage": 17,
            "color_class": "category-groceries"
        }
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
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
