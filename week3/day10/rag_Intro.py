import os

from pathlib import Path
from dotenv import load_dotenv
from groq import Groq



load_dotenv()


my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY IS NOT FOUND!!!")

client=Groq(api_key=my_api_key)

model="openai/gpt-oss-120b"


knowledge_base={
    "age":"24+",
    "name":"Swarnabha Dutta",
    "location":"Kolkata, India",
    "education":"Bachelor of Technology in Electronics  And Communication Engineering",
    "experience":"2 years of experience in software development",
    "skills":"Python, JavaScript, React, Node.js, MongoDB",
    "projects":"10+ projects completed",
    "achievements":"10+ achievements",
    
}


def retrieve_Augmented_Data(question):
    question=question.lower()
    if "age" in question:
        return knowledge_base["age"]
    elif "name" in question:
        return knowledge_base["name"]
    elif "location" in question:
        return knowledge_base["location"]
    elif "education" in question:
        return knowledge_base["education"]
    elif "experience" in question:
        return knowledge_base["experience"]
    elif "skills" in question:
        return knowledge_base["skills"]
    elif "projects" in question:
        return knowledge_base["projects"]
    elif "achievements" in question:
        return knowledge_base["achievements"]
    else:
        return "I don't know the answer to that question"


def ask_llm(prompt):
    context = retrieve_Augmented_Data(prompt)
    system_prompt=f"""tell the answer in one line.Do not hallucinate.
    Strictly obey that only give the answer related to the context.
    Pick only from that following context:{context}"""

    system_message={
        "role":"system",
        "content":system_prompt
    }


    user_message={
        "role":"user",
        "content":prompt
    }

    messages=[system_message,user_message]

    response= client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.9
    )

    answer = response.choices[0].message.content

    return answer


print(ask_llm("What is  Swarnabha Dutta's age?"))













# models = client.models.list()

# for model in models.data:
#     print(model.id)