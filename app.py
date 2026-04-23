import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    create_table,
    add_application,
    get_all_applications,
    update_status,
    save_generated_email,
    update_send_schedule,
    migrate_database,
    delete_application
)
from ai_email import generate_cold_email

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)

# ---- INIT DATABASE ----
create_table()
migrate_database()

# ---- HEADER ----
st.title("💼 AI Job Application Tracker")
st.markdown("Track your applications, generate AI emails, and manage your job hunt — all in one place.")
st.divider()

# ---- SIDEBAR — ADD NEW JOB ----
with st.sidebar:
    st.header("➕ Add New Job")

    with st.form("add_job_form", clear_on_submit=True):
        company_name = st.text_input("Company Name", placeholder="e.g. Google")
        job_title = st.text_input("Job Title", placeholder="e.g. AI Engineer Intern")
        job_description = st.text_area("Job Description", placeholder="Paste the job description here...", height=150)
        contact_email = st.text_input("HR Email", placeholder="e.g. hr@company.com")
        submitted = st.form_submit_button("Add Application", use_container_width=True)

        if submitted:
            if company_name and job_title and job_description and contact_email:
                add_application(company_name, job_title, job_description, contact_email)
                st.success(f"✅ Added {company_name} - {job_title}")
                st.rerun()
            else:
                st.error("Please fill in all fields.")

# ---- FETCH ALL APPLICATIONS ----
applications = get_all_applications()

if not applications:
    st.info("No applications yet. Add your first job from the sidebar!")
else:
    # ---- STATS ROW ----
    from collections import Counter
    status_counts = Counter(app[5] for app in applications)
    total = len(applications)
    applied = status_counts.get("Applied", 0)
    interviews = status_counts.get("Interview", 0)
    rejected = status_counts.get("Rejected", 0)
    not_applied = status_counts.get("Not Applied", 0)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", total)
    col2.metric("Not Applied", not_applied)
    col3.metric("Applied", applied)
    col4.metric("Interviews", interviews)
    col5.metric("Rejected", rejected)

    st.divider()

    # ---- FILTER ----
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Not Applied", "Applied", "Interview", "Rejected"]
    )

    # ---- APPLICATION CARDS ----
    for app in applications:
        app_id = app[0]
        comp = app[1]
        title = app[2]
        desc = app[3]
        email_addr = app[4]
        status = app[5]
        gen_email = app[6]
        date = app[7]

        # Apply filter
        if status_filter != "All" and status != status_filter:
            continue

        # Color code by status
        color_map = {
            "Not Applied": "🔵",
            "Applied": "🟡",
            "Interview": "🟢",
            "Rejected": "🔴"
        }
        icon = color_map.get(status, "🔵")

        with st.expander(f"{icon} {comp} — {title} | {status} | Added: {date}"):
            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.markdown("**📋 Job Description:**")
                st.write(desc)
                st.markdown(f"**📧 HR Email:** `{email_addr}`")

            with col_right:
                st.markdown("**📊 Update Status:**")
                new_status = st.selectbox(
                    "Status",
                    ["Not Applied", "Applied", "Interview", "Rejected"],
                    index=["Not Applied", "Applied", "Interview", "Rejected"].index(status),
                    key=f"status_{app_id}"
                )
                if st.button("Update", key=f"update_{app_id}"):
                    update_status(app_id, new_status)
                    st.success("Status updated!")
                    st.rerun()

            st.divider()

            # ---- AI EMAIL SECTION ----
            st.markdown("**🤖 AI Generated Email:**")

            if gen_email:
                st.text_area(
                    "Generated Email",
                    value=gen_email,
                    height=250,
                    key=f"email_{app_id}"
                )
                if st.button("🔄 Regenerate Email", key=f"regen_{app_id}"):
                    with st.spinner("Generating new email..."):
                        new_email = generate_cold_email(comp, title, desc)
                        save_generated_email(app_id, new_email)
                        st.success("Email regenerated!")
                        st.rerun()
            else:
                st.info("No email generated yet.")
                if st.button("✨ Generate Email", key=f"gen_{app_id}"):
                    with st.spinner("AI is writing your email..."):
                        new_email = generate_cold_email(comp, title, desc)
                        save_generated_email(app_id, new_email)
                        st.success("Email generated!")
                        st.rerun()

            st.divider()

            # ---- EMAIL SCHEDULING SECTION ----
            st.markdown("**📅 Schedule Email Send:**")

            send_scheduled = bool(app[8]) if len(app) > 8 else False
            send_time_str = app[9] if len(app) > 9 else None

            schedule_send = st.checkbox("Schedule to send automatically", value=send_scheduled, key=f"schedule_{app_id}")

            if schedule_send:
                if send_time_str:
                    try:
                        default_time = datetime.fromisoformat(send_time_str)
                    except:
                        default_time = datetime.now()
                else:
                    default_time = datetime.now()

                send_datetime = st.date_input("Send Date", value=default_time.date(), key=f"date_{app_id}")
                send_time = st.time_input("Send Time", value=default_time.time(), key=f"time_{app_id}")
                combined_datetime = datetime.combine(send_datetime, send_time)

                if st.button("Set Schedule", key=f"set_schedule_{app_id}"):
                    update_send_schedule(app_id, 1, combined_datetime.isoformat())
                    st.success(f"Email scheduled for {combined_datetime}")
                    st.rerun()
            else:
                if send_scheduled:
                    if st.button("Cancel Schedule", key=f"cancel_{app_id}"):
                        update_send_schedule(app_id, 0, None)
                        st.success("Schedule cancelled!")
                        st.rerun()

            st.divider()

            # ---- DELETE SECTION ----
            if st.button("🗑️ Delete Application", key=f"delete_{app_id}", type="secondary"):
                delete_application(app_id)
                st.success("Application deleted!")
                st.rerun()