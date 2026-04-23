import schedule
import time
from datetime import datetime
from database import get_all_applications, update_send_schedule, migrate_database
from email_sender import send_email

def check_and_send_emails():
    """
    Checks for applications with scheduled sends and sends emails if time has come.
    """
    applications = get_all_applications()
    now = datetime.now()

    for app in applications:
        app_id = app[0]
        company_name = app[1]
        contact_email = app[4]
        generated_email = app[6]
        send_scheduled = app[8]
        send_time_str = app[9]

        if send_scheduled and generated_email and send_time_str:
            try:
                send_time = datetime.fromisoformat(send_time_str)
                if now >= send_time:
                    # Send the email
                    subject = generated_email.split('\n')[0].replace('Subject: ', '') if 'Subject:' in generated_email else f"Application for {app[2]} at {company_name}"
                    body = generated_email
                    if send_email(contact_email, subject, body):
                        # Mark as sent by clearing schedule
                        update_send_schedule(app_id, 0, None)
                        print(f"Email sent for {company_name}")
                    else:
                        print(f"Failed to send email for {company_name}")
            except ValueError as e:
                print(f"Invalid send time for app {app_id}: {e}")

def run_scheduler():
    """
    Runs the scheduler to check every minute.
    """
    migrate_database()  # Ensure database is up to date
    schedule.every(1).minutes.do(check_and_send_emails)

    print("Scheduler started. Checking for emails to send every minute...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()