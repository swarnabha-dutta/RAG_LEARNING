# 🤖 Resume–JD Matching & Shortlisting System

An AI-powered resume screening system that analyzes a candidate's resume against a human-readable Job Description (JD), converts unstructured information into structured JSON, validates it using Pydantic, performs deterministic matching, calculates a weighted compatibility score, and generates a final shortlist decision.

---

## 📌 Project Overview

Recruiters often need to compare a candidate's resume with a Job Description and determine whether the candidate satisfies the role requirements.

This project automates that workflow.

The system accepts:

* A candidate resume in PDF format
* A normal human-readable Job Description in `.txt` format

It then uses an LLM to extract structured information from both sources and performs rule-based matching and scoring.

---

## 🧠 System Workflow

```text
                    RESUME PDF
                        │
                        ▼
                PDF Text Extraction
                        │
                        ▼
                  LLM Extraction
                        │
                        ▼
             Structured Candidate JSON
                        │
                        ▼
                Pydantic Validation
                        │
                        ▼
                Candidate Profile
                        │
                        │
                        │
                        │
                  JOB DESCRIPTION
                        │
                        ▼
               Human-readable JD Text
                        │
                        ▼
                  LLM Extraction
                        │
                        ▼
              Structured JD JSON
                        │
                        ▼
               Pydantic Validation
                        │
                        ▼
                Job Requirements
                        │
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
     Candidate Profile       Job Requirements
            │                       │
            └───────────┬───────────┘
                        ▼
                 Text Normalization
                        │
                        ▼
                Requirement Matching
                        │
                        ▼
                  Score Calculation
                        │
                        ▼
                 Shortlist Decision
```

---

# ✨ Features

## 1. Resume PDF Processing

The system reads a candidate resume from a PDF file and extracts its text using `pypdf`.

The extracted resume text is passed to the LLM for structured information extraction.

```text
Resume PDF
   ↓
PDF Text Extraction
   ↓
Raw Resume Text
   ↓
LLM
   ↓
Structured Candidate Data
```

---

## 2. Structured Candidate Extraction

The LLM extracts candidate information based on a predefined Pydantic schema.

Current candidate schema:

```python
class Candidate(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    skills: list[str]
    languages: list[str]
    projects: list[str]
```

The LLM output is converted into JSON and then validated using Pydantic.

---

## 3. Human-readable Job Description Processing

The system does **not** require the Job Description to already be JSON.

The JD is provided as a normal `.txt` file.

Example:

```text
Job Title: AI Engineer - LLM Applications

Requirements:

- Strong programming experience with Python.
- Experience working with LLM APIs.
- Experience building REST APIs.
- Experience with Git and databases.

Preferred Qualifications:

- Experience with RAG.
- Experience with Docker.
- Experience with CI/CD.
```

The system sends this normal text to the LLM.

The LLM extracts the hiring requirements into structured JSON.

---

## 4. Structured Job Description

The Job Description is represented using a Pydantic model:

```python
class JobDescription(BaseModel):
    job_title: str
    minimum_experience_years: float

    required_skills: list[str]
    preferred_skills: list[str]

    required_languages: list[str]
    preferred_languages: list[str]

    required_domain_experience: list[str]
    preferred_domain_experience: list[str]
```

Example structured output:

```json
{
  "job_title": "AI Engineer - LLM Applications",
  "minimum_experience_years": 1,
  "required_skills": [
    "Python",
    "LLM APIs",
    "Prompt engineering",
    "REST APIs",
    "Git"
  ],
  "preferred_skills": [
    "RAG",
    "Docker",
    "CI/CD"
  ],
  "required_languages": [
    "English"
  ],
  "preferred_languages": [
    "Hindi"
  ],
  "required_domain_experience": [],
  "preferred_domain_experience": [
    "AI-powered applications",
    "LLM-based applications"
  ]
}
```

---

# 🔍 5. Text Normalization

Before comparing candidate information with JD requirements, the system normalizes text.

The normalization process includes:

* Converting text to lowercase
* Removing unnecessary special characters
* Normalizing whitespace

Example:

```text
"Prompt Engineering"
        ↓
"prompt engineering"
```

This helps reduce simple formatting differences during matching.

---

# 🔗 6. Requirement Matching

The system compares candidate information with job requirements.

Matching is performed using:

* Exact matching
* Partial matching
* Normalized text comparison

For example:

```text
Candidate:
"LLM APIs (Google Gemini)"

JD:
"LLM APIs"

Result:
MATCHED
```

The system separately identifies:

```text
Matched Requirements
Missing Requirements
```

---

# 📊 7. Skill Matching

Required and preferred skills are evaluated separately.

Example:

```text
Required Skills

Matched:
✓ Python
✓ REST APIs
✓ Git
✓ LLM APIs

Missing:
✗ SQL or NoSQL
```

Preferred skills are also evaluated independently.

---

# 🌐 8. Language Matching

The system checks:

* Required languages
* Preferred languages

Required language requirements have a stronger effect on the final shortlist decision.

---

# 🧠 9. Domain Experience Matching

The system evaluates domain-related requirements using candidate skills and project information.

For example:

```text
JD:
AI-powered applications

Candidate Project:
AI Code Reviewer

Result:
Potential Domain Match
```

---

# ⏱️ 10. Experience Extraction

The system uses an LLM to estimate professional experience based only on explicitly mentioned employment or internship information.

The system does **not** count:

* Education
* Personal projects

Internship experience may be counted as professional experience.

Example output:

