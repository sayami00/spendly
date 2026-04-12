# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the development server (port 5001, debug mode)
python app.py

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run a single test file
pytest tests/test_foo.py
```

## Architecture

**Spendly** is a Flask expense-tracking web app built as a step-by-step learning project. The stack is intentionally minimal: no frontend framework, no ORM, no build step.

### Request flow

```
Browser → Flask route (app.py) → render_template → Jinja2 template → HTML
```

All routes live in `app.py`. Many are stubs (returning strings) that students implement in later steps.

### Templates

- `templates/base.html` — shared layout: navbar, footer, Google Fonts (DM Sans + DM Serif Display), `style.css`, `main.js`. All pages extend this.
- Page templates use `{% extends "base.html" %}` and fill `{% block title %}`, `{% block head %}`, `{% block content %}`, and `{% block scripts %}`.
- Page-specific CSS is loaded via `{% block head %}` (e.g. `landing.css` for the landing page).

### Static assets

- `static/css/style.css` — global styles (navbar, footer, typography, shared components)
- `static/css/landing.css` — landing page only
- `static/js/main.js` — vanilla JS, no libraries or frameworks (project constraint)

### Database

- `database/db.py` — SQLite helpers to be implemented by students: `get_db()`, `init_db()`, `seed_db()`
- `database/__init__.py` — package init (empty)
- Database is not yet wired into any route; future steps will add it.

### Currency / locale

The app targets Indian users — amounts are displayed in Rupees (₹).
