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
#     print(model.id)import os
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

prompt1="Hi"
prompt2="Explain time travel in Detail under 100 words "
prompt3="Write n essay of 1000 words on Machine Learning"

prompts=[prompt1,prompt2,prompt3]

for prompt in prompts:
    message={
        "role":role,
        "content":prompt
    }
    messages=[message]
    
    response=client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1.8,
        max_tokens=500
    )
    usage=response.usage
    print(f"Prompt: {prompt} --> your tokens: {usage.prompt_tokens} completion_tokens: {usage.completion_tokens} total tokens:{usage.total_tokens} Finish Reason:{response.choices[0].finish_reason}")



# message_system={
#     "role":"system",
#     "content":"You are a brand manager who suggest the brand name for my food company,name should be in one word"
# }


# messages=[message_system,message]


# response=client.chat.completions.create(
#     model=model,
#     messages=messages,
#     temperature=1.8
# )



# print(response.choices[0].message.content)

# models = client.models.list()

# for model in models.data:
#     print(model.id)