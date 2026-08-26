from pypdf import PdfReader
from pydantic import BaseModel
import os
import json
import re

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# 1. READ RESUME PDF
# ============================================================

resume_path = "SWARNABHA_DUTTA_FULLSTACK_MERN_2025.pdf"

reader = PdfReader(resume_path)

resume_text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        resume_text += page_text + "\n"


# ============================================================
# 2. CANDIDATE SCHEMA
# ============================================================

class Candidate(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    skills: list[str]
    languages: list[str]
    projects: list[str]


# ============================================================
# 3. JOB DESCRIPTION SCHEMA
# ============================================================

class JobDescription(BaseModel):
    job_title: str
    minimum_experience_years: float

    required_skills: list[str]
    preferred_skills: list[str]

    required_languages: list[str]
    preferred_languages: list[str]

    required_domain_experience: list[str]
    preferred_domain_experience: list[str]


# ============================================================
# 4. LOAD GROQ API
# ============================================================

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!!")

model = "openai/gpt-oss-120b"

client = Groq(api_key=my_api_key)


# ============================================================
# 5. EXTRACT CANDIDATE INFORMATION
# ============================================================

candidate_user_prompt = f"""
This is a candidate resume.

Extract the candidate information strictly based on the schema.

DO NOT invent or assume information.

If a field is not explicitly available in the resume,
return an empty string or empty list as appropriate.

Resume:

{resume_text}
"""

candidate_schema = Candidate.model_json_schema()

response_format = {
    "type": "json_object"
}

candidate_system_prompt = f"""
You are a resume information extraction system.

Extract candidate information strictly based on the schema
and return the output in JSON format.

Rules:

1. Do NOT invent information.
2. Do NOT assume information.
3. Only extract information explicitly available in the resume.
4. If information is missing, return an empty string or empty list.
5. Keep skills as individual items.
6. Keep projects as individual project names.

Schema:

{candidate_schema}
"""

candidate_messages = [
    {
        "role": "system",
        "content": candidate_system_prompt
    },
    {
        "role": "user",
        "content": candidate_user_prompt
    }
]


candidate_response = client.chat.completions.create(
    model=model,
    messages=candidate_messages,
    response_format=response_format
)


# ============================================================
# 6. CONVERT CANDIDATE RESPONSE
# ============================================================

raw_candidate_answer = candidate_response.choices[0].message.content

print("===== RAW CANDIDATE JSON =====")
print(raw_candidate_answer)

compiled_candidate_data = json.loads(raw_candidate_answer)

print("\n===== CANDIDATE JSON KEYS =====")
print(compiled_candidate_data.keys())

candidate_data = Candidate(**compiled_candidate_data)


# ============================================================
# 7. DISPLAY CANDIDATE INFORMATION
# ============================================================

print("\n========================================")
print("        CANDIDATE INFORMATION")
print("========================================")

print("Name:", candidate_data.name)
print("Email:", candidate_data.email)
print("Phone:", candidate_data.phone)
print("Location:", candidate_data.location)
print("Skills:", candidate_data.skills)
print("Languages:", candidate_data.languages)
print("Projects:", candidate_data.projects)


# ============================================================
# 8. READ JOB DESCRIPTION
# ============================================================

with open(
    "job_description.txt",
    "r",
    encoding="utf-8"
) as file:

    jd_text = file.read()


print("\n========================================")
print("          JOB DESCRIPTION")
print("========================================")

print(jd_text)


# ============================================================
# 9. EXTRACT STRUCTURED JD
# ============================================================

jd_user_prompt = f"""
This is a real-world job description written in
normal human-readable text.

Extract the hiring requirements strictly based
on the schema.

DO NOT invent or assume any requirement.

Only extract information explicitly mentioned
in the job description.

Separate required requirements from preferred
requirements.

Job Description:

{jd_text}
"""

jd_schema = JobDescription.model_json_schema()

jd_system_prompt = f"""
You are an HR job-description extraction system.

Extract the job requirements strictly based on
the schema and return the output in JSON format.

Rules:

1. Do NOT invent information.
2. Do NOT assume a skill is required.
3. Keep required and preferred requirements separate.
4. Extract the minimum experience requirement
   if explicitly mentioned.
5. Extract languages only when explicitly mentioned.
6. Extract domain experience only when explicitly mentioned.
7. If something is unavailable, return an empty
   list or 0 as appropriate.
8. Do not convert preferred requirements into required ones.

Schema:

{jd_schema}
"""

jd_messages = [
    {
        "role": "system",
        "content": jd_system_prompt
    },
    {
        "role": "user",
        "content": jd_user_prompt
    }
]


jd_response = client.chat.completions.create(
    model=model,
    messages=jd_messages,
    response_format=response_format
)


# ============================================================
# 10. CONVERT JD RESPONSE
# ============================================================

raw_jd_answer = jd_response.choices[0].message.content

print("\n===== RAW JD JSON =====")
print(raw_jd_answer)

compiled_jd_data = json.loads(raw_jd_answer)

print("\n===== JD JSON KEYS =====")
print(compiled_jd_data.keys())

job_data = JobDescription(**compiled_jd_data)


# ============================================================
# 11. DISPLAY STRUCTURED JD
# ============================================================

print("\n========================================")
print("       STRUCTURED JOB DESCRIPTION")
print("========================================")

print("Job Title:", job_data.job_title)

print(
    "Minimum Experience:",
    job_data.minimum_experience_years,
    "years"
)

print(
    "Required Skills:",
    job_data.required_skills
)

print(
    "Preferred Skills:",
    job_data.preferred_skills
)

print(
    "Required Languages:",
    job_data.required_languages
)

print(
    "Preferred Languages:",
    job_data.preferred_languages
)

print(
    "Required Domain Experience:",
    job_data.required_domain_experience
)

print(
    "Preferred Domain Experience:",
    job_data.preferred_domain_experience
)


# ============================================================
# 12. NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:

    text = text.lower().strip()

    # Remove special characters
    text = re.sub(r"[^a-z0-9+#./\s-]", " ", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# 13. MATCH LIST ITEMS
# ============================================================

def match_items(
    candidate_items: list[str],
    required_items: list[str]
):
    """
    Compare candidate information against JD requirements.

    Uses normalized exact/partial matching.
    """

    candidate_normalized = [
        normalize_text(item)
        for item in candidate_items
    ]

    matched = []
    missing = []

    for required_item in required_items:

        normalized_required = normalize_text(required_item)

        found = False

        for candidate_item in candidate_normalized:

            # Exact match
            if normalized_required == candidate_item:
                found = True
                break

            # Candidate contains requirement
            if normalized_required in candidate_item:
                found = True
                break

            # Requirement contains candidate skill
            if candidate_item in normalized_required:
                found = True
                break

        if found:
            matched.append(required_item)
        else:
            missing.append(required_item)

    return matched, missing


# ============================================================
# 14. SKILL MATCHING
# ============================================================

required_skill_matches, missing_required_skills = match_items(
    candidate_data.skills,
    job_data.required_skills
)

preferred_skill_matches, missing_preferred_skills = match_items(
    candidate_data.skills,
    job_data.preferred_skills
)


# ============================================================
# 15. LANGUAGE MATCHING
# ============================================================

required_language_matches, missing_required_languages = match_items(
    candidate_data.languages,
    job_data.required_languages
)

preferred_language_matches, missing_preferred_languages = match_items(
    candidate_data.languages,
    job_data.preferred_languages
)


# ============================================================
# 16. DOMAIN MATCHING
# ============================================================

candidate_domain_items = (
    candidate_data.skills
    + candidate_data.projects
)

required_domain_matches, missing_required_domains = match_items(
    candidate_domain_items,
    job_data.required_domain_experience
)

preferred_domain_matches, missing_preferred_domains = match_items(
    candidate_domain_items,
    job_data.preferred_domain_experience
)


# ============================================================
# 17. EXPERIENCE EXTRACTION
# ============================================================

experience_prompt = f"""
Analyze the following candidate resume.

Estimate the candidate's total professional
software engineering / AI application experience
based ONLY on explicitly mentioned employment,
internship, or professional experience.

Do not count education as experience.

Do not invent experience.

Return ONLY valid JSON in this format:

{{
    "experience_years": 0.0
}}

Resume:

{resume_text}
"""


experience_system_prompt = """
You are an HR experience extraction system.

Calculate the candidate's professional experience
based only on explicit dates and work experience
mentioned in the resume.

Rules:

1. Do not count education.
2. Do not count personal projects as professional experience.
3. Do not invent dates.
4. Internship experience may be counted as professional experience.
5. Return only JSON.
"""


experience_messages = [
    {
        "role": "system",
        "content": experience_system_prompt
    },
    {
        "role": "user",
        "content": experience_prompt
    }
]


experience_response = client.chat.completions.create(
    model=model,
    messages=experience_messages,
    response_format=response_format
)


raw_experience_answer = (
    experience_response
    .choices[0]
    .message
    .content
)

experience_data = json.loads(raw_experience_answer)

candidate_experience_years = float(
    experience_data.get("experience_years", 0)
)


# ============================================================
# 18. EXPERIENCE MATCH
# ============================================================

required_experience = job_data.minimum_experience_years

if candidate_experience_years >= required_experience:

    experience_match = True

else:

    experience_match = False


# ============================================================
# 19. CALCULATE REQUIRED SKILL SCORE
# ============================================================

if len(job_data.required_skills) > 0:

    required_skill_score = (
        len(required_skill_matches)
        / len(job_data.required_skills)
    ) * 100

else:

    required_skill_score = 100


# ============================================================
# 20. CALCULATE PREFERRED SKILL SCORE
# ============================================================

if len(job_data.preferred_skills) > 0:

    preferred_skill_score = (
        len(preferred_skill_matches)
        / len(job_data.preferred_skills)
    ) * 100

else:

    preferred_skill_score = 100


# ============================================================
# 21. CALCULATE LANGUAGE SCORE
# ============================================================

if len(job_data.required_languages) > 0:

    required_language_score = (
        len(required_language_matches)
        / len(job_data.required_languages)
    ) * 100

else:

    required_language_score = 100


if len(job_data.preferred_languages) > 0:

    preferred_language_score = (
        len(preferred_language_matches)
        / len(job_data.preferred_languages)
    ) * 100

else:

    preferred_language_score = 100


# ============================================================
# 22. CALCULATE DOMAIN SCORE
# ============================================================

if len(job_data.required_domain_experience) > 0:

    required_domain_score = (
        len(required_domain_matches)
        / len(job_data.required_domain_experience)
    ) * 100

else:

    required_domain_score = 100


if len(job_data.preferred_domain_experience) > 0:

    preferred_domain_score = (
        len(preferred_domain_matches)
        / len(job_data.preferred_domain_experience)
    ) * 100

else:

    preferred_domain_score = 100


# ============================================================
# 23. EXPERIENCE SCORE
# ============================================================

if required_experience <= 0:

    experience_score = 100

else:

    experience_score = min(
        (candidate_experience_years / required_experience) * 100,
        100
    )


# ============================================================
# 24. FINAL WEIGHTED MATCH SCORE
# ============================================================

"""
We give higher importance to mandatory requirements.

Weights:

Required Skills       = 35%
Preferred Skills      = 15%
Required Languages    = 10%
Preferred Languages   = 5%
Required Domain       = 10%
Preferred Domain      = 10%
Experience            = 15%

Total = 100%
"""


final_match_score = (

    required_skill_score * 0.35

    + preferred_skill_score * 0.15

    + required_language_score * 0.10

    + preferred_language_score * 0.05

    + required_domain_score * 0.10

    + preferred_domain_score * 0.10

    + experience_score * 0.15

)


final_match_score = round(final_match_score, 2)


# ============================================================
# 25. SHORTLIST DECISION
# ============================================================

"""
Important:

A candidate should NOT be shortlisted only because
the overall percentage is high.

Mandatory requirements matter.

If required skills are missing OR required language
is missing OR minimum experience is not satisfied,
the candidate should not automatically pass.

For this mini project we use:

- Overall score >= 70
- Required skill score >= 60
- Required language must be satisfied
- Minimum experience must be satisfied

"""


if (
    final_match_score >= 70
    and required_skill_score >= 60
    and experience_match
    and len(missing_required_languages) == 0
):

    shortlist_status = "SHORTLISTED"

else:

    shortlist_status = "NOT SHORTLISTED"


# ============================================================
# 26. DISPLAY MATCHING RESULTS
# ============================================================

print("\n")
print("========================================")
print("          RESUME MATCH ANALYSIS")
print("========================================")

print("\nCandidate:")
print(candidate_data.name)

print("\nJob:")
print(job_data.job_title)


# ------------------------------------------------------------
# Required Skills
# ------------------------------------------------------------

print("\n----------------------------------------")
print("REQUIRED SKILLS")
print("----------------------------------------")

print(
    "Matched:",
    required_skill_matches
)

print(
    "Missing:",
    missing_required_skills
)

print(
    "Score:",
    round(required_skill_score, 2),
    "%"
)


# ------------------------------------------------------------
# Preferred Skills
# ------------------------------------------------------------

print("\n----------------------------------------")
print("PREFERRED SKILLS")
print("----------------------------------------")

print(
    "Matched:",
    preferred_skill_matches
)

print(
    "Missing:",
    missing_preferred_skills
)

print(
    "Score:",
    round(preferred_skill_score, 2),
    "%"
)


# ------------------------------------------------------------
# Languages
# ------------------------------------------------------------

print("\n----------------------------------------")
print("LANGUAGE MATCH")
print("----------------------------------------")

print(
    "Required Matched:",
    required_language_matches
)

print(
    "Required Missing:",
    missing_required_languages
)

print(
    "Preferred Matched:",
    preferred_language_matches
)

print(
    "Preferred Missing:",
    missing_preferred_languages
)


# ------------------------------------------------------------
# Domain
# ------------------------------------------------------------

print("\n----------------------------------------")
print("DOMAIN EXPERIENCE")
print("----------------------------------------")

print(
    "Required Domain Matched:",
    required_domain_matches
)

print(
    "Required Domain Missing:",
    missing_required_domains
)

print(
    "Preferred Domain Matched:",
    preferred_domain_matches
)

print(
    "Preferred Domain Missing:",
    missing_preferred_domains
)


# ------------------------------------------------------------
# Experience
# ------------------------------------------------------------

print("\n----------------------------------------")
print("EXPERIENCE")
print("----------------------------------------")

print(
    "Candidate Experience:",
    round(candidate_experience_years, 2),
    "years"
)

print(
    "Required Experience:",
    required_experience,
    "years"
)

print(
    "Experience Requirement Met:",
    experience_match
)


# ------------------------------------------------------------
# Final Score
# ------------------------------------------------------------

print("\n========================================")
print("             FINAL RESULT")
print("========================================")

print(
    "Overall Match:",
    final_match_score,
    "%"
)

print(
    "Required Skill Score:",
    round(required_skill_score, 2),
    "%"
)

print(
    "Experience Score:",
    round(experience_score, 2),
    "%"
)

print(
    "Shortlist Decision:",
    shortlist_status
)

print("========================================")