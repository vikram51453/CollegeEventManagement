# 🎓 College Event Management System

A complete, professional **Flask-based College Event Management System** built as a DevOps mini-project. It demonstrates a full-stack web application integrated with a complete CI/CD pipeline using Git, GitHub, Jenkins, Docker, Pytest, Ansible, and Docker Volume for persistent storage.

---

## 📌 Problem Statement

College event management is often fragmented — announcements via notice boards, registrations through spreadsheets, and no real-time tracking for students. This project solves that by providing a centralised web portal where:

- **Students** can browse events, register, and track their participation.
- **Administrators** can create, manage, and monitor events through a dashboard.
- The entire system is containerised and deployable through an automated CI/CD pipeline.

---

## 🎯 Project Objectives

1. Build a functional college event management web application using Flask and SQLite.
2. Implement student registration with duplicate detection and capacity enforcement.
3. Provide an admin dashboard with full CRUD operations on events.
4. Containerise the application using Docker with persistent volume storage.
5. Write automated tests with Pytest covering all critical paths.
6. Build a Jenkins CI/CD pipeline (Build → Test → Deploy).
7. Deploy the container using Ansible for infrastructure automation.
8. Demonstrate persistent SQLite storage across container restarts.

---

## 👨‍🎓 Student Features

- Browse all college events with search and category filters.
- View complete event details (date, time, venue, organizer, capacity).
- Register for events using a form (name, email, department, year).
- Receive a unique **Registration ID** (e.g., `REG00042`) on successful registration.
- Track registration status using Registration ID + email.
- Capacity and duplicate registration enforced automatically.

## 🔐 Administrator Features

- Secure session-based admin login (password via environment variable).
- Dashboard with live summary stats (total events, upcoming, completed, registrations).
- Create, edit, and delete events.
- Update event status (Upcoming → Ongoing → Completed → Cancelled).
- View all student registrations with filtering by event.
- Cancel individual student registrations.
- All data sourced directly from SQLite.

---

## 🛠️ Technology Stack

| Layer       | Technology                      |
|-------------|----------------------------------|
| Frontend    | HTML5, CSS3, JavaScript         |
| Backend     | Python 3.11, Flask 2.x          |
| Database    | SQLite (via Python `sqlite3`)   |
| Testing     | Pytest                          |
| Container   | Docker (`python:3.11-slim`)     |
| Persistence | Docker Volume                   |
| CI/CD       | Jenkins (Declarative Pipeline)  |
| Deployment  | Ansible (`community.docker`)    |
| Version Ctrl| Git + GitHub                    |

---

## 🔄 Application Workflow

```
Student
  └─▶ Browse Events → Select Event → View Details → Register
        └─▶ Flask validates → SQLite stores → Registration ID returned
              └─▶ Student tracks with REG ID + email

Admin
  └─▶ Login → Dashboard → Create/Edit Events → View Registrations
        └─▶ Flask processes → SQLite updated → Changes visible to students
```

---

## 🗄️ Database Structure

**Database file:** `data/college_events.db`

### Table: `events`

| Column           | Type    | Description              |
|------------------|---------|--------------------------|
| id               | INTEGER | Primary key (autoincrement) |
| title            | TEXT    | Event title              |
| category         | TEXT    | Event category           |
| description      | TEXT    | Full description         |
| event_date       | TEXT    | Date (YYYY-MM-DD)        |
| event_time       | TEXT    | Time (HH:MM)             |
| venue            | TEXT    | Event location           |
| organizer        | TEXT    | Organising department    |
| max_participants | INTEGER | Maximum seat capacity    |
| status           | TEXT    | Upcoming/Ongoing/Completed/Cancelled |
| created_at       | TEXT    | Timestamp of creation    |

### Table: `registrations`

| Column        | Type    | Description                   |
|---------------|---------|-------------------------------|
| id            | INTEGER | Primary key (autoincrement)   |
| event_id      | INTEGER | Foreign key → events.id       |
| student_name  | TEXT    | Full name                     |
| email         | TEXT    | Student email                 |
| department    | TEXT    | Department name               |
| year          | TEXT    | Year of study                 |
| status        | TEXT    | Confirmed / Cancelled         |
| registered_at | TEXT    | Timestamp of registration     |

---

## 🚀 DevOps Workflow

```
Developer
  └─▶ git push → GitHub
        └─▶ Jenkins triggered (manual or webhook)
              ├─ Stage 1: docker build -t college-event-ci .
              ├─ Stage 2: docker run --rm ... python -m pytest test_app.py
              │     └─▶ If tests fail → pipeline stops here
              └─ Stage 3: Ansible playbook deploys container
                    └─▶ college-event-ansible running on port 5002
                          └─▶ SQLite stored in college_event_data volume
```

