# TaskFlow — Team Task Manager

A full-stack task management app built with **Django + DRF** (backend) and **HTML/CSS/Vanilla JS** (frontend). JWT auth, role-based access, kanban board, and a per-project dashboard.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Django 4.2, Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Frontend | HTML, CSS, Vanilla JS |
| Deployment | Railway (backend) + Railway Static / Vercel (frontend) |

---

## Features

- Signup / Login with JWT tokens (auto-refresh)
- Create projects → become Admin automatically
- Admins: create tasks, assign to members, manage team
- Members: view tasks, update status on assigned tasks only
- Kanban board (To Do / In Progress / Done)
- Dashboard with stats: total, overdue, per-member breakdown
- Toast notifications, clean dark UI

---

## Local Setup

### Backend

```bash
cd backend

# create virtual env
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# install deps
pip install -r requirements.txt

# run migrations
python manage.py migrate

# create a superuser (optional)
python manage.py createsuperuser

# start server
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000`

### Frontend

Just open `frontend/index.html` with any local server:

```bash
# Python
cd frontend
python -m http.server 5500

# Or use VS Code Live Server extension
```

Frontend at `http://127.0.0.1:5500`

Make sure `BASE_URL` in `frontend/js/api.js` points to your backend URL.

---

## API Endpoints

### Auth
```
POST /api/auth/signup/        → register
POST /api/auth/login/         → get tokens
GET  /api/auth/me/            → current user
POST /api/auth/token/refresh/ → refresh access token
```

### Projects
```
GET    /api/projects/              → list your projects
POST   /api/projects/              → create project (you become admin)
GET    /api/projects/:id/          → project detail
PATCH  /api/projects/:id/          → edit (admin only)
DELETE /api/projects/:id/          → delete (owner only)
POST   /api/projects/:id/members/  → add member (admin only)
DELETE /api/projects/:id/members/  → remove member (admin only)
```

### Tasks
```
GET    /api/tasks/:project_id/tasks/           → list tasks (filter by status, assigned_to)
POST   /api/tasks/:project_id/tasks/           → create task (admin only)
GET    /api/tasks/:project_id/tasks/:task_id/  → task detail
PATCH  /api/tasks/:project_id/tasks/:task_id/  → update task
DELETE /api/tasks/:project_id/tasks/:task_id/  → delete (admin only)
GET    /api/tasks/:project_id/dashboard/       → dashboard stats
```

---

## Deploy on Railway

### Backend

1. Push to GitHub
2. Go to railway.app → New Project → Deploy from GitHub
3. Select your repo's `backend/` folder
4. Add environment variables:
   ```
   SECRET_KEY=<generate a long random string>
   DEBUG=False
   ALLOWED_HOSTS=<your-railway-domain>.railway.app
   ```
5. Railway auto-detects Python and runs `Procfile`

### Frontend

Option 1 — Railway Static:
- Create a new service → Static Site → point to `frontend/` folder

Option 2 — Vercel:
```bash
cd frontend
vercel deploy
```

After deploying frontend, update `BASE_URL` in `frontend/js/api.js` to your Railway backend URL, then redeploy frontend.

---

## Project Structure

```
taskflow/
├── backend/
│   ├── core/          ← Django settings, urls
│   ├── accounts/      ← Custom user model, JWT auth views
│   ├── projects/      ← Project and membership models
│   ├── tasks/         ← Task model, board, dashboard
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.json
└── frontend/
    ├── css/main.css   ← All styles
    ├── js/api.js      ← API calls centralized
    ├── js/utils.js    ← Helpers
    ├── index.html     ← Projects list
    ├── project.html   ← Board + dashboard + members
    ├── login.html
    └── signup.html
```

---

## Role Permissions

| Action | Admin | Member |
|--------|-------|--------|
| View project | ✓ | ✓ |
| Create/delete tasks | ✓ | ✗ |
| Assign tasks | ✓ | ✗ |
| Update task status | ✓ | own tasks only |
| Add/remove members | ✓ | ✗ |
| View dashboard | ✓ | ✓ |
| Delete project | owner only | ✗ |
