import os
import sqlite3
import re
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Allow test override for isolated database
DATABASE = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'data', 'college_events.db'))


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't exist and seed sample events."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT    NOT NULL,
            category      TEXT    NOT NULL,
            description   TEXT    NOT NULL,
            event_date    TEXT    NOT NULL,
            event_time    TEXT    NOT NULL,
            venue         TEXT    NOT NULL,
            organizer     TEXT    NOT NULL,
            max_participants INTEGER NOT NULL DEFAULT 100,
            status        TEXT    NOT NULL DEFAULT 'Upcoming',
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id       INTEGER NOT NULL,
            student_name   TEXT    NOT NULL,
            email          TEXT    NOT NULL,
            department     TEXT    NOT NULL,
            year           TEXT    NOT NULL,
            status         TEXT    NOT NULL DEFAULT 'Confirmed',
            registered_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    # Seed sample events only if table is empty
    c.execute("SELECT COUNT(*) FROM events")
    if c.fetchone()[0] == 0:
        sample_events = [
            ('National Hackathon 2026', 'Hackathons',
             'A 24-hour coding challenge open to all engineering students. '
             'Build innovative solutions for real-world problems.',
             '2026-11-15', '09:00', 'Main Auditorium', 'CSE Department', 150),
            ('Web Development Workshop', 'Workshops',
             'Hands-on workshop covering modern web development with HTML, CSS, JavaScript and Flask.',
             '2026-11-20', '10:00', 'Lab Block 3', 'IT Department', 60),
            ('Techfest Symposium', 'Symposiums',
             'Annual technical symposium featuring paper presentations, project exhibitions and guest lectures.',
             '2026-12-05', '09:00', 'Seminar Hall', 'Technical Committee', 200),
            ('Cultural Night 2026', 'Cultural Events',
             'Annual cultural extravaganza featuring music, dance, drama and other performances.',
             '2026-11-30', '18:00', 'College Ground', 'Cultural Committee', 500),
            ('AI & ML Seminar', 'Seminars',
             'Expert talk on Artificial Intelligence and Machine Learning trends in industry and research.',
             '2026-11-10', '11:00', 'Seminar Hall B', 'AI Club', 120),
            ('Inter-College Cricket Tournament', 'Sports Events',
             'Inter-college cricket tournament. Teams of 11 players. Open to all departments.',
             '2026-12-10', '08:00', 'Sports Ground', 'Sports Department', 80),
        ]
        c.executemany(
            "INSERT INTO events (title, category, description, event_date, event_time, venue, organizer, max_participants) VALUES (?,?,?,?,?,?,?,?)",
            sample_events
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_registration_count(db, event_id):
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM registrations WHERE event_id=? AND status='Confirmed'",
        (event_id,)
    ).fetchone()
    return row['cnt'] if row else 0


def generate_reg_id(reg_id):
    return f"REG{reg_id:05d}"


# ---------------------------------------------------------------------------
# Student Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    upcoming = db.execute(
        "SELECT * FROM events WHERE status='Upcoming' AND event_date >= ? ORDER BY event_date LIMIT 6",
        (today,)
    ).fetchall()
    # Stats for hero section
    total_events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    total_regs   = db.execute("SELECT COUNT(*) FROM registrations WHERE status='Confirmed'").fetchone()[0]
    return render_template('index.html', upcoming_events=upcoming,
                           total_events=total_events, total_regs=total_regs)


@app.route('/events')
def events():
    db = get_db()
    category = request.args.get('category', '')
    search   = request.args.get('search', '').strip()

    query  = "SELECT * FROM events WHERE 1=1"
    params = []
    if category:
        query += " AND category=?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR venue LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    query += " ORDER BY event_date ASC"

    all_events = db.execute(query, params).fetchall()
    categories = [
        'Technical Events', 'Workshops', 'Hackathons', 'Cultural Events',
        'Sports Events', 'Seminars', 'Symposiums', 'Other'
    ]
    # Attach registration count to each event
    events_data = []
    for ev in all_events:
        cnt = get_registration_count(db, ev['id'])
        events_data.append({'event': ev, 'registered': cnt})

    return render_template('events.html', events_data=events_data,
                           categories=categories, selected_category=category, search=search)


@app.route('/event/<int:event_id>')
def event_details(event_id):
    db  = get_db()
    ev  = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('events'))
    cnt = get_registration_count(db, event_id)
    return render_template('event_details.html', event=ev, registered=cnt)