---

## 📁 Project Structure

```
CollegeEventManagement/
│
├── app.py                  ← Flask application (all routes + DB logic)
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Container build instructions
├── Jenkinsfile             ← CI/CD pipeline definition
├── event-deploy.yml        ← Ansible deployment playbook
├── test_app.py             ← Pytest automated tests (17 test cases)
├── .gitignore
├── .dockerignore
├── README.md
│
├── templates/
│   ├── base.html           ← Shared layout (navbar, footer, flash)
│   ├── index.html          ← Homepage with hero and featured events
│   ├── events.html         ← Events listing with search/filter
│   ├── event_details.html  ← Individual event detail page
│   ├── register.html       ← Student registration form
│   ├── track.html          ← Registration tracking page
│   ├── admin_login.html    ← Admin login page
│   ├── admin.html          ← Admin dashboard
│   ├── create_event.html   ← Create new event form
│   ├── edit_event.html     ← Edit existing event form
│   └── registrations.html  ← View/manage registrations
│
├── static/
│   ├── style.css           ← Full dark-theme stylesheet
│   └── script.js           ← Client-side interactions
│
└── data/
    └── .gitkeep            ← Keeps the folder tracked by Git
```

---

## ▶️ How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CollegeEventManagement.git
cd CollegeEventManagement
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

```bash
# Windows PowerShell
$env:ADMIN_PASSWORD  = "admin123"
$env:FLASK_SECRET_KEY = "my-secret-key"

# Linux/macOS
export ADMIN_PASSWORD=admin123
export FLASK_SECRET_KEY=my-secret-key
```

### 5. Run the Flask application

```bash
python app.py
```

Open your browser: **http://localhost:5000**

---

## 🐳 Docker

### Build the Docker image

```bash
docker build -t college-event-ci .
```

### Create the persistent Docker Volume

```bash
docker volume create college_event_data
```

### Run the container with persistent storage

```bash
docker run -d \
  --name college-event-ansible \
  -p 5002:5000 \
  -v college_event_data:/app/data \
  -e ADMIN_PASSWORD=admin123 \
  -e FLASK_SECRET_KEY=my-secret-key \
  --restart unless-stopped \
  college-event-ci
```

Open your browser: **http://localhost:5002**

### Stop and restart (data persists!)

```bash
docker stop college-event-ansible
docker rm   college-event-ansible
# Re-run the docker run command above — all data is preserved in the volume
```

### Verify persistent data

```bash
docker run --rm -v college_event_data:/data python:3.11-slim \
  python -c "import sqlite3; conn=sqlite3.connect('/data/college_events.db'); \
  print(conn.execute('SELECT COUNT(*) FROM events').fetchone())"
```

---

## 🧪 Running Pytest

### Locally

```bash
python -m pytest test_app.py -v
```

### Inside Docker

```bash
docker run --rm \
  -e ADMIN_PASSWORD=testpassword123 \
  -e DATABASE_PATH=/tmp/test_events.db \
  college-event-ci \
  python -m pytest test_app.py -v
```

### Test Coverage Summary (17 tests)

| # | Test Case |
|---|-----------|
| 1 | App initialises successfully |
| 2 | Homepage returns HTTP 200 |
| 3 | Events page returns HTTP 200 |
| 4 | Admin login with correct password |
| 5 | Admin login with wrong password is rejected |
| 6 | Unauthenticated admin access is blocked |
| 7 | Admin can create an event |
| 8 | Created event is stored in SQLite |
| 9 | Student can view an event |
| 10 | Student can register for an event |
| 11 | Registration is stored in SQLite |
| 12 | Duplicate registration is rejected |
| 13 | Registration blocked when event is full |
| 14 | Registration tracking returns correct data |
| 15 | Admin dashboard displays actual records |
| 16 | Admin can update event status |
| 17 | Registration blocked for cancelled events |

---

## ⚙️ Jenkins CI/CD Pipeline

### Pipeline Stages

```
Build → Test → Deploy with Ansible
```

**Stage 1 — Build:**
```groovy
docker build -t college-event-ci .
```
Builds the Docker image from the Dockerfile.

**Stage 2 — Test:**
```groovy
docker run --rm college-event-ci python -m pytest test_app.py -v
```
Runs all 17 Pytest tests inside Docker. If any test fails, the pipeline stops and deployment does **not** happen.

