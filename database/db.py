import os
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "spendly.db")


def get_db():
    """Return a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables (idempotent — safe to call on every startup)."""
    conn = get_db()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    UNIQUE NOT NULL,
                password   TEXT    NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name    TEXT    NOT NULL,
                color   TEXT
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                amount      REAL    NOT NULL,
                description TEXT,
                date        DATE    NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount  REAL    NOT NULL,
                month   TEXT    NOT NULL
            );
        """)
    conn.close()


def seed_db():
    """Insert sample data for development. Safe to call multiple times — skips if demo user exists."""
    conn = get_db()

    existing = conn.execute("SELECT id FROM users WHERE email = ?", ("nitish@example.com",)).fetchone()
    if existing:
        conn.close()
        return

    with conn:
        # --- user ---
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Nitish Kumar", "nitish@example.com", generate_password_hash("password123")),
        )
        user_id = conn.execute("SELECT id FROM users WHERE email = ?", ("nitish@example.com",)).fetchone()["id"]

        # --- categories ---
        categories = [
            ("Food",          "#F97316"),
            ("Travel",        "#3B82F6"),
            ("Bills",         "#EF4444"),
            ("Entertainment", "#A855F7"),
            ("Groceries",     "#22C55E"),
        ]
        for name, color in categories:
            conn.execute(
                "INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)",
                (user_id, name, color),
            )

        def cat_id(name):
            return conn.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ?", (user_id, name)
            ).fetchone()["id"]

        # --- budget ---
        conn.execute(
            "INSERT INTO budgets (user_id, amount, month) VALUES (?, ?, ?)",
            (user_id, 25000.0, "2026-04"),
        )

        # --- expenses (~10 rows across April 2026) ---
        expenses = [
            (cat_id("Food"),          450.0,   "Lunch at Cafe",       "2026-04-02"),
            (cat_id("Food"),          780.0,   "Dinner with family",   "2026-04-05"),
            (cat_id("Food"),          1200.0,  "Grocery run",          "2026-04-08"),
            (cat_id("Travel"),        320.0,   "Ola ride",             "2026-04-03"),
            (cat_id("Travel"),        4500.0,  "Flight to Delhi",      "2026-04-10"),
            (cat_id("Bills"),         1800.0,  "Electricity bill",     "2026-04-01"),
            (cat_id("Bills"),         999.0,   "Internet plan",        "2026-04-01"),
            (cat_id("Entertainment"), 649.0,   "Netflix subscription", "2026-04-01"),
            (cat_id("Entertainment"), 600.0,   "Movie tickets",        "2026-04-07"),
            (cat_id("Groceries"),     1182.0,  "Weekend market",       "2026-04-06"),
        ]
        for category_id, amount, description, date in expenses:
            conn.execute(
                "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, category_id, amount, description, date),
            )

    conn.close()