```json
{
  "experience_years": 0.17
}
```

---

# 📈 11. Weighted Matching Score

The project calculates an overall compatibility score using weighted components.

| Category            |   Weight |
| ------------------- | -------: |
| Required Skills     |      35% |
| Preferred Skills    |      15% |
| Required Languages  |      10% |
| Preferred Languages |       5% |
| Required Domain     |      10% |
| Preferred Domain    |      10% |
| Experience          |      15% |
| **Total**           | **100%** |

This gives higher importance to mandatory requirements.

---

# ✅ 12. Shortlist Decision

The system does not rely only on the overall percentage.

A candidate must satisfy the mandatory conditions.

Current rules:

```text
Overall Score >= 70
        AND
Required Skill Score >= 60
        AND
Required Languages satisfied
        AND
Minimum Experience satisfied
```

If all conditions are satisfied:

```text
SHORTLISTED
```

Otherwise:

```text
NOT SHORTLISTED
```

---

# 🛠️ Tech Stack

* Python
* Groq API
* GPT-OSS-120B
* Pydantic
* PyPDF
* JSON
* Regex
* Streamlit
* python-dotenv

---

# 📁 Project Structure

```text
day5_mini_project/
│
├── main.py
├── ui.py
├── job_description.txt
├── SWARNABHA_DUTTA_FULLSTACK_MERN_2025.pdf
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project:

```bash
cd day5_mini_project
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If using `uv`:

```bash
uv sync
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do **not** commit the `.env` file to GitHub.

Make sure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
```

---

# ▶️ Run the CLI Version

After activating the virtual environment:

```bash
python main.py
```

The program will:

1. Read the resume PDF
2. Extract candidate information
3. Read the Job Description
4. Extract structured JD requirements
5. Match candidate skills against the JD
6. Calculate scores
7. Generate a shortlist decision

---

# 🖥️ Run the Streamlit UI

Install Streamlit if required:

```bash
pip install streamlit
```

Then:

```bash
streamlit run ui.py
```

If using `uv`:

```bash
uv run streamlit run ui.py
```

The application will open in the browser.

---

# 🧪 How to Test the Project

## Test 1 — Change the Job Description

Open:

```text
job_description.txt
```

Replace its contents with another human-readable Job Description.

Example:

```text
Job Title: Backend Developer

Requirements:

- Strong experience with Python.
- Experience with REST APIs.
- Experience with PostgreSQL.
- Experience with Git.

Preferred:

- Docker
- Redis
- AWS
```

Run:

```bash
python main.py
```

The system should extract the new requirements automatically.

---

## Test 2 — Test Different Resumes

Replace the configured resume PDF with another resume and run:

```bash
python main.py
```

The candidate profile should change based on the new resume.

---

## Test 3 — Test Missing Skills

Use a JD containing skills that are not present in the resume.

The output should show:

```text
Matched:
...

Missing:
...
```

The final score should decrease accordingly.

---

## Test 4 — Test Required Language

Change the JD to require a language that the candidate does not have.

The shortlist decision should consider the missing required language.

---

## Test 5 — Test Experience Requirement

Increase the JD's minimum experience requirement.

The experience check should affect the final shortlist decision.

---

# 🧩 Important Design Principle

The project separates two responsibilities.

### LLM Responsibility

The LLM handles:

```text
Unstructured Text
       ↓
Structured Information
```

### Deterministic Python Responsibility

Python handles:

```text
Structured Information
       ↓
Matching
       ↓
Scoring
       ↓
Shortlist Decision
```

This prevents the LLM from directly deciding whether a candidate should be shortlisted.

---

# 🔐 Why Pydantic?

Pydantic provides a predefined structure for the extracted candidate and job data.

Instead of relying on arbitrary LLM output, the application expects a specific schema.

For example:

```python
class JobDescription(BaseModel):
    job_title: str
    minimum_experience_years: float
    required_skills: list[str]
    preferred_skills: list[str]
```

The extracted JSON is then converted into the Pydantic model.

This provides:

* Structured data
* Type validation
* Consistent application behavior
* Early detection of malformed LLM output

---

# 🚧 Current Limitations

This is an educational mini project and not a production-grade ATS.

Current limitations include:

* Basic text matching
* No vector database
* No embedding-based semantic search
* No advanced entity resolution
* Limited experience interpretation
* No OCR for scanned resumes
* No recruiter authentication
* No persistent database
* Matching logic is intentionally simple

---

# 🚀 Future Improvements

Possible future improvements:

* Semantic similarity using embeddings
* Vector database integration
* Better skill ontology
* Skill synonyms and aliases
* Experience timeline extraction
* Recruiter dashboard
* Candidate ranking
* Multiple candidate comparison
* Resume improvement suggestions
* Explainable match reasoning
* Persistent candidate database
* RAG-based job intelligence
* Advanced agentic recruitment workflow

---

# 🎯 Learning Objectives

This project was built to understand practical LLM application development concepts:

* Working with LLM APIs
* Prompt engineering
* Structured LLM output
* JSON processing
* Pydantic validation
* PDF text extraction
* Text normalization
* Requirement matching
* Weighted scoring
* Rule-based decision systems
* Streamlit application development

---

# 👨‍💻 Author

**Swarnabha Dutta**

Full Stack Developer | AI/LLM Application Development

---

# 📌 Project Status

**Completed — Mini Project**

The current version focuses on building a functional end-to-end resume and Job Description matching pipeline before moving toward more advanced AI/RAG features.
