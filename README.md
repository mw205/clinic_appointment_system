# clinic_appointment_system

Monorepo for a clinic appointment system with:

- Backend: Django, Django REST Framework, SQLite
- Frontend: Vue 3, Vite, pnpm

## Current Readiness

As checked on 2026-04-18, the repository is usable as a development starting point, but it is not fully provisioned against the intended stack yet.

What is working now:

- Django project exists and passes `python manage.py check`
- Vue frontend installs and builds with `pnpm build`
- Backend virtual environment and frontend dependencies already exist in this checkout

What still needs attention:

- `frontend/.env` is missing and must define `VITE_API_BASE_URL`
- `frontend/components.json` is missing, so `shadcn-vue` does not appear to be initialized yet
- No project stylesheet currently contains the Tailwind `@tailwind` directives
- `backend/.env` is missing, though it is currently optional because the backend does not read environment variables yet
- The backend is still scaffold-level: only the Django admin route is defined and no API routes are wired yet

## Prerequisites

- Python 3.9+
- Node.js `^20.19.0 || >=22.12.0`
- `pnpm`

## Repository Layout

```text
.
├── backend
│   ├── .venv
│   ├── core
│   ├── api
│   ├── manage.py
│   └── requirements.txt
├── frontend
│   ├── src
│   ├── package.json
│   ├── tailwind.config.js
│   └── pnpm-lock.yaml
└── diagnose_setup.py
```

## Backend Setup

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional backend environment file:

```bash
cp .env.example .env
```

If `.env.example` is empty, that is expected in the current state of the repo. The backend does not currently require environment variables to boot.

Apply migrations:

```bash
python manage.py migrate
```

Start the backend:

```bash
python manage.py runserver
```

Backend default URL:

```text
http://127.0.0.1:8000/
```

Current routed page:

- Django admin at `/admin/`

## Frontend Setup

From the repository root:

```bash
cd frontend
pnpm install
cp .env.example .env
```

Verify `frontend/.env` contains:

```bash
VITE_API_BASE_URL=http://localhost:8000/
```

Start the frontend:

```bash
pnpm dev
```

Frontend default URL:

```text
http://127.0.0.1:5173/
```

## Recommended Next Frontend Steps

To align the project with the intended stack, complete these before building real UI work:

1. Initialize `shadcn-vue` so `frontend/components.json` is generated.
2. Add a global stylesheet such as `frontend/src/assets/main.css`.
3. Add these Tailwind directives to that stylesheet:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

4. Import the stylesheet from `frontend/src/main.js`.

Example:

```js
import './assets/main.css'
```

## Start Both Apps

Use two terminals.

Terminal 1:

```bash
cd backend
source .venv/bin/activate
python manage.py runserver
```

Terminal 2:

```bash
cd frontend
pnpm dev
```

## Development Health Check

Run the diagnostic CLI from the repository root:

```bash
python3 diagnose_setup.py
```

Or:

```bash
./diagnose_setup.py
```

The script checks:

- Root files such as `.gitignore` and `README.md`
- Backend setup such as `.venv`, `requirements.txt`, `.env`, `manage.py`, CORS settings, and `db.sqlite3`
- Frontend setup such as `node_modules`, `.env`, `VITE_API_BASE_URL`, Tailwind version, `components.json`, and Tailwind directives

Exit behavior:

- Exit code `0`: no critical setup failures
- Exit code `1`: one or more required setup items are missing

## Quick Start

If you are cloning the repo fresh, the shortest path is:

```bash
git clone git@github.com:mw205/clinic_appointment_system.git
cd clinic_appointment_system

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

cd ../frontend
pnpm install
cp .env.example .env

cd ..
python3 diagnose_setup.py
```

---
## Database seeding
```bash
cd ./backend
python3 manage.py flush ##to delete the database's content
python3 manage.py setup_roles #setup roles for the project
python3 manage.py makemigrations
python3 manage.py migrate
python3 seed_data.py
```
Then start backend and frontend in separate terminals as shown above.
