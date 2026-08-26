import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

import os
import json
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        color: white;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        color: #d1d5db;
        font-size: 1.05rem;
    }

    .metric-card {
        padding: 1.2rem;
        border-radius: 14px;
        background: white;
        border: 1px solid #e5e7eb;
        text-align: center;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .match {
        color: #15803d;
        font-weight: 600;
    }

    .missing {
        color: #dc2626;
        font-weight: 600;
    }

    .shortlisted {
        padding: 1rem;
        border-radius: 12px;
        background-color: #dcfce7;
        color: #166534;
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
    }

    .not-shortlisted {
        padding: 1rem;
        border-radius: 12px;
        background-color: #fee2e2;
        color: #991b1b;
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<h1>🚀 AI Resume Screener</h1>

<p>
AI-powered resume screening and job matching system
for HR teams.
</p>
""", unsafe_allow_html=True)
# ============================================================
# LOAD API
# ============================================================

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    st.error("GROQ_API_KEY was not found in .env")
    st.stop()

client = Groq(api_key=my_api_key)

MODEL = "openai/gpt-oss-120b"


# ============================================================
# SCHEMAS
# ============================================================

class Candidate(BaseModel):

    name: str
    email: str
    phone: str
    location: str

    skills: list[str]
    languages: list[str]
    projects: list[str]


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
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ============================================================
# CANDIDATE EXTRACTION
# ============================================================

def extract_candidate(resume_text):

    schema = Candidate.model_json_schema()

    system_prompt = f"""
You are a professional resume information extraction system.

Extract candidate information strictly based on the schema.

Rules:

1. Do NOT invent information.
2. Do NOT assume information.
3. Only use information explicitly present in the resume.
4. Missing fields must be empty.
5. Return valid JSON only.

Schema:

{schema}
"""

    user_prompt = f"""
Extract candidate information from this resume.

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    raw_answer = response.choices[0].message.content

    data = json.loads(raw_answer)

    return Candidate(**data)


# ============================================================
# JD EXTRACTION
# ============================================================

def extract_jd(jd_text):

    schema = JobDescription.model_json_schema()

    system_prompt = f"""
You are an HR job-description extraction system.

Extract requirements from the JD strictly based on the schema.

Rules:

1. Do NOT invent requirements.
2. Keep required and preferred requirements separate.
3. Extract minimum experience if explicitly mentioned.
4. Extract languages only when explicitly mentioned.
5. Extract domain experience only when explicitly mentioned.
6. Return valid JSON only.

Schema:

{schema}
"""

    user_prompt = f"""
Extract structured hiring requirements from this job description.

Job Description:

{jd_text}
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    raw_answer = response.choices[0].message.content

    data = json.loads(raw_answer)

    return JobDescription(**data)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9+#./\s-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# MATCH ITEMS
# ============================================================

def match_items(
    candidate_items,
    required_items
):

    candidate_normalized = [
        normalize_text(item)
        for item in candidate_items
    ]

    matched = []
    missing = []

    for requirement in required_items:

        normalized_requirement = normalize_text(
            requirement
        )

        found = False

        for candidate_item in candidate_normalized:

            if normalized_requirement == candidate_item:

                found = True
                break

            if normalized_requirement in candidate_item:

                found = True
                break

            if candidate_item in normalized_requirement:

                found = True
                break

        if found:

            matched.append(requirement)

        else:

            missing.append(requirement)

    return matched, missing


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(resume_text):

    system_prompt = """
You are an HR experience extraction system.

Estimate professional software engineering or AI
application experience based ONLY on explicit
employment or internship experience.

Rules:

1. Do not count education.
2. Do not count personal projects.
3. Do not invent dates.
4. Internship experience may be counted.
5. Return JSON only.

Format:

{
    "experience_years": 0.0
}
"""

    user_prompt = f"""
Analyze this resume.

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    data = json.loads(
        response.choices[0].message.content
    )

    return float(
        data.get(
            "experience_years",
            0
        )
    )


# ============================================================
# ANALYSIS
# ============================================================

def analyze_candidate(
    candidate,
    job,
    resume_text
):

    # Skills

    required_skill_matches, missing_required_skills = match_items(
        candidate.skills,
        job.required_skills
    )

    preferred_skill_matches, missing_preferred_skills = match_items(
        candidate.skills,
        job.preferred_skills
    )

    # Languages

    required_language_matches, missing_required_languages = match_items(
        candidate.languages,
        job.required_languages
    )

    preferred_language_matches, missing_preferred_languages = match_items(
        candidate.languages,
        job.preferred_languages
    )

    # Domain

    candidate_domain_items = (
        candidate.skills +
        candidate.projects
    )

    required_domain_matches, missing_required_domains = match_items(
        candidate_domain_items,
        job.required_domain_experience
    )

    preferred_domain_matches, missing_preferred_domains = match_items(
        candidate_domain_items,
        job.preferred_domain_experience
    )

    # Experience

    experience_years = extract_experience(
        resume_text
    )

    required_experience = (
        job.minimum_experience_years
    )

    experience_match = (
        experience_years >= required_experience
    )

    # Scores

    required_skill_score = (
        len(required_skill_matches)
        / len(job.required_skills)
        * 100
        if job.required_skills
        else 100
    )

    preferred_skill_score = (
        len(preferred_skill_matches)
        / len(job.preferred_skills)
        * 100
        if job.preferred_skills
        else 100
    )

    required_language_score = (
        len(required_language_matches)
        / len(job.required_languages)
        * 100
        if job.required_languages
        else 100
    )

    preferred_language_score = (
        len(preferred_language_matches)
        / len(job.preferred_languages)
        * 100
        if job.preferred_languages
        else 100
    )

    required_domain_score = (
        len(required_domain_matches)
        / len(job.required_domain_experience)
        * 100
        if job.required_domain_experience
        else 100
    )

    preferred_domain_score = (
        len(preferred_domain_matches)
        / len(job.preferred_domain_experience)
        * 100
        if job.preferred_domain_experience
        else 100
    )

    experience_score = (

        min(
            experience_years /
            required_experience *
            100,
            100
        )

        if required_experience > 0

        else 100
    )

    # Final score

    final_score = (

        required_skill_score * 0.35

        + preferred_skill_score * 0.15

        + required_language_score * 0.10

        + preferred_language_score * 0.05

        + required_domain_score * 0.10

        + preferred_domain_score * 0.10

        + experience_score * 0.15
    )

    final_score = round(
        final_score,
        2
    )

    # Shortlist

    shortlisted = (

        final_score >= 70

        and required_skill_score >= 60

        and experience_match

        and len(missing_required_languages) == 0
    )

    return {

        "required_skill_matches":
            required_skill_matches,

        "missing_required_skills":
            missing_required_skills,

        "preferred_skill_matches":
            preferred_skill_matches,

        "missing_preferred_skills":
            missing_preferred_skills,

        "required_language_matches":
            required_language_matches,

        "missing_required_languages":
            missing_required_languages,

        "preferred_language_matches":
            preferred_language_matches,

        "missing_preferred_languages":
            missing_preferred_languages,

        "required_domain_matches":
            required_domain_matches,

        "missing_required_domains":
            missing_required_domains,

        "preferred_domain_matches":
            preferred_domain_matches,

        "missing_preferred_domains":
            missing_preferred_domains,

        "experience_years":
            experience_years,

        "required_experience":
            required_experience,

        "experience_match":
            experience_match,

        "required_skill_score":
            round(required_skill_score, 2),

        "preferred_skill_score":
            round(preferred_skill_score, 2),

        "experience_score":
            round(experience_score, 2),

        "final_score":
            final_score,

        "shortlisted":
            shortlisted
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📋 Screening Setup")

    st.write(
        "Upload a candidate resume and provide "
        "the job description."
    )

    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

    jd_file = st.file_uploader(
        "Upload Job Description",
        type=["txt"]
    )

    st.divider()

    st.caption(
        "AI Resume Screener • Day 5 Mini Project"
    )


# ============================================================
# MAIN INPUT AREA
# ============================================================

st.markdown(
    '<div class="section-title">📥 Candidate Screening</div>',
    unsafe_allow_html=True
)

if resume_file is None:

    st.info(
        "Upload a candidate resume PDF from the sidebar."
    )

if jd_file is None:

    st.info(
        "Upload the job description TXT file from the sidebar."
    )


# ============================================================
# RUN ANALYSIS
# ============================================================

if resume_file and jd_file:

    st.success(
        "Resume and Job Description uploaded successfully."
    )

    if st.button(
        "🚀 Analyze Candidate",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Reading resume and analyzing candidate..."
            ):

                # Resume

                resume_text = extract_pdf_text(
                    resume_file
                )

                # JD

                jd_text = jd_file.read().decode(
                    "utf-8"
                )

                # Candidate

                candidate = extract_candidate(
                    resume_text
                )

                # JD

                job = extract_jd(
                    jd_text
                )

                # Analysis

                result = analyze_candidate(
                    candidate,
                    job,
                    resume_text
                )


            # ====================================================
            # RESULT HEADER
            # ====================================================

            st.divider()

            st.markdown(
                '<div class="section-title">📊 Screening Result</div>',
                unsafe_allow_html=True
            )


            # ====================================================
            # TOP METRICS
            # ====================================================

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Match Score",
                    f"{result['final_score']}%"
                )

            with col2:

                st.metric(
                    "Experience",
                    f"{result['experience_years']:.1f} yrs"
                )

            with col3:

                st.metric(
                    "Required Skills",
                    f"{len(result['required_skill_matches'])}/"
                    f"{len(job.required_skills)}"
                )

            with col4:

                st.metric(
                    "Preferred Skills",
                    f"{len(result['preferred_skill_matches'])}/"
                    f"{len(job.preferred_skills)}"
                )


            # ====================================================
            # SHORTLIST STATUS
            # ====================================================

            if result["shortlisted"]:

                st.markdown(
                    """
                    <div class="shortlisted">
                        ✅ SHORTLISTED
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="not-shortlisted">
                        ❌ NOT SHORTLISTED
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ====================================================
            # CANDIDATE PROFILE
            # ====================================================

            st.markdown(
                '<div class="section-title">👤 Candidate Profile</div>',
                unsafe_allow_html=True
            )

            profile_col1, profile_col2 = st.columns(2)

            with profile_col1:

                st.write(
                    f"**Name:** {candidate.name}"
                )

                st.write(
                    f"**Email:** {candidate.email}"
                )

                st.write(
                    f"**Phone:** {candidate.phone}"
                )

            with profile_col2:

                st.write(
                    f"**Location:** {candidate.location}"
                )

                st.write(
                    f"**Target Role:** {job.job_title}"
                )

                st.write(
                    f"**Required Experience:** "
                    f"{job.minimum_experience_years} years"
                )


            # ====================================================
            # SKILLS
            # ====================================================

            st.markdown(
                '<div class="section-title">🧠 Skills Analysis</div>',
                unsafe_allow_html=True
            )

            skill_col1, skill_col2 = st.columns(2)

            with skill_col1:

                st.subheader(
                    "✅ Matched Required Skills"
                )

                if result["required_skill_matches"]:

                    for skill in result[
                        "required_skill_matches"
                    ]:

                        st.write(
                            f"✓ {skill}"
                        )

                else:

                    st.write(
                        "No required skills matched."
                    )

            with skill_col2:

                st.subheader(
                    "❌ Missing Required Skills"
                )

                if result["missing_required_skills"]:

                    for skill in result[
                        "missing_required_skills"
                    ]:

                        st.write(
                            f"• {skill}"
                        )

                else:

                    st.write(
                        "All required skills matched."
                    )


            # ====================================================
            # PREFERRED SKILLS
            # ====================================================

            st.subheader(
                "⭐ Preferred Skills"
            )

            preferred_col1, preferred_col2 = st.columns(2)

            with preferred_col1:

                st.write("**Matched:**")

                for skill in result[
                    "preferred_skill_matches"
                ]:

                    st.write(
                        f"✓ {skill}"
                    )

            with preferred_col2:

                st.write("**Missing:**")

                for skill in result[
                    "missing_preferred_skills"
                ]:

                    st.write(
                        f"• {skill}"
                    )


            # ====================================================
            # EXPERIENCE
            # ====================================================

            st.markdown(
                '<div class="section-title">💼 Experience Analysis</div>',
                unsafe_allow_html=True
            )

            experience_col1, experience_col2 = st.columns(2)

            with experience_col1:

                st.metric(
                    "Candidate Experience",
                    f"{result['experience_years']:.1f} years"
                )

            with experience_col2:

                st.metric(
                    "Required Experience",
                    f"{result['required_experience']:.1f} years"
                )

            if result["experience_match"]:

                st.success(
                    "Candidate satisfies the minimum experience requirement."
                )

            else:

                st.error(
                    "Candidate does not satisfy the minimum experience requirement."
                )


            # ====================================================
            # LANGUAGE
            # ====================================================

            st.markdown(
                '<div class="section-title">🌐 Language Analysis</div>',
                unsafe_allow_html=True
            )

            language_col1, language_col2 = st.columns(2)

            with language_col1:

                st.subheader(
                    "Required Languages"
                )

                st.write(
                    "Matched:",
                    result[
                        "required_language_matches"
                    ]
                )

                st.write(
                    "Missing:",
                    result[
                        "missing_required_languages"
                    ]
                )

            with language_col2:

                st.subheader(
                    "Preferred Languages"
                )

                st.write(
                    "Matched:",
                    result[
                        "preferred_language_matches"
                    ]
                )

                st.write(
                    "Missing:",
                    result[
                        "missing_preferred_languages"
                    ]
                )


            # ====================================================
            # DOMAIN
            # ====================================================

            st.markdown(
                '<div class="section-title">🤖 Domain Experience</div>',
                unsafe_allow_html=True
            )

            domain_col1, domain_col2 = st.columns(2)

            with domain_col1:

                st.subheader(
                    "Matched Domain"
                )

                st.write(
                    result[
                        "preferred_domain_matches"
                    ]
                )

            with domain_col2:

                st.subheader(
                    "Missing Domain"
                )

                st.write(
                    result[
                        "missing_preferred_domains"
                    ]
                )


            # ====================================================
            # SCORE BREAKDOWN
            # ====================================================

            st.markdown(
                '<div class="section-title">📈 Score Breakdown</div>',
                unsafe_allow_html=True
            )

            st.progress(
                int(
                    result[
                        "required_skill_score"
                    ]
                )
            )

            st.write(
                "Required Skills:",
                f"{result['required_skill_score']}%"
            )

            st.progress(
                int(
                    result[
                        "preferred_skill_score"
                    ]
                )
            )

            st.write(
                "Preferred Skills:",
                f"{result['preferred_skill_score']}%"
            )

            st.progress(
                int(
                    result[
                        "experience_score"
                    ]
                )
            )

            st.write(
                "Experience:",
                f"{result['experience_score']}%"
            )


            # ====================================================
            # PROJECTS
            # ====================================================

            st.markdown(
                '<div class="section-title">🚀 Candidate Projects</div>',
                unsafe_allow_html=True
            )

            for project in candidate.projects:

                st.write(
                    f"• {project}"
                )


            # ====================================================
            # RAW DATA
            # ====================================================

            with st.expander(
                "🔍 View Structured Candidate Data"
            ):

                st.json(
                    candidate.model_dump()
                )


            with st.expander(
                "🔍 View Structured JD Data"
            ):

                st.json(
                    job.model_dump()
                )


        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )