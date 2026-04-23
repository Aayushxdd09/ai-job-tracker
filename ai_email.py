from groq import Groq
from database import get_all_applications, save_generated_email
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ⚠️ SET YOUR GROQ API KEY AS ENVIRONMENT VARIABLE: GROQ_API_KEY
API_KEY = os.getenv('GROQ_API_KEY')

if not API_KEY:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")

# Configure Groq client
client = Groq(api_key=API_KEY)


def generate_cold_email(company_name, job_title, job_description):
    """
    Takes job details and asks Groq AI to write a cold email.
    Returns the generated email as a string.
    """

    prompt = f"""
    You are a professional job application email writer.
    
    Write a short, professional cold email for a job application with these details:
    
    - Applicant Name: Ayush Soni
    - Applicant Skills: Python, Flask, REST APIs, AI tools, Data Automation
    - Company Name: {company_name}
    - Job Title: {job_title}
    - Job Description: {job_description}
    
    The email should:
    1. Be 150-200 words only
    2. Have a subject line at the top (start with "Subject:")
    3. Sound confident but not arrogant
    4. Mention 1-2 relevant skills that match the job description
    5. End with a call to action (asking for interview/call)
    6. Be ready to send — no placeholders like [Your Name]
    
    Return only the email. Nothing else.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Free, fast model on Groq
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating email: {e}")
        return "Error: Unable to generate email. Please check your API key and try again."


def generate_emails_for_all():
    """
    Loops through all applications in the database,
    generates an email for each one, and saves it back.
    """

    applications = get_all_applications()

    if not applications:
        print("No applications found in database. Add some first.")
        return

    print(f"Found {len(applications)} applications. Generating emails...\n")

    for app in applications:
        app_id = app[0]
        company_name = app[1]
        job_title = app[2]
        job_description = app[3]
        existing_email = app[6]  # index 6 is generated_email column

        # Skip if email already generated
        if existing_email:
            print(f"⏭️  Skipping {company_name} — email already exists.")
            continue

        print(f"Generating email for {company_name} - {job_title}...")

        try:
            time.sleep(2)  # Small delay between API calls
            email_text = generate_cold_email(company_name, job_title, job_description)
            save_generated_email(app_id, email_text)
            print(f"✅ Email saved for {company_name}\n")
            print("--- PREVIEW ---")
            print(email_text[:300])
            print("---------------\n")

        except Exception as e:
            print(f"❌ Error generating email for {company_name}: {e}")


def generate_email_for_one(app_id):
    """
    Generates and saves email for a single application by ID.
    Useful when you add a new job and want email for just that one.
    """

    applications = get_all_applications()

    target = None
    for app in applications:
        if app[0] == app_id:
            target = app
            break

    if not target:
        print(f"No application found with ID {app_id}")
        return

    company_name = target[1]
    job_title = target[2]
    job_description = target[3]

    print(f"Generating email for {company_name} - {job_title}...")

    try:
        email_text = generate_cold_email(company_name, job_title, job_description)
        save_generated_email(app_id, email_text)
        print(f"✅ Done! Email saved for {company_name}\n")
        print("--- FULL EMAIL ---")
        print(email_text)
        print("------------------")

    except Exception as e:
        print(f"❌ Error: {e}")


# Run this file directly to generate emails for all applications
if __name__ == "__main__":
    generate_emails_for_all()