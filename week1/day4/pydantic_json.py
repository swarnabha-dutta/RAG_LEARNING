import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API_KEY WAS NOT FOUND!!!")

model="openai/gpt-oss-120b"

client=Groq(api_key=my_api_key)

# Define the users perspective --> role and prompt
role="user"

# create a variable that add on prompts

text="Hello My name is Pratyush. Yesterday I broke up with my girlfriend sheetal I have an iphone which is not working at all. My address is delhi. My email is abc@gmail.com. My contact number is 82134"


prompt=f"""
This is a Customer Ticket.Please Extract the information from this.
{text}
"""


users_message={
    "role":role,
    "content":prompt
}


# Define System Instructions --> role="system" and "content"=

from pydantic import BaseModel

class Ticket(BaseModel):
    name:str
    email:str
    issues:str


schema=Ticket.model_json_schema()

response_format={
    "type":"json_object"
}

system_prompt=f"""
Extract the personal information strictly based on the schema and give the output in json format.
{schema}
"""

system_messages={
    "role":"system",
    "content":system_prompt
}

messages=[system_messages,users_message]


response=client.chat.completions.create(
    model=model,
    messages=messages,
    response_format=response_format
)



raw_answer=response.choices[0].message.content

# print(raw_answer)


# Read the Raw JSon answer

import json


raw_json_Data=raw_answer
compiled_Field_datas=json.loads(raw_json_Data)
extract_Datas=Ticket(**compiled_Field_datas)

print(extract_Datas)

print("######################")

# name
print(extract_Datas.name)

# email
print(extract_Datas.email)

# Issues
print(extract_Datas.issues)


