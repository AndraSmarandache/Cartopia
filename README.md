# Cartopia

Django e-commerce application with product catalog, cart, wishlist, orders, and staff dashboard. Each product can have an optional PDF specifications document (uploaded or generated from product data). Includes search (BM25), autocomplete (trie), and similar-product recommendations (TF-IDF + cosine similarity).

---

## How to run

**Prerequisites:** Python 3.x (3.10+ recommended).

**First-time setup** (from the folder that contains `manage.py`):

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   ```

   - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   - **Windows (Command Prompt):** `venv\Scripts\activate.bat`
   - **Linux/macOS:** `source venv/bin/activate`

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

4. **Load sample data** (optional; creates categories, products, test users)

   ```bash
   python manage.py load_sample_data
   ```

5. **Start the server**

   ```bash
   python manage.py runserver
   ```

   Open **http://127.0.0.1:8000/** in your browser.

**Custom host/port:**

```bash
python manage.py runserver 127.0.0.1:8080
```

**Windows shortcut:** use `run.bat` in the project folder. It activates the venv and runs the server. Set `RUN_PORT=8080` (or `RUN_HOST` and `RUN_PORT`) before running if you want a different address.

---

## Tech stack

- Python 3.x
- Django 4.2
- SQLite (default)
- Bootstrap 5
- django-crispy-forms, Pillow, ReportLab, scikit-learn

## Setup (detailed)

From the project root (the folder containing `manage.py`), follow the steps under **How to run** above. The virtual environment must be activated before `pip install` and `python manage.py` commands.

## Test accounts (after load_sample_data)

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| User  | testuser | test123   |

## Main features

- **Public:** Product list and detail, categories, search, cart, wishlist, checkout, order history, user registration and profile.
- **Search (BM25):** Full-text product search with BM25 ranking. Optional substring matching (e.g. "lap" matches "laptop"). Used on the home page and product list.
- **Autocomplete:** While typing in the search bar, suggestions from a trie (prefix tree) over product titles; inline gray completion and dropdown, with keyboard navigation (arrows, Enter, Tab).
- **Similar products:** On each product page, recommendations via TF-IDF and cosine similarity on name, description, and specifications (scikit-learn).
- **Product specifications PDF:** Each product can have an attached PDF (descriptive document). On the product page it appears as "Download specifications file (PDF)" under the specifications section. PDFs can be uploaded manually or generated from the product’s name, description, and specifications via the staff dashboard or Django admin.
- **Staff dashboard:** Product and order management, add/edit/delete products, generate specification PDFs for products, update order status. Access requires a staff user.

Django admin is at `/admin/` for full backend management.

## Project structure

- `ecommerce/` — Django project settings and root URL config.
- `shop/` — Main app: models (Category, Product, Cart, Wishlist, Order, etc.), views, forms, URLs. Search: `search_utils.py` (BM25), `autocomplete.py` (trie), `similarity.py` (TF-IDF + cosine). PDFs: `pdf_utils.py`.
- `templates/` — Base and app templates.
- `static/` — Static assets.
- `media/` — User-uploaded files (product images, PDFs). Tracked in the repo so clones include sample data and uploads.
- `db.sqlite3` — SQLite database. Tracked in the repo.

## License

See repository or project for license details.
