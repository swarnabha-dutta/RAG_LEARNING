import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer
import sys



model = SentenceTransformer("all-MiniLM-L6-v2") #384 features

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!")

client=Groq(api_key=my_api_key)

groq_model="openai/gpt-oss-120b"

documents=[
    "Employees receive 24 days of paid leave per year.",

    "Employees work from the office on Tuesday, wednesday and Thursday. ",
    
    "Monday and Friday are optional work-from-home days.",

    "Employees receive Rs 3000 per month for Gym reimbursements.",

    "Employees can claim Rs 2000 per month for home internet.",

    "Employees have a 90 day notice period."
]


document_embeddings = model.encode(documents)


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a)  * np.linalg.norm(b)
    )


def retrieve(embedding):
    scores = []

    for i, document in enumerate(document_embeddings):
        score = cosine_similarity(embedding,document)
        scores.append((score,documents[i]))

    scores.sort(reverse=True)
    return scores[0]




def  ask_llm(question, context):

    system_prompt=f"""answer in one line only. Answer only based on this context.do not hallucinate. Context: {context}"""

    system_message={
        "role": "system",
        "content": system_prompt
    }


    user_message={
        "role" : "user",
        "content": question
    }

    messages=[system_message, user_message]


    response = client.chat.completions.create(
        model=groq_model,
        messages=messages
    )

    answer=response.choices[0].message.content
    return answer




query = "What companies pay for my Health Compensation? "
q_embedding=model.encode(query)

score,context = retrieve(q_embedding)
answer=ask_llm(query,context)

print(score)
print(answer)