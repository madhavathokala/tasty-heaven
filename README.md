# Tasty Heaven — Full-Stack Restaurant Ordering & Reservation System

A complete full-stack web application for a restaurant: browse the menu, order
food, reserve a table, and (for admins) manage the whole operation — built by
adding a **Flask + SQLite** backend to an existing HTML/CSS/JS frontend.

The original frontend's design, layout, colors, images, and page structure
have all been preserved. Only the parts needed to connect it to a real
backend were added or changed.

---

## 1. Features

**Customers**
- Browse a menu that is loaded live from the database (not hardcoded)
- Filter the menu by category (Veg / Non Veg / Starters / Desserts / Drinks)
- Add items to a cart (Local Storage, same UX as before)
- Create an account / log in / log out (real sessions, hashed passwords)
- Checkout — the order and its total are calculated and stored **on the server**
- View personal order history
- Reserve a table (saved to the database, not just an alert box)
- Send a contact message (saved to the database)

**Admin**
- Dashboard with live stats (users, orders, reservations, revenue)
- Full menu CRUD (add / edit / delete / enable-disable dishes)
- View & update the status of every order
- View & update the status of every reservation
- View all registered users
- View all contact messages

---

## 2. Technology Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Backend        | Python 3, Flask                               |
| Database       | SQLite (file-based, in `instance/`)           |
| ORM            | SQLAlchemy (via Flask-SQLAlchemy)             |
| Authentication | Flask sessions + Werkzeug password hashing    |
| Frontend       | Existing HTML, CSS, JavaScript (unchanged design) |

No React, Node.js, Express, MongoDB, Django, or PHP was used anywhere.

---

## 3. Project Structure

```
tasty-heaven/
│
├── app.py                  # Flask app factory, page routes, error handlers
├── config.py                # Configuration (secret key, DB URI)
├── requirements.txt
├── README.md
├── .gitignore
│
├── instance/
│   └── tasty_heaven.db      # SQLite database file (created automatically)
│
├── models/
│   ├── __init__.py          # db = SQLAlchemy(), imports all models
│   ├── user.py               # User (customers + admins)
│   ├── menu.py                # MenuItem
│   ├── reservation.py         # Reservation
│   ├── order.py                # Order, OrderItem
│   └── contact.py               # ContactMessage
│
├── routes/
│   ├── __init__.py           # login_required / admin_required decorators
│   ├── auth.py                 # /api/register /api/login /api/logout /api/me
│   ├── menu.py                  # /api/menu (public GET, admin CRUD)
│   ├── reservation.py            # /api/reservations /api/my-reservations
│   ├── order.py                   # /api/orders
│   ├── contact.py                   # /api/contact
│   └── admin.py                      # /api/admin/* (protected)
│
├── templates/                # All page HTML (Jinja2), original design preserved
│   ├── index.html, about.html, menu.html, gallery.html,
│   ├── reservation.html, contact.html, login.html, cart.html,
│   └── signup.html, orders.html, admin.html   (new pages)
│
├── static/                    # CSS, JS, and every original image (flat, unchanged paths)
│   ├── style.css
│   ├── app.js                  # Frontend <-> backend bridge (fetch calls)
│   ├── admin.js                  # Admin dashboard logic
│   └── *.jpg / *.png / *.webp / *.avif / *.jpeg
│
└── database/
    └── seed.py                # Creates tables + sample accounts + real menu items
```

---

## 4. Installation & Setup

### Step 1 — Open a terminal in the project folder
```bash
cd tasty-heaven
```

### Step 2 — Create and activate a virtual environment
```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Seed the database
This creates the SQLite tables, a sample admin account, a sample user
account, and the full menu (using the real dishes/prices/images from the
original project).
```bash
python database/seed.py
```

### Step 5 — Run the Flask app
```bash
python app.py
```
(or, alternatively: `flask run`)

### Step 6 — Open it in your browser
```
http://127.0.0.1:5000
```

---

## 5. Default Development Credentials

Created by `database/seed.py`. **For local development only — change or
remove before deploying anywhere public.**

| Role  | Email                     | Password   |
|-------|---------------------------|------------|
| Admin | admin@tastyheaven.com     | Admin@123  |
| User  | user@tastyheaven.com      | User@123   |

Admin dashboard: `http://127.0.0.1:5000/admin.html` (log in as the admin
account first).