@app.route('/register/<int:event_id>')
def register(event_id):
    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('events'))
    cnt = get_registration_count(db, event_id)
    if ev['status'] not in ('Upcoming', 'Ongoing'):
        flash('Registration is not available for this event.', 'warning')
        return redirect(url_for('event_details', event_id=event_id))
    if cnt >= ev['max_participants']:
        flash('This event has reached maximum capacity.', 'warning')
        return redirect(url_for('event_details', event_id=event_id))
    departments = [
        'Computer Science Engineering', 'Information Technology',
        'Electronics & Communication', 'Electrical Engineering',
        'Mechanical Engineering', 'Civil Engineering',
        'Chemical Engineering', 'Biotechnology', 'Other'
    ]
    years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
    return render_template('register.html', event=ev, departments=departments, years=years)


@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    db           = get_db()
    event_id     = request.form.get('event_id', '').strip()
    student_name = request.form.get('student_name', '').strip()
    email        = request.form.get('email', '').strip().lower()
    department   = request.form.get('department', '').strip()
    year         = request.form.get('year', '').strip()

    # Basic validation
    if not all([event_id, student_name, email, department, year]):
        flash('All fields are required.', 'danger')
        return redirect(request.referrer or url_for('events'))

    if not event_id.isdigit():
        flash('Invalid event.', 'danger')
        return redirect(url_for('events'))

    event_id = int(event_id)

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('register', event_id=event_id))

    ev = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('events'))

    if ev['status'] not in ('Upcoming', 'Ongoing'):
        flash('Registration is closed for this event.', 'warning')
        return redirect(url_for('event_details', event_id=event_id))

    cnt = get_registration_count(db, event_id)
    if cnt >= ev['max_participants']:
        flash('Event capacity is full.', 'warning')
        return redirect(url_for('event_details', event_id=event_id))

    # Duplicate check
    dup = db.execute(
        "SELECT id FROM registrations WHERE event_id=? AND email=? AND status='Confirmed'",
        (event_id, email)
    ).fetchone()
    if dup:
        flash('You are already registered for this event with that email address.', 'warning')
        return redirect(url_for('event_details', event_id=event_id))

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = db.execute(
        "INSERT INTO registrations (event_id, student_name, email, department, year, status, registered_at) VALUES (?,?,?,?,?,?,?)",
        (event_id, student_name, email, department, year, 'Confirmed', now)
    )
    db.commit()
    reg_id_str = generate_reg_id(cur.lastrowid)
    flash(f'Registration successful! Your Registration ID is <strong>{reg_id_str}</strong>. '
          f'Please save this for tracking.', 'success')
    return redirect(url_for('track', reg_id=reg_id_str, email=email))


@app.route('/track')
def track():
    db     = get_db()
    reg_id = request.args.get('reg_id', '').strip().upper()
    email  = request.args.get('email', '').strip().lower()
    result = None
    error  = None

    if reg_id and email:
        # Convert REGxxxxx → integer id
        if reg_id.startswith('REG') and reg_id[3:].isdigit():
            rid = int(reg_id[3:])
            row = db.execute(
                """SELECT r.*, e.title as event_title, e.category, e.event_date,
                          e.event_time, e.venue, e.organizer, e.status as event_status
                   FROM registrations r
                   JOIN events e ON e.id = r.event_id
                   WHERE r.id=? AND LOWER(r.email)=?""",
                (rid, email)
            ).fetchone()
            if row:
                result = row
            else:
                error = 'No registration found with the provided ID and email.'
        else:
            error = 'Invalid Registration ID format. It should look like REG00001.'

    return render_template('track.html', result=result, error=error,
                           reg_id=reg_id, email=email)


# ---------------------------------------------------------------------------
# Admin Routes
# ---------------------------------------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome back, Administrator!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid password. Please try again.', 'danger')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')

    total_events    = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    upcoming_events = db.execute("SELECT COUNT(*) FROM events WHERE status='Upcoming' AND event_date >= ?", (today,)).fetchone()[0]
    completed_events= db.execute("SELECT COUNT(*) FROM events WHERE status='Completed'").fetchone()[0]
    total_regs      = db.execute("SELECT COUNT(*) FROM registrations WHERE status='Confirmed'").fetchone()[0]

    recent_events = db.execute(
        "SELECT e.*, (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id AND r.status='Confirmed') as reg_count FROM events e ORDER BY e.created_at DESC LIMIT 10"
    ).fetchall()

    recent_regs = db.execute(
        """SELECT r.id, r.student_name, r.email, r.department, r.year,
                  r.status, r.registered_at, e.title as event_title
           FROM registrations r JOIN events e ON e.id=r.event_id
           ORDER BY r.registered_at DESC LIMIT 10"""
    ).fetchall()

    return render_template('admin.html',
                           total_events=total_events,
                           upcoming_events=upcoming_events,
                           completed_events=completed_events,
                           total_regs=total_regs,
                           recent_events=recent_events,
                           recent_regs=recent_regs)


