# Shared Household Budgeting Monorepo

This monorepo contains:

- `backend/` — FastAPI backend with SQLAlchemy, Alembic, JWT auth, budgeting APIs, and Plaid sandbox scaffolding.
- `ios/` — SwiftUI app workspace placeholder.

## Architecture

- **Auth**: email/password + JWT bearer tokens.
- **Data**: PostgreSQL via SQLAlchemy ORM.
- **Migrations**: Alembic (`backend/alembic/versions/0001_init.py`).
- **Budget domain**: users, households, memberships, categories, monthly budgets, transactions, device tokens, budget alert states.
- **Plaid scaffold**:
  - Create link token
  - Exchange public token for (encrypted) access token storage
  - Persist item cursor for `/transactions/sync`
  - Webhook endpoint for future ngrok testing
  - Sync service that upserts transactions and evaluates budget thresholds
- **Notifications**: local log-only sender (`app/services/notifications.py`).

## Local setup

### 1) Prerequisites
- Docker + Docker Compose

### 2) Run services
```bash
docker compose up --build
```

This starts:
- Postgres on `localhost:5432`
- FastAPI on `localhost:8000`

The backend container runs migrations at startup (`alembic upgrade head`).

### 3) Verify health
```bash
curl http://localhost:8000/health
```

### 4) API docs
- Swagger UI: `http://localhost:8000/docs`

## Environment variables

Backend uses these env vars (defaults in `app/core/config.py`):

- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM` (default: HS256)
- `ACCESS_TOKEN_MINUTES`
- `TOKEN_ENCRYPTION_KEY` (used to encrypt Plaid access tokens)
- `PLAID_ENV` (default: sandbox)
- `PLAID_CLIENT_ID`
- `PLAID_SECRET`
- `PLAID_WEBHOOK_URL`

> For initial local development, Plaid credentials can be empty; scaffolded endpoints return placeholder behavior.

## Core endpoints

### Auth
- `POST /auth/register`
- `POST /auth/login`

### Households
- `POST /households` (create; returns invite code)
- `POST /households/join` (join via invite code)

### Categories / Budgets / Transactions (CRUD)
Scoped under household:
- `/households/{household_id}/categories`
- `/households/{household_id}/budgets`
- `/households/{household_id}/transactions`

### Summary
- `GET /summary/monthly?household_id=<uuid>&month=YYYY-MM`

Returns overall monthly spent and totals by category.

### Plaid scaffold
- `POST /plaid/link-token`
- `POST /plaid/exchange-public-token`
- `POST /plaid/sync/{connection_id}`
- `POST /plaid/webhook`

## Plaid webhook testing with ngrok (later)

When you are ready to validate webhooks end-to-end:

1. Start backend:
   ```bash
   docker compose up --build
   ```
2. Expose local backend with ngrok:
   ```bash
   ngrok http 8000
   ```
3. Copy HTTPS forwarding URL and set:
   ```bash
   export PLAID_WEBHOOK_URL=https://<your-subdomain>.ngrok.io/plaid/webhook
   ```
4. Restart backend with updated env.
5. In Plaid Sandbox flow, configure/use webhook URL and trigger updates.

## Backend development without Docker (optional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
