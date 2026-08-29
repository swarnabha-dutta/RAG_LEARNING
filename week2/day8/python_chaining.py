import os

from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep


load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!!!")


client=Groq(api_key=my_api_key)
model= "openai/gpt-oss-20b"


JD="""
We are hiring a Backend Python Developer.

Requirements:
- Strong Python
- FastAPI or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

RESUME="""
Name: Rahul Sharma

Experience:
3 years as a Software Developer.

Skills:
Python, FastAPI, MySQL, Docker,
REST APIs, Git

Projects:
Built a food delivery backend using
FastAPI and MySQL.

Deployed applications using Docker.
"""
# purpose:for llm call
def ask_llm(system_prompt,user_prompt):
    sys_message={
        "role":"system",
        "content":system_prompt
    }
    user_message={
        "role":"user",
        "content":user_prompt
    }
    messages=[sys_message,user_message]
    response= client.chat.completions.create(
        model=model,
        messages=messages
    )
    answer=response.choices[0].message.content
    return answer



# step1: Resume Extraction
def resume_extract(RESUME):
    print("STEP 1: ")
    system_prompt="""
    You are a professional and expert HR assistant. Extract the skills from the candidates resume provided.
    Only return the skills no other information. Do not invent any skills by yourself.
    """
    user_prompt=f"""
    Extract the skills from this resume
    {RESUME}
    """
    return ask_llm(system_prompt,user_prompt)

# Step 2 : Extract the JD
def JD_extract(JD):
    print("STEP 2:")
    
    system_prompt="""
    You are a professional and expert JD extractor assistant. Extract the skills from the JD(Job Description) provided.
    Only return the skills no other information. Do not invent any skills by yourself.
    
    Output Format:
    Skills should be separated by commas. Just return comma separated skills do not return any other filler information.
    """
    user_prompt=f"""
    Extract the skills from this JD
    {JD}
    """
    return ask_llm(system_prompt,user_prompt)

# Step3: Match the JD skills vs candidate's RESUME skills

def match(candidate,jd):
    print("STEP 3:")
    system_prompt="""
    You are a professional and Expert HR assistant.Compare the skills of candidate and the skills required in the JD and produce a final score between 1 and 100.
    And also produce a short verdict whether the candidate is a good fit for the role.
    """

    user_prompt=f"""
    Compare and Match the skills 
    JD:{jd}
    candidate:
    {candidate}
    """
    return ask_llm(system_prompt,user_prompt)




candidate=resume_extract(RESUME)
print("Candidate:-> ",candidate)
sleep(2)
jd=JD_extract(JD)
print("JD:",jd)
sleep(2)
score=match(candidate,jd)

print("score:-->\n",score)
# import requests
# import os
# from dotenv import load_dotenv


# load_dotenv()


# api_key = os.getenv("GROQ_API_KEY")
# url = "https://api.groq.com/openai/v1/models"

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# response = requests.get(url, headers=headers)



# models=response.json()["data"]

# for model in models:
    # print(model["id"])