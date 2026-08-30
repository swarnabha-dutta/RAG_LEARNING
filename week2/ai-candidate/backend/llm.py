import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")


if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!!")

client=Groq(api_key=my_api_key)

model="openai/gpt-oss-120b"


def ask_llm(messages: list[dict]):
    
    response=client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    full_response = ""

    for chunk in response:
        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)
            full_response += content
    print()
    return full_response


def stream_llm(messages: list[dict]):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in response:
        content = chunk.choices[0].delta.content

        if content:
            yield content