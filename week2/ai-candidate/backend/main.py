from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


from candidate import load_candidate
from prompts import build_system_prompt
from llm import stream_llm


app = FastAPI()

candidate = load_candidate()
system_prompt = build_system_prompt(candidate)


class ChatRequest(BaseModel):
    question: str



messages=[
    {
        "role":"system",
        "content": system_prompt
    },
]


@app.get("/")
def home():
    return {
        "message": "AI Candidate API is running"
    }



@app.post("/chat")
def chat(request: ChatRequest):

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": request.question
        }
    ]

    print("DEBUG MESSAGES:", messages)

    return StreamingResponse(
        stream_llm(messages),
        media_type="text/plain"
    )