**Stage 3 — Deploy with Ansible:**
```groovy
docker cp event-deploy.yml ansible-docker-lab:/event-deploy.yml
docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /event-deploy.yml
```
Copies the latest Ansible playbook into the Ansible container and triggers deployment.

### Jenkins Prerequisites

1. Jenkins must be able to run `docker` commands (mount Docker socket or use Docker agent).
2. Two Jenkins credentials must be configured:
   - `COLLEGE_ADMIN_PASSWORD` — Secret text for the admin password.
   - `COLLEGE_FLASK_SECRET`   — Secret text for the Flask session secret.
3. The `ansible-docker-lab` container must be running and have:
   - The `community.docker` Ansible collection installed.
   - The Docker Python SDK (`pip install docker`) installed.
   - Access to the same Docker daemon (Docker socket mounted).
   - An `/inventory.ini` file with `localhost ansible_connection=local`.

---

## 🤖 Ansible Deployment

The playbook `event-deploy.yml`:

1. Creates the `college_event_data` Docker volume (idempotent).
2. Deploys the `college-event-ci` image as container `college-event-ansible`.
3. Mounts the volume to `/app/data` for persistent SQLite storage.
4. Exposes the application on host port `5002`.
5. Waits for the port to be ready before completing.
6. Prints a deployment summary.

### Run Ansible manually (from inside ansible-docker-lab)

```bash
docker exec ansible-docker-lab \
  ansible-playbook -i /inventory.ini /event-deploy.yml \
  -e "admin_password=admin123" -e "flask_secret=my-secret"
```

### Cancel/stop the container via Ansible

```bash
docker exec ansible-docker-lab \
  ansible-playbook -i /inventory.ini /event-deploy.yml \
  -e "container_state=stopped"
```

---

## 💾 Docker Volume Persistence

The `college_event_data` volume stores the SQLite database at `/app/data/college_events.db`.

**What this means:**
- Stop the container → data is **not lost**.
- Remove the container → data is **not lost**.
- Rebuild the image → redeploy → **all events and registrations remain intact**.

Only `docker volume rm college_event_data` would delete the data.

---

## 🔐 Required Environment Variables

| Variable         | Default               | Purpose                              |
|------------------|-----------------------|--------------------------------------|
| `ADMIN_PASSWORD` | `admin123`            | Administrator login password         |
| `FLASK_SECRET_KEY` | `dev-secret-key...` | Flask session signing secret         |
| `DATABASE_PATH`  | `data/college_events.db` | Override database file location   |
| `FLASK_DEBUG`    | `false`               | Enable Flask debug mode              |

> ⚠️ Never commit real passwords to GitHub. Use environment variables or Jenkins credentials.

---

## 🏗️ DevOps Environment Prerequisites

| Component | Requirement |
|-----------|-------------|
| Docker    | Installed and running on the host machine |
| Jenkins   | Running (Docker image or local install); must have Docker socket access |
| Ansible Container | `ansible-docker-lab` container running; `community.docker` collection + Docker SDK installed; Docker socket mounted |
| Python    | 3.11+ (for local dev only) |
| Git       | For version control and Jenkins checkout |
| GitHub    | Remote repository for code storage and Jenkins webhook |

### inventory.ini (inside ansible-docker-lab)

```ini
[local]
localhost ansible_connection=local
```

---

## 🌐 Access URLs

| Environment | URL |
|-------------|-----|
| Local Flask | http://localhost:5000 |
| Docker container | http://localhost:5002 |
| Admin login | http://localhost:5002/admin/login |
| Track Registration | http://localhost:5002/track |

---

## 🎓 Viva Demonstration Guide

### Demonstrate the application:
1. Open **http://localhost:5002** and show the homepage.
2. Go to **Events** → filter by category → click **View Details**.
3. Register as a student → copy the **Registration ID**.
4. Track the registration using the ID and email.
5. Log into **Admin** → show the dashboard stats.
6. Create a new event → verify it appears on the events page.
7. Update event status → cancel a registration.

### Demonstrate the DevOps pipeline:
1. Show the `Dockerfile` and explain each instruction.
2. Run `docker build -t college-event-ci .` live.
3. Run `python -m pytest test_app.py -v` and show all 17 tests passing.
4. Show the `Jenkinsfile` and explain Build → Test → Deploy stages.
5. Show `event-deploy.yml` and explain each Ansible task.
6. Stop the container, restart it, and show that all data is preserved (Docker Volume).

---

*Built with ❤️ for the College DevOps Laboratory · Python · Flask · SQLite · Docker · Jenkins · Ansible*
