# TaskFlow — Team Task Manager

A full-stack task management web app built with **Django + DRF** (backend) and **HTML/CSS/Vanilla JS** (frontend).  
Features JWT authentication, role-based access control, a Kanban board, and a per-project dashboard.

🔗 **Live Demo:** https://creative-churros-e6fde1.netlify.app/login.html  
📦 **Backend API:** https://team-task-manager-website-production.up.railway.app

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Django 4.2, Django REST Framework |
| Auth | JWT via djangorestframework-simplejwt |
| Database | MySQL |
| Frontend | HTML, CSS, Vanilla JS |
| Deployment | Railway (backend + MySQL) + Netlify (frontend) |

---

## Features

- Signup / Login with JWT tokens (auto-refresh)
- Create projects → become Admin automatically
- **Admins:** create tasks, assign to members, manage team
- **Members:** view tasks, update status on assigned tasks only
- Kanban board (To Do / In Progress / Done)
- Dashboard with stats: total tasks, overdue, per-member breakdown
- Toast notifications, clean light UI

---

## Local Setup

### Backend

```bash
cd taskflow/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and fill in your MySQL credentials

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000`

### Frontend

```bash
cd taskflow/frontend
python -m http.server 5500
```

Frontend at: `http://127.0.0.1:5500/login.html`

> Make sure `BASE_URL` in `frontend/js/api.js` points to `http://127.0.0.1:8000/api` for local development.

### MySQL Setup (One-Time)

```sql
CREATE DATABASE taskflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'taskflow_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON taskflow_db.* TO 'taskflow_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## Environment Variables

Create a `.env` file in `taskflow/backend/`:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=taskflow_db
DB_USER=taskflow_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

---

## API Endpoints

### Auth
```
POST /api/auth/signup/         → Register new user
POST /api/auth/login/          → Get JWT tokens
GET  /api/auth/me/             → Current user info
POST /api/auth/token/refresh/  → Refresh access token
POST /api/auth/logout/         → Logout
```

### Projects
```
GET    /api/projects/               → List your projects
POST   /api/projects/               → Create project (you become admin)
GET    /api/projects/:id/           → Project detail
PATCH  /api/projects/:id/           → Edit project (admin only)
DELETE /api/projects/:id/           → Delete project (owner only)
POST   /api/projects/:id/members/   → Add member (admin only)
DELETE /api/projects/:id/members/   → Remove member (admin only)
```

### Tasks
```
GET    /api/tasks/:project_id/tasks/            → List tasks
POST   /api/tasks/:project_id/tasks/            → Create task (admin only)
GET    /api/tasks/:project_id/tasks/:task_id/   → Task detail
PATCH  /api/tasks/:project_id/tasks/:task_id/   → Update task
DELETE /api/tasks/:project_id/tasks/:task_id/   → Delete task (admin only)
GET    /api/tasks/:project_id/dashboard/        → Dashboard stats
```

---

## Deployment

### Backend (Railway)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set **Root Directory** to `taskflow/backend`
4. Add a **MySQL** database service
5. Set environment variables:

```
SECRET_KEY=<generate a long random string>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app
DB_NAME=${{MySQL.MYSQLDATABASE}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
CORS_ALLOWED_ORIGINS=https://<your-netlify-domain>.netlify.app
```

### Frontend (Netlify)

1. Go to [netlify.com](https://netlify.com) → New Site → Import from GitHub
2. Set **Base directory** to `taskflow/frontend`
3. Set **Publish directory** to `taskflow/frontend`
4. Deploy!

> After deploying, update `BASE_URL` in `frontend/js/api.js` to your Railway backend URL.

---

## Project Structure

```
taskflow/
├── backend/
│   ├── core/           ← Django settings, URLs
│   ├── accounts/       ← Custom user model, JWT auth views
│   ├── projects/       ← Project and membership models
│   ├── tasks/          ← Task model, board, dashboard
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.json
└── frontend/
    ├── css/main.css    ← All styles
    ├── js/api.js       ← Centralized API calls
    ├── js/utils.js     ← Helper functions
    ├── index.html      ← Projects list
    ├── project.html    ← Board + dashboard + members
    ├── login.html
    └── signup.html
```

---

## Role Permissions

| Action | Admin | Member |
|--------|-------|--------|
| View project | ✅ | ✅ |
| Create / delete tasks | ✅ | ❌ |
| Assign tasks | ✅ | ❌ |
| Update task status | ✅ | Own tasks only |
| Add / remove members | ✅ | ❌ |
| View dashboard | ✅ | ✅ |
| Delete project | Owner only | ❌ |

---

## Author

Made  by **Yatharth**