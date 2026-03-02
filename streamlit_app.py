import streamlit as st
import os
from app.agents import (
    query_builder_agent,
    job_fetch_agent,
    ai_filter_agent,
    email_agent
)
from app.email_service import send_email
from app.excel_service import save_jobs_to_excel

st.set_page_config(page_title="AI Job Hunter ASP", layout="wide")

st.title("🤖 Autonomous AI Job Hunter")
st.markdown("Search → Filter → Generate Email → Apply")

# -------------------------------
# JOB FILTER SECTION
# -------------------------------

st.header("🔎 Job Preferences")

col1, col2, col3 = st.columns(3)

with col1:
    position = st.selectbox(
        "Select Position",
        [
            "DevOps Engineer",
            "MLOps Engineer",
            "Data Analyst",
            "Data Scientist",
            "Machine Learning Engineer",
            "AI Engineer",
            "Cloud Engineer",
            "Backend Developer",
            "Other"
        ]
    )

with col2:
    experience = st.selectbox(
        "Experience Level",
        [
            "Fresher",
            "0-1 years",
            "1-3 years",
            "3-5 years",
            "5+ years"
        ]
    )

with col3:
    location = st.selectbox(
        "Location",
        [
            "India",
            "USA",
            "Remote",
            "Europe",
            "Canada"
        ]
    )

skills = st.text_input("Enter Required Skills (comma separated)")

# -------------------------------
# CANDIDATE SECTION
# -------------------------------

st.header("👤 Candidate Details")

col4, col5 = st.columns(2)

with col4:
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

with col5:
    phone = st.text_input("Your Phone")
    profile = st.text_area("Short Profile Summary")
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
# -------------------------------
# SEARCH BUTTON
# -------------------------------

# -------------------------------
# SEARCH BUTTON
# -------------------------------

if st.button("🚀 Search Jobs"):

    user_input = f"""
    Position: {position}
    Experience: {experience}
    Location: {location}
    Skills: {skills}
    """

    optimized_query = query_builder_agent(user_input)
    jobs = job_fetch_agent(optimized_query)

    if jobs:
        filtered_jobs = ai_filter_agent(jobs, user_input)

        if filtered_jobs:
            st.session_state.jobs = filtered_jobs
            save_jobs_to_excel(filtered_jobs)
            st.success(f"{len(filtered_jobs)} jobs found!")
        else:
            st.warning("No matching jobs found.")
    else:
        st.error("No jobs found.")


# -------------------------------
# DISPLAY JOBS IF AVAILABLE
# -------------------------------

if "jobs" in st.session_state:

    st.subheader("📋 Filtered Jobs")

    for i, job in enumerate(st.session_state.jobs):
        with st.expander(f"{job['title']} - {job['company']}"):
            st.write("📍 Location:", job["location"])
            st.write("🔗 Link:", job["link"])
            st.write(job["description"])


    st.header("✉ Apply to First Job")

    candidate = {
        "name": name,
        "email": email,
        "phone": phone,
        "profile": profile
    }

    if st.button("Generate Email"):

        first_job = st.session_state.jobs[0]
        email_text = email_agent(first_job, candidate)

        st.session_state.generated_email = email_text


# -------------------------------
# SHOW GENERATED EMAIL
# -------------------------------
# -------------------------------
# SHOW GENERATED EMAIL
# -------------------------------

if "generated_email" in st.session_state:

    st.text_area("Generated Email", st.session_state.generated_email, height=300)

    hr_email = st.text_input("Enter HR Email")

    if st.button("📨 Send Email"):

        if not hr_email:
            st.warning("Please enter HR email.")
        else:
            first_job = st.session_state.jobs[0]
            resume_path = None

            # Save uploaded resume temporarily
            if resume_file:
                
            # Create pdf folder if not exists
                    os.makedirs("pdf", exist_ok=True)

                    resume_path = os.path.join("pdf", resume_file.name)

                    with open(resume_path, "wb") as f:
                        f.write(resume_file.getbuffer())

            try:
                send_email(
                    hr_email,
                    f"Application for {first_job['title']}",
                    st.session_state.generated_email,
                    attachment_path=resume_path
                )

                st.success("✅ Email Sent Successfully with Resume!")

            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")