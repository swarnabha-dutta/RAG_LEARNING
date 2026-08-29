import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"


prompt="Explain Black Hole"

message={
    "role":"user",
    "content":prompt
}

messages=[message]

# No Streaming --> Get the direct answer after some time 
# response1=client.chat.completions.create(
#     model=model,
#     messages=messages
# )
# answer1 = response1.choices[0].message.content
# print("answer1:",answer1)


# Streaming --> give the response chunk wise

response2 =client.chat.completions.create(
    model=model,
    messages=messages,
    stream=True
)

for chunk in response2:
    content=chunk.choices[0].delta.content
    if content:
        print(content, end="",flush=True)