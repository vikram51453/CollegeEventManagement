import os
import tempfile
import pytest
import json

# ── Point the app at a temp database before importing ──
os.environ.setdefault('ADMIN_PASSWORD', 'testpassword123')

import app as application
from app import init_db


@pytest.fixture
def client(tmp_path):
    """
    Create a fully isolated Flask test client using a temporary SQLite database.
    The temp database is destroyed after each test function.
    """
    db_file = str(tmp_path / 'test_events.db')
    application.DATABASE = db_file
    os.environ['DATABASE_PATH'] = db_file

    application.app.config['TESTING'] = True
    application.app.config['WTF_CSRF_ENABLED'] = False
    application.app.secret_key = 'test-secret-key'

    # Force fresh database on every test
    with application.app.app_context():
        init_db()

    with application.app.test_client() as c:
        yield c

    # Cleanup env override so tests don't bleed into each other
    del os.environ['DATABASE_PATH']


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def admin_login(client, password='testpassword123'):
    return client.post('/admin/login', data={'password': password}, follow_redirects=True)


def create_event(client, title='Test Hackathon', max_participants=50):
    return client.post('/admin/create_event', data={
        'title':            title,
        'category':         'Hackathons',
        'description':      'A test hackathon event for pytest.',
        'event_date':       '2027-06-15',
        'event_time':       '09:00',
        'venue':            'Lab Block 1',
        'organizer':        'Test Organizer',
        'max_participants': str(max_participants),
    }, follow_redirects=True)


def register_student(client, event_id, email='student@college.edu', name='Test Student'):
    return client.post('/submit_registration', data={
        'event_id':     str(event_id),
        'student_name': name,
        'email':        email,
        'department':   'Computer Science Engineering',
        'year':         '2nd Year',
    }, follow_redirects=True)


def get_first_event_id(client):
    """Return the id of the first event in the temp database."""
    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM events ORDER BY id LIMIT 1").fetchone()
        conn.close()
        return row['id'] if row else None


# ─────────────────────────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────────────────────────

# 1. Flask application initialises successfully
def test_app_initialises(client):
    assert client is not None

# 2. Homepage returns HTTP 200
def test_homepage(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'College Event Management' in resp.data

# 3. Events page returns HTTP 200
def test_events_page(client):
    resp = client.get('/events')
    assert resp.status_code == 200

# 4. Admin login with correct password succeeds
def test_admin_login_success(client):
    resp = admin_login(client)
    assert resp.status_code == 200
    assert b'Admin Dashboard' in resp.data or b'Dashboard' in resp.data

# 5. Incorrect password is rejected
def test_admin_login_fail(client):
    resp = client.post('/admin/login', data={'password': 'wrongpassword'}, follow_redirects=True)
    assert b'Invalid password' in resp.data

# 6. Unauthenticated access to admin dashboard redirects
def test_admin_protected(client):
    resp = client.get('/admin', follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin/login' in resp.headers['Location']

# 7. Admin can create an event
def test_admin_create_event(client):
    admin_login(client)
    resp = create_event(client, title='Pytest Event Alpha')
    assert resp.status_code == 200
    assert b'created successfully' in resp.data

# 8. Created event is stored in SQLite
def test_event_stored_in_db(client):
    admin_login(client)
    create_event(client, title='DB Storage Test Event')
    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        row = conn.execute("SELECT * FROM events WHERE title='DB Storage Test Event'").fetchone()
        conn.close()
    assert row is not None

# 9. Students can view an available event
def test_student_view_event(client):
    admin_login(client)
    create_event(client, title='Unique Visible Event XYZ')
    # Get the id of the event we just created (max id, not first)
    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM events WHERE title='Unique Visible Event XYZ' LIMIT 1").fetchone()
        conn.close()
        event_id = row['id']
    client.get('/admin/logout')
    resp = client.get(f'/event/{event_id}')
    assert resp.status_code == 200
    assert b'Unique Visible Event XYZ' in resp.data

# 10. Students can register for an event
def test_student_registration(client):
    admin_login(client)
    create_event(client)
    event_id = get_first_event_id(client)
    client.get('/admin/logout')
    resp = register_student(client, event_id)
    assert resp.status_code == 200
    assert b'REG' in resp.data

# 11. Registration info is stored in SQLite
def test_registration_stored_in_db(client):
    admin_login(client)
    create_event(client)
    event_id = get_first_event_id(client)
    client.get('/admin/logout')
    register_student(client, event_id, email='dbcheck@college.edu')
    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        row = conn.execute(
            "SELECT * FROM registrations WHERE email='dbcheck@college.edu'"
        ).fetchone()
        conn.close()
    assert row is not None

# 12. Duplicate active registration from same email is rejected
def test_duplicate_registration_rejected(client):
    admin_login(client)
    create_event(client)
    event_id = get_first_event_id(client)
    client.get('/admin/logout')
    register_student(client, event_id, email='dup@college.edu')
    resp = register_student(client, event_id, email='dup@college.edu')
    assert b'already registered' in resp.data

# 13. Registration is rejected when event is at full capacity
def test_registration_rejected_when_full(client):
    admin_login(client)
    create_event(client, title='Full Capacity Event ABC', max_participants=1)
    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM events WHERE title='Full Capacity Event ABC' LIMIT 1").fetchone()
        conn.close()
        event_id = row['id']
    client.get('/admin/logout')
    register_student(client, event_id, email='first@college.edu')
    resp = register_student(client, event_id, email='second@college.edu')
    assert b'full' in resp.data.lower() or b'capacity' in resp.data.lower()

# 14. Registration tracking returns correct information
def test_registration_tracking(client):
    admin_login(client)
    create_event(client)
    event_id = get_first_event_id(client)
    client.get('/admin/logout')
    register_student(client, event_id, email='track@college.edu', name='Tracker Student')

    with application.app.app_context():
        import sqlite3
        conn = sqlite3.connect(application.DATABASE)
        row = conn.execute(
            "SELECT id FROM registrations WHERE email='track@college.edu'"
        ).fetchone()
        conn.close()
        reg_id_str = f"REG{row[0]:05d}"

    resp = client.get(f'/track?reg_id={reg_id_str}&email=track@college.edu')
    assert resp.status_code == 200
    assert b'Tracker Student' in resp.data

# 15. Admin dashboard displays actual database records
def test_admin_dashboard_shows_records(client):
    admin_login(client)
    create_event(client, title='Dashboard Test Event')
    resp = client.get('/admin')
    assert resp.status_code == 200
    assert b'Dashboard Test Event' in resp.data

# 16. Admin can update event status
def test_admin_update_event_status(client):
    admin_login(client)
    create_event(client, title='Status Test Event')
    event_id = get_first_event_id(client)
    resp = client.post('/admin/update_status', data={
        'event_id': str(event_id),
        'status':   'Completed',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Completed' in resp.data

# 17. Registration is blocked for cancelled events
def test_registration_blocked_for_cancelled_event(client):
    admin_login(client)
    create_event(client, title='Cancelled Event')
    event_id = get_first_event_id(client)
    client.post('/admin/update_status', data={
        'event_id': str(event_id), 'status': 'Cancelled'
    }, follow_redirects=True)
    client.get('/admin/logout')
    resp = register_student(client, event_id, email='blocked@college.edu')
    assert b'Registration is closed' in resp.data or b'not available' in resp.data.lower()
