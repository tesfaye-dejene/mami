# Inventory Shop — Django Templates Frontend

Local inventory & ordering app with **Django Templates** UI (no separate React required for day-to-day use).

## Who sees what

| Role | Sees |
|------|------|
| **Guest** | Product catalog, cart |
| **Customer** | Own orders only (`My Orders`) |
| **Owner / Admin (staff)** | Dashboard with **order counts**, all orders, status updates, products |

Customer orders are **not** visible to other customers — only to the customer who placed them and to the shop owner.

## Run (backend only)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate   # or Git Bash / Linux / macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

### Demo owner login
- Username: `admin`
- Password: `Admin12345!`

Owner area: **http://127.0.0.1:8000/owner/**  
→ Total orders, Pending / Confirmed / Processing / Completed / Cancelled counts, recent orders, full order list.

### Customer flow
1. Register → Login  
2. Add products to cart → Place order  
3. **My Orders** — only that customer’s orders  
4. Owner sees every order and the counts on the dashboard  

## Optional React frontend

The original Vite/React app under `frontend/` still works against `/api/v1/`. Templates are the primary UI.

## API

Still available under `/api/v1/` (auth, products, orders, messages, services).
