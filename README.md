# Dashboard Application (Production Template)

A secure, modular, production-ready dashboard web application designed to manage and monitor systems through a unified interface. Features include cookie-based JWT authentication, system metrics, user management, and modular plugin support.

> ⚠️ This is a sample project and includes dummy data for demonstration purposes.

---

## 📦 Tech Stack

* **Frontend**: React + Vite + Tailwind CSS
* **Backend**: Flask (Python 3.12) + SQLite
* **Deployment**: Gunicorn + Nginx + systemd
* **Security**: Let's Encrypt SSL, iptables firewall
* **Auth**: JWT stored in HTTP-only cookies with role-based access (RBAC)

---

## 🚀 Quick Setup Instructions (Ubuntu 24.04)

### 1. Download Setup Script

Use `wget` or `git` to download `updated_setup.sh` to your home directory (e.g. `/home/ubuntu` or `~/`):

```bash
wget https://raw.githubusercontent.com/landonis/dashboard-app/main/scripts/updated_setup.sh
# OR
# git clone https://github.com/landonis/dashboard-app.git
```

### 2. Make It Executable

```bash
chmod +x ~/updated_setup.sh
```

### 3. Edit Domain Name

Open the script and set your domain name:

```bash
DOMAIN_NAME="your-domain.com"
```

### 4. Run the Script

```bash
sudo ~/updated_setup.sh
```

This script:

* Installs system dependencies
* Clones the GitHub repo
* Builds frontend and backend
* Configures Nginx and SSL
* Deploys with Gunicorn and systemd

---

## 🔐 Authentication

* JWT access tokens are issued via `set_access_cookies()`
* Tokens are stored in **secure, HTTP-only cookies**
* Login state is maintained via `/auth/me`
* Logout clears cookie with `unset_jwt_cookies()`
* No `localStorage` is used for token handling

---

## 📁 Project Structure

```
dashboard-app/
├── backend/               # Flask app (modular backend)
│   ├── modules/           # Modular features (e.g., system info)
│   ├── auth.py            # JWT login/logout
│   ├── app.py             # App factory and route registration
│   └── ...
├── frontend/              # React frontend (Vite + Tailwind)
│   ├── src/pages/         # LoginPage, SystemInfoPage, etc.
│   ├── contexts/          # AuthContext
│   └── ...
├── scripts/               # Setup scripts
│   └── updated_setup.sh
└── nginx/                 # Nginx config templates
```

---

## 🛠 Features

* Secure JWT cookie-based login system
* Admin panel with user management (SQLite-based RBAC)
* Modular backend architecture (`/modules`)
* Live system metrics (CPU, memory, disk, uptime)
* Auto-refresh on system info page
* Role-restricted routes using `hasRole()`
* Reverse proxy via Nginx with automatic Let's Encrypt SSL
* Fully automated deployment with `setup.sh`

---

## 📂 Environment Variables (`.env`)

This file is created automatically but supports the following overrides:

```env
SECRET_KEY=...
JWT_SECRET_KEY=...
DATABASE_URL=sqlite:///dashboard.db
FLASK_ENV=production
FLASK_DEBUG=false
VITE_API_URL=https://your-domain.com
```

---

## 🔎 Verifying Deployment

### Backend

```bash
sudo systemctl status dashboard-backend
```

### Frontend

```bash
sudo systemctl status dashboard-frontend
```

### Nginx

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Logs

```bash
sudo journalctl -u dashboard-backend -f
sudo tail -f /var/log/nginx/error.log
```

---

## 🌐 Accessing the Dashboard

After deployment:

```
https://your-domain.com
```

Default credentials:

* Username: `admin`
* Password: `admin`

Login as admin to view live system stats and manage users.

---

## 🔧 Extending the Dashboard

### Adding a Module

1. Create a folder in `backend/modules/`
2. Add a `routes.py` with `@bp.route(...)`
3. Register blueprint in `app.py`

### Frontend Integration

1. Add page under `frontend/src/pages`
2. Update navigation/sidebar
3. Secure route with `hasRole('admin')`

---

## 📘 License

MIT. See `LICENSE` file for details.