---

## 6. API Endpoints

All endpoints return JSON in the form `{"success": true/false, "message": "...", ...}`.

### Auth (`/api`)
| Method | Endpoint         | Description                          | Auth required |
|--------|------------------|---------------------------------------|----------------|
| POST   | `/api/register`  | Create an account, auto-logs in      | No             |
| POST   | `/api/login`     | Log in, creates a session            | No             |
| POST   | `/api/logout`    | Clear the session                    | No             |
| GET    | `/api/me`        | Get the current logged-in user       | No             |

### Menu (`/api`)
| Method | Endpoint               | Description                     | Auth required |
|--------|------------------------|-----------------------------------|----------------|
| GET    | `/api/menu`            | List all menu items (optional `?category=`) | No |
| GET    | `/api/menu/<id>`       | Get one menu item                | No             |
| POST   | `/api/menu`            | Create a menu item               | Admin          |
| PUT    | `/api/menu/<id>`       | Update a menu item               | Admin          |
| DELETE | `/api/menu/<id>`       | Delete a menu item               | Admin          |

### Reservations (`/api`)
| Method | Endpoint                  | Description                        | Auth required |
|--------|----------------------------|--------------------------------------|----------------|
| POST   | `/api/reservations`       | Create a reservation                | No (tagged to your account if logged in) |
| GET    | `/api/my-reservations`    | List your own reservations          | Yes            |

### Orders (`/api`)
| Method | Endpoint            | Description                                          | Auth required |
|--------|----------------------|---------------------------------------------------------|----------------|
| POST   | `/api/orders`       | Place an order (`{"items":[{"menu_item_id":1,"quantity":2}]}`) | Yes |
| GET    | `/api/orders`        | List your own orders                                   | Yes            |
| GET    | `/api/orders/<id>`    | Get one order (owner or admin only)                    | Yes            |

### Contact (`/api`)
| Method | Endpoint         | Description             | Auth required |
|--------|------------------|---------------------------|----------------|
| POST   | `/api/contact`   | Submit a contact message | No             |

### Admin (`/api/admin`) — all require an admin session
| Method | Endpoint                              | Description                       |
|--------|-----------------------------------------|--------------------------------------|
| GET    | `/api/admin/users`                     | List all users                    |
| GET    | `/api/admin/reservations`               | List all reservations             |
| PUT    | `/api/admin/reservations/<id>`           | Update a reservation's status     |
| GET    | `/api/admin/orders`                       | List all orders                    |
| PUT    | `/api/admin/orders/<id>`                   | Update an order's status          |
| GET    | `/api/admin/contact-messages`               | List all contact messages         |
| GET    | `/api/admin/stats`                            | Dashboard summary numbers         |

---

## 7. Architecture: Frontend → Backend → Database

```
Tasty Heaven Frontend (HTML/CSS/JS, served from templates/ + static/)
        │
        │  JavaScript fetch() calls (app.js / admin.js)
        ▼
Flask Backend (app.py + routes/*.py)
        │
        │  SQLAlchemy ORM (models/*.py)
        ▼
SQLite Database (instance/tasty_heaven.db)
```

- Every page (`index.html`, `menu.html`, etc.) is now served by Flask via
  `render_template()`, instead of being opened as a static file. This lets
  the navbar show "Login" or "Logout / My Orders / Admin" depending on
  whether you're logged in — decided server-side using the Flask session.
- `static/` is mounted at the site root (`static_url_path=""`), so every
  original relative link (`href="style.css"`, `src="image 1.jpg"`, etc.)
  kept working with **zero changes** to those paths.
- The shopping cart still lives in `localStorage` for a snappy add/remove/
  quantity experience — exactly like before. The only change is that
  **checkout** now sends the cart to `/api/orders`, and the **price/total
  used is always the one stored in the database**, never whatever the
  browser sent. This prevents a user from tampering with prices in the
  browser to get a cheaper order.

---

## 8. How Login Works

1. `login.html` submits email/password to `POST /api/login` via `fetch()`.
2. Flask looks up the user by email, and verifies the password using
   `werkzeug.security.check_password_hash` against the stored hash (plain-text
   passwords are never stored).
3. On success, Flask stores `user_id` and `role` in the **server-side
   session** (a signed cookie — the actual data stays on the server).
4. Every subsequent request automatically includes that session cookie, so
   `routes/__init__.py`'s `current_user()` helper can identify who's logged
   in, and `login_required` / `admin_required` decorators protect the
   relevant endpoints.
5. `POST /api/logout` clears the session.

## 9. How Reservations Work

`reservation.html`'s form submits to `POST /api/reservations`. The backend
validates every field (name, valid email, phone length, date, time, and that
a guest count was actually selected), then stores a new row in the
`reservations` table with `status="pending"`. If you're logged in, the
reservation is also linked to your account so it can show up as "my
reservations" later.

## 10. How Orders Work

1. You add items to your cart in `menu.html` (stored in `localStorage`,
   including each item's database ID).
2. On checkout, the frontend sends **only** `{menu_item_id, quantity}` pairs
   to `POST /api/orders` — it does **not** send prices.
3. The backend looks up each `menu_item_id` in SQLite, reads its **current
   price from the database**, multiplies by quantity, and sums everything
   (+ a flat delivery fee) to get the final total — all computed server-side.
4. An `Order` row and its `OrderItem` rows are created and saved.
5. The response includes the real order ID and total, which the frontend
   displays before redirecting to `orders.html`.

## 11. How Admin Functionality Works

- Any user with `role="admin"` who logs in gets an **Admin** link in the
  navbar instead of the usual Login/Logout links, taking them to
  `admin.html`.
- `admin.html` first calls `GET /api/me` to double-check the logged-in
  user is actually an admin before showing any dashboard content or firing
  further requests (defense in depth — every `/api/admin/*` route is also
  protected server-side by the `@admin_required` decorator, so even a
  direct API call from a non-admin session is rejected with `403`).
- From there, the dashboard's tabs call the various `/api/admin/*`
  endpoints to manage the menu, view/update orders and reservations, and
  view users and contact messages.

---

## 12. Troubleshooting

| Problem | Likely Cause / Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | You didn't activate the virtual environment, or didn't run `pip install -r requirements.txt`. |
| Menu page shows "No menu items available" | You haven't run `python database/seed.py` yet, or you deleted the DB file — re-run the seed script. |
| Login says "Invalid email or password" | Double check you're using the exact seeded credentials, or that you registered first. |
| Changes to menu items via admin don't show on `menu.html` | Refresh the menu page — it always loads live from `/api/menu`, so this should be automatic. If not, hard-refresh (Ctrl+F5) to bypass any cached JS. |
| `sqlite3.OperationalError: unable to open database file` | Make sure the `instance/` folder exists and is writable (it's created automatically on first run, but check folder permissions if running in a restricted environment). |
| Port 5000 already in use | Run `flask run --port 5001` instead, or stop whatever else is using port 5000. |
| Images not loading | Confirm you're running the app through Flask (`python app.py`), not opening the HTML files directly in a browser — the images are served via Flask's static route. |

---

## 13. Short "Viva" Explanation

*"I converted a static HTML/CSS/JS restaurant website into a full-stack app
by adding a Flask backend and a SQLite database. Flask serves the original
pages using Jinja templates instead of raw HTML files, so the server can
know whether someone is logged in. I used SQLAlchemy as the ORM to define
five tables — Users, MenuItems, Reservations, Orders, and OrderItems — with
proper foreign key relationships (an Order has many OrderItems, a User has
many Orders and Reservations). Authentication uses Flask's server-side
sessions, and passwords are hashed with Werkzeug — never stored as plain
text. The most important design decision is that when a customer checks
out, the browser only sends item IDs and quantities — the actual price
calculation happens entirely on the server, using the price stored in the
database at that moment, so a user can't tamper with the price in the
browser. There's also a role-based admin panel: only accounts with
role='admin' can reach the admin API routes, enforced by a decorator
that checks the session on every request, not just by hiding a link in the
UI."*