@app.route('/admin/create_event', methods=['GET', 'POST'])
@admin_required
def create_event():
    categories = [
        'Technical Events', 'Workshops', 'Hackathons', 'Cultural Events',
        'Sports Events', 'Seminars', 'Symposiums', 'Other'
    ]
    if request.method == 'POST':
        title            = request.form.get('title', '').strip()
        category         = request.form.get('category', '').strip()
        description      = request.form.get('description', '').strip()
        event_date       = request.form.get('event_date', '').strip()
        event_time       = request.form.get('event_time', '').strip()
        venue            = request.form.get('venue', '').strip()
        organizer        = request.form.get('organizer', '').strip()
        max_participants = request.form.get('max_participants', '').strip()

        if not all([title, category, description, event_date, event_time, venue, organizer, max_participants]):
            flash('All fields are required.', 'danger')
            return render_template('create_event.html', categories=categories)

        if not max_participants.isdigit() or int(max_participants) <= 0:
            flash('Max participants must be a positive number.', 'danger')
            return render_template('create_event.html', categories=categories)

        db  = get_db()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            "INSERT INTO events (title,category,description,event_date,event_time,venue,organizer,max_participants,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (title, category, description, event_date, event_time, venue, organizer, int(max_participants), 'Upcoming', now)
        )
        db.commit()
        flash(f'Event "{title}" created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_event.html', categories=categories)


@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    categories = [
        'Technical Events', 'Workshops', 'Hackathons', 'Cultural Events',
        'Sports Events', 'Seminars', 'Symposiums', 'Other'
    ]

    if request.method == 'POST':
        title            = request.form.get('title', '').strip()
        category         = request.form.get('category', '').strip()
        description      = request.form.get('description', '').strip()
        event_date       = request.form.get('event_date', '').strip()
        event_time       = request.form.get('event_time', '').strip()
        venue            = request.form.get('venue', '').strip()
        organizer        = request.form.get('organizer', '').strip()
        max_participants = request.form.get('max_participants', '').strip()
        status           = request.form.get('status', '').strip()

        if not all([title, category, description, event_date, event_time, venue, organizer, max_participants, status]):
            flash('All fields are required.', 'danger')
            return render_template('edit_event.html', event=ev, categories=categories)

        if not max_participants.isdigit() or int(max_participants) <= 0:
            flash('Max participants must be a positive number.', 'danger')
            return render_template('edit_event.html', event=ev, categories=categories)

        db.execute(
            "UPDATE events SET title=?,category=?,description=?,event_date=?,event_time=?,venue=?,organizer=?,max_participants=?,status=? WHERE id=?",
            (title, category, description, event_date, event_time, venue, organizer, int(max_participants), status, event_id)
        )
        db.commit()
        flash(f'Event "{title}" updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_event.html', event=ev, categories=categories)


@app.route('/admin/update_status', methods=['POST'])
@admin_required
def update_status():
    db       = get_db()
    event_id = request.form.get('event_id', '').strip()
    status   = request.form.get('status', '').strip()
    valid    = ('Upcoming', 'Ongoing', 'Completed', 'Cancelled')

    if not event_id.isdigit() or status not in valid:
        flash('Invalid request.', 'danger')
        return redirect(url_for('admin_dashboard'))

    ev = db.execute("SELECT title FROM events WHERE id=?", (int(event_id),)).fetchone()
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.execute("UPDATE events SET status=? WHERE id=?", (status, int(event_id)))
    # Cancel all confirmed registrations when event is cancelled
    if status == 'Cancelled':
        db.execute("UPDATE registrations SET status='Cancelled' WHERE event_id=? AND status='Confirmed'", (int(event_id),))
    db.commit()
    flash(f'Event status updated to "{status}".', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/registrations')
@admin_required
def admin_registrations():
    db       = get_db()
    event_id = request.args.get('event_id', '')

    events_list = db.execute("SELECT id, title FROM events ORDER BY title").fetchall()

    query  = """SELECT r.id, r.student_name, r.email, r.department, r.year,
                       r.status, r.registered_at, e.title as event_title, e.id as event_id
                FROM registrations r JOIN events e ON e.id=r.event_id"""
    params = []
    if event_id and event_id.isdigit():
        query += " WHERE r.event_id=?"
        params.append(int(event_id))
    query += " ORDER BY r.registered_at DESC"

    regs = db.execute(query, params).fetchall()
    return render_template('registrations.html', registrations=regs,
                           events_list=events_list, selected_event=event_id)


@app.route('/admin/cancel_registration', methods=['POST'])
@admin_required
def cancel_registration():
    db     = get_db()
    reg_id = request.form.get('reg_id', '').strip()
    if not reg_id.isdigit():
        flash('Invalid registration.', 'danger')
        return redirect(url_for('admin_registrations'))
    db.execute("UPDATE registrations SET status='Cancelled' WHERE id=?", (int(reg_id),))
    db.commit()
    flash(f'Registration {generate_reg_id(int(reg_id))} has been cancelled.', 'info')
    return redirect(url_for('admin_registrations'))


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
