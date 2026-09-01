import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from candidate import load_candidate
from prompts import build_system_prompt
from llm import stream_llm


app = FastAPI()


# --------------------------------------------------
# CORS
# --------------------------------------------------

configured_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_URLS", "").split(",")
    if origin.strip()
]

allow_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-candidate-xi.vercel.app",
    *configured_origins,
]

# Remove duplicates while preserving order
allow_origins = list(dict.fromkeys(allow_origins))


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Candidate data
# --------------------------------------------------

candidate = load_candidate()

system_prompt = build_system_prompt(candidate)


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class ChatRequest(BaseModel):
    question: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Candidate API is running"
    }


# --------------------------------------------------
# Chat endpoint
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": request.question,
        },
    ]

    print("DEBUG MESSAGES:", messages)

    return StreamingResponse(
        stream_llm(messages),
        media_type="text/plain",
    )