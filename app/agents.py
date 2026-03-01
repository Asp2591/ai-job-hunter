import json
from serpapi import GoogleSearch
from google import genai
from app.config import GEMINI_API_KEY, SERPAPI_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def query_builder_agent(user_input):
    print("🧠 Building optimized job search query...")

    prompt = f"""
    Convert this job requirement into a clean Google job search query.

    User Requirement:
    {user_input}

    Return only the optimized search query.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()


def job_fetch_agent(query):
    print("🔎 Searching Google Jobs...")

    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = []

    if "jobs_results" in results:
        for job in results["jobs_results"]:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "link": job.get("related_links", [{}])[0].get("link", "")
            })

    print(f"✅ Fetched {len(jobs)} jobs")
    return jobs


def ai_filter_agent(jobs, user_input):
    print("🤖 AI Filtering jobs based on user requirements...")

    prompt = f"""
    User Requirement:
    {user_input}

    Below is job data in JSON format:
    {json.dumps(jobs)}

    IMPORTANT:
    - Return ONLY valid JSON
    - No markdown
    - No explanation
    - No backticks
    - Only pure JSON list
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw_text = response.text.strip()

    try:
        # Remove markdown if exists
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]

        filtered_jobs = json.loads(raw_text)
        print(f"✅ {len(filtered_jobs)} jobs matched AI filter")
        return filtered_jobs

    except Exception as e:
        print("⚠ AI formatting issue. Returning all jobs.")
        print("DEBUG Gemini Output:", raw_text)
        return jobs


def email_agent(job, candidate_details):
    print("✉ Generating Personalized Email...")

    prompt = f"""
    Write a professional job application email.

    Candidate:
    Name: {candidate_details['name']}
    Email: {candidate_details['email']}
    Phone: {candidate_details['phone']}
    Profile: {candidate_details['profile']}

    Job:
    {json.dumps(job)}

    Return only email body.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text