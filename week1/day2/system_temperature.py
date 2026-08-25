import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key :
    raise ValueError("API KEY WAS NOT FOUND!!!")

client=Groq(api_key=my_api_key)

model="openai/gpt-oss-safeguard-20b"

role="user"
prompt="Suggest me only one  name for my food company"

message_system={
    "role":"system",
    "content":"You are a brand manager who suggest the brand name for my food company,name should be in one word"
}

message={
    "role":role,
    "content":prompt
}

messages=[message_system,message]


response=client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=1.8
)



print(response.choices[0].message.content)

# models = client.models.list()

# for model in models.data:
#     print(model.id)