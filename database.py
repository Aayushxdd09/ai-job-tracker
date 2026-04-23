import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = sqlite3.connect("job_tracker.db")
    try:
        yield conn
    finally:
        conn.close()

# This creates the main table where all job applications are stored
def create_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_description TEXT,
                contact_email TEXT,
                status TEXT DEFAULT 'Not Applied',
                generated_email TEXT,
                date_added TEXT DEFAULT (DATE('now')),
                send_scheduled INTEGER DEFAULT 0,
                send_time TEXT
            )
        ''')
        conn.commit()
    print("Table created successfully.")

def migrate_database():
    """Add missing columns to existing database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Check if columns exist and add them if not
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN send_scheduled INTEGER DEFAULT 0")
            print("Added send_scheduled column")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN send_time TEXT")
            print("Added send_time column")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.commit()

# This adds a new job application to the database
def add_application(company_name, job_title, job_description, contact_email):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications (company_name, job_title, job_description, contact_email)
            VALUES (?, ?, ?, ?)
        ''', (company_name, job_title, job_description, contact_email))
        conn.commit()
    print(f"Added: {company_name} - {job_title}")

# This fetches all applications from the database
def get_all_applications():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications")
        rows = cursor.fetchall()
    return rows

# This updates the status of an application (Applied, Interview, Rejected etc.)
def update_status(app_id, new_status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE applications SET status = ? WHERE id = ?
        ''', (new_status, app_id))
        conn.commit()
    print(f"Status updated for ID {app_id}")

# This saves the AI-generated email back into the database
def save_generated_email(app_id, email_text):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE applications SET generated_email = ? WHERE id = ?
        ''', (email_text, app_id))
        conn.commit()

# This updates the send schedule for an application
def update_send_schedule(app_id, send_scheduled, send_time):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE applications SET send_scheduled = ?, send_time = ? WHERE id = ?
        ''', (send_scheduled, send_time, app_id))
        conn.commit()
    print(f"Send schedule updated for ID {app_id}")

# Run this file directly to initialize the database
if __name__ == "__main__":
    create_table()

    # Adding 2 sample applications to test
    add_application(
        company_name="Google",
        job_title="AI Engineer Intern",
        job_description="Looking for Python developer with ML knowledge to build AI tools.",
        contact_email="careers@google.com"
    )

    add_application(
        company_name="Swiggy",
        job_title="Data Automation Analyst",
        job_description="Automate data pipelines and reporting using Python and SQL.",
        contact_email="hr@swiggy.in"
    )

    # Fetch and print all applications to verify
    print("\nAll Applications:")
    for row in get_all_applications():
        print(row)