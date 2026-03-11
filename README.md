# Cartopia

Django e-commerce application with product catalog, cart, wishlist, orders, and staff dashboard. Each product can have an optional PDF specifications document (uploaded or generated from product data).

## Tech stack

- Python 3.x
- Django 4.2
- SQLite (default)
- Bootstrap 5
- django-crispy-forms, Pillow, ReportLab

## Setup

From the project root (the folder containing `manage.py`):

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows (PowerShell):

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   Windows (Command Prompt):

   ```bat
   venv\Scripts\activate.bat
   ```

   Linux/macOS:

   ```bash
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```bash
   python manage.py migrate
   ```

4. Load sample data (categories, products, suppliers, delivery methods, test users):

   ```bash
   python manage.py load_sample_data
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

   By default the app is at `http://127.0.0.1:8000/`. To use another host or port:

   ```bash
   python manage.py runserver 127.0.0.1:8080
   ```

   On Windows you can use `run.bat` after setting `RUN_HOST` and `RUN_PORT` if needed.

## Test accounts (after load_sample_data)

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| User  | testuser | test123   |

## Main features

- **Public:** Product list and detail, categories, search, cart, wishlist, checkout, order history, user registration and profile.
- **Product specifications PDF:** Each product can have an attached PDF (descriptive document). On the product page it appears as "Download specifications file (PDF)" under the specifications section. PDFs can be uploaded manually or generated from the product’s name, description, and specifications via the staff dashboard or Django admin.
- **Staff dashboard:** Product and order management, add/edit/delete products, generate specification PDFs for products, update order status. Access requires a staff user.

Django admin is at `/admin/` for full backend management.

## Project structure

- `ecommerce/` — Django project settings and root URL config.
- `shop/` — Main app: models (Category, Product, Cart, Wishlist, Order, etc.), views, forms, URLs. PDF generation lives in `shop/pdf_utils.py`.
- `templates/` — Base and app templates.
- `static/` — Static assets.
- `media/` — User-uploaded files (product images, PDFs). Tracked in the repo so clones include sample data and uploads.
- `db.sqlite3` — SQLite database. Tracked in the repo.

## License

See repository or project for license details.
