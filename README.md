# HealthCare Clinic Appointment System

A comprehensive, full-stack clinic appointment management system designed for distinct user roles: Patients, Doctors, Receptionists, and Administrators.

## 🚀 Tech Stack

- **Backend:** Django, Django REST Framework (DRF), MySQL
- **Frontend:** Vue 3 (Composition API), Vite, Tailwind CSS, shadcn-vue
- **Authentication:** Secure HttpOnly Cookies (JWT-based) with automatic silent refresh
- **Package Manager:** pnpm

## ✨ Key Features

- **Robust Authentication Flow:**
  - Secure HttpOnly cookie-based sessions (protects against XSS vulnerabilities).
  - Automatic, transparent token refreshing via Axios interceptors.
  - Complete flows for Login, Signup, Password Reset, and Email Verification (with rate-limiting and countdown timers).
- **Role-Based Access Control (RBAC):**
  - Distinct portals and dashboard navigation tailored for `Admin`, `Receptionist`, `Doctor`, and `Patient` roles.
  - Granular API permission classes enforcing strict backend data access.
- **User Administration Panel:**
  - Dedicated interface for Admins and Receptionists to view and manage users.
  - Advanced DRF-powered filtering (Search by name/email, Filter by Role, Filter by Status).
  - Server-side pagination with dynamic UI controls.
  - UI strictly reflects backend constraints (e.g., Receptionists are restricted to read-only views).
- **Profile & Account Management:**
  - Dynamic profile forms rendering distinct fields based on user role (e.g., Doctors have specialties, Patients have blood types).
  - Seamless password change and security flows.

### 🔜 Upcoming Team Modules (Work in Progress)

*(This section is reserved for the rest of the team to document their upcoming features)*

- **[Module Name e.g., Appointment Scheduling]:**
  - *To be added by [Team Member Name]*
- **[Module Name e.g., Medical Records / Prescriptions]:**
  - *To be added by [Team Member Name]*
- **[Module Name e.g., Billing & Invoicing]:**
  - *To be added by [Team Member Name]*

## 🛠️ Prerequisites

- Python 3.9+
- Node.js `^20.19.0 || >=22.12.0`
- `pnpm`
- MySQL (or SQLite for local rapid dev)

## 📦 Repository Layout

```text
.
├── backend
│   ├── api                 # DRF serializers, views, and core business logic
│   ├── accounts            # Custom user models and authentication workflows
│   ├── manage.py
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── components      # UI components (shadcn-vue)
│   │   ├── composables     # Global state and auth logic (useAuth.js)
│   │   ├── layouts         # Dashboard and Auth wrappers
│   │   ├── services        # Axios API configurations
│   │   └── views           # Page-level components organized by feature
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── diagnose_setup.py       # Local dev health-checker
```

## ⚙️ Quick Start Guide

### 1. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

*Note: Ensure your `.env` contains the correct database credentials if using MySQL.*

**Database Seeding:**
To quickly populate the database with default roles, admin users, and dummy data:
```bash
python manage.py flush           # WARNING: Deletes existing data
python manage.py setup_roles     # Creates Patient, Doctor, Receptionist, Admin groups
python manage.py makemigrations
python manage.py migrate
python seed_data.py
```

**Start the API:**
```bash
python manage.py runserver
```
*The backend will be available at `http://127.0.0.1:8000/`*

### 2. Frontend Setup

In a new terminal window:

```bash
cd frontend
pnpm install
cp .env.example .env
```

Verify your `frontend/.env` points to the Django backend. Specifically, ensure the API base URL is set correctly:
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

**Start the Development Server:**
```bash
pnpm dev
```
*The frontend will be available at `http://127.0.0.1:5173/`*

## 🩺 Development Health Check

You can run the diagnostic CLI from the repository root to verify your environment is correctly configured:

```bash
python3 diagnose_setup.py
```
This script acts as an automated checklist and validates missing virtual environments, node modules, required `.env` flags, and CORS configurations.

---
*Built by mw205 team.*
