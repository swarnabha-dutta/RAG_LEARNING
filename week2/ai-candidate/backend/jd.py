from candidate import load_candidate
from prompts import build_system_prompt
from llm import ask_llm

candidate = load_candidate()

system_prompt = build_system_prompt(candidate)

def analyze_jd(jd: str):
    messages = [
        {
            "role":"system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""
Analyze the following Job Description against the candidate profile.


JOB DESCRIPTION:

{jd}

Evaluate:
 - Required skills
 - Preferred skills
 - Relevant experience
 - Education
 - Projects
 - Technologies 
 - Missing or unconfirmed requirements
 -Candidate strengths
 - Potential concerns
 

 Give a suitability score from 1 to 100.

Use this format:

Suitability Score: XX/100

Strong Matches:
- ...

Relevant Evidence:
- ...

Missing / Unconfirmed:
- ...

Potential Concerns:
- ...

Verdict:
Strong Fit / Moderate Fit / Weak Fit / Not a Good Fit

Reason:
...
"""
        }
    ]

    return ask_llm(messages)


if __name__ == "__main__":
    jd="""
We are looking for a Full Stack Developer.

Required:
- React.js
- Node.js
- Express.js
- MongoDB
- PostgreSQL
- TypeScript
- REST APIs
- Docker
- Git
- AWS
- Kubernetes
- 2+ years of professional experience

Preferred:
- Redis
- AI/LLM experience
"""

    print("\n AI JD Analysis:\n")
    analyze_jd(jd)