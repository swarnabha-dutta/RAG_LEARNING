from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from candidate import load_candidate
from prompts import build_system_prompt
from llm import stream_llm


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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