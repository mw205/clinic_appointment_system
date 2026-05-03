# Clinic Appointment System

A comprehensive, role-based clinic management and appointment system. This monorepo contains a robust Django REST API and a modern Vue 3 frontend.

## Project Status

The project is **functional** and supports role-based access for Admins, Doctors, Receptionists, and Patients. It includes a complete set of features from appointment booking to consultation management and analytics.

## Tech Stack

### Backend

- **Framework:** [Django 4.2](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/)
- **Database:** MySQL
- **Authentication:** JWT (JSON Web Tokens) with rotation and blacklisting
- **Background Tasks:** Email services (configured for console output by default)
- **Tools:** `django-filter`, `django-extensions`, `faker` (for seeding)

### Frontend

- **Framework:** [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool:** [Vite](https://vitejs.dev/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/) & [Shadcn-Vue](https://www.shadcn-vue.com/)
- **State Management:** [Pinia](https://pinia.vuejs.org/)
- **Form Handling:** [VeeValidate](https://vee-validate.logaretm.com/v4/) & [Zod](https://zod.dev/)

## Features

- **🔐 Multi-Role RBAC:**
  - **Admin:** Dashboard, user management, and system-wide analytics.
  - **Doctor:** Daily appointment queue, patient medical records, and consultation forms (prescriptions & tests).
  - **Receptionist:** Appointment scheduling, rescheduling, and patient check-in.
  - **Patient:** Online booking, personal appointment history, and consultation summaries.
- **📅 Appointment Management:** Comprehensive booking flow with doctor availability, slot durations, and buffer times.
- **📧 Communication:** Email verification and password reset workflows.
- **📊 Analytics:** Visualized data for administrative insights.

## 🛠️ Prerequisites

- **Python:** 3.9+
- **Node.js:** ^20.19.0 || >=22.12.0
- **Package Manager:** `pnpm`
- **Database:** MySQL

## 📦 Repository Layout

```text
.
├── backend/              # Django Project
│   ├── accounts/         # User models, RBAC, and Profiles
│   ├── appointments/     # Booking logic and Appointment models
│   ├── scheduling/       # Doctor schedules and slot generation
│   ├── consultations/    # Medical records and prescriptions
│   ├── analytics/        # Business intelligence logic
│   └── core/             # Project settings and configuration
├── frontend/             # Vue 3 Project
│   ├── src/assets/       # Global styles and assets
│   ├── src/components/   # Reusable UI components (Shadcn)
│   ├── src/views/        # Role-based page views
│   └── src/stores/       # Pinia state management
└── diagnose_setup.py     # Diagnostic tool
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
cp .env.example .env
```

**Note:** Update `backend/.env` with your MySQL database credentials.

### 2. Database Initialization & Seeding

**Database Seeding:**
To quickly populate the database with default roles, admin users, and dummy data:

```bash
# Initialize roles and permissions
python manage.py setup_roles

# Apply migrations
python manage.py migrate

# Seed the database with sample data (creates all roles)
python seed_data.py
```

_Default password for all seeded users: `password123`_

### 3. Frontend Setup

```bash
cd ../frontend
pnpm install
cp .env.example .env
```

Ensure `VITE_API_BASE_URL` in `frontend/.env` points to your backend (default: `http://localhost:8000/api/`).

## Running the Application

You will need two terminals running simultaneously.

### Terminal 1: Backend

```bash
cd backend
source .venv/bin/activate
python manage.py runserver
```

### Terminal 2: Frontend

```bash
cd frontend
pnpm dev
```

The application will be accessible at `http://localhost:5173`.

## Development Tools

### Diagnostics

Run the diagnostic script from the root to verify your environment setup:

```bash
python3 diagnose_setup.py
```

### Linting & Formatting

```bash
cd frontend
pnpm lint    # Run linter
pnpm format  # Run formatter (Prettier)
```
