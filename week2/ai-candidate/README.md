# 🤖 AI Candidate — Engineering Intelligence Profile

> **Not just the resume. Understand the engineer.**

AI Candidate is an interactive, AI-powered engineering profile that allows recruiters, interviewers, and hiring teams to explore a candidate's technical background through natural-language questions.

Instead of presenting a static resume, the application turns a candidate's projects, technical experience, engineering strengths, AI work, and growth areas into an interactive conversational experience.

The system uses a structured candidate knowledge profile, a custom system prompt, and a streaming LLM backend to generate evidence-grounded responses.

---

## 🌐 Live Demo

### Frontend
https://ai-candidate-xi.vercel.app/

### Backend API
https://ai-candidate-api.onrender.com

---

## 🎯 Why This Project?

Traditional developer portfolios are mostly static:

```text
Resume
   ↓
Projects
   ↓
Skills
   ↓
Contact
```

AI Candidate changes the interaction model:

```text
Recruiter
   ↓
Natural-language question
   ↓
AI Candidate Interface
   ↓
FastAPI Backend
   ↓
Candidate Profile + System Prompt
   ↓
LLM
   ↓
Streaming Response
   ↓
Evidence-oriented Answer
```

A recruiter can ask questions such as:

- What are his strongest engineering skills?
- What makes him different from a typical junior developer?
- Which project best demonstrates his engineering ability?
- What AI/LLM experience does he have?
- What measurable engineering impact has he delivered?
- What are his current technical growth areas?
- Explain his Bookify project.
- Explain his AI Code Reviewer project.
- What is his current technical focus?

---

# ✨ Core Features

## 🧠 AI Candidate Assistant

Recruiters can ask questions about the candidate using natural language.

The AI generates responses based on the candidate profile and predefined engineering evidence instead of behaving like a generic chatbot.

---

## 💬 Conversational Recruiter Interface

The interface is designed around recruiter-style interactions.

Features include:

- Natural-language questions
- AI-generated answers
- Streaming responses
- Loading / thinking state
- Markdown-rendered responses
- Quick recruiter actions
- Project-specific AI questions

---

## ⚡ Streaming AI Responses

The backend streams LLM output directly to the frontend.

Instead of waiting for the entire response:

```text
LLM
 ↓
Token / chunk
 ↓
FastAPI StreamingResponse
 ↓
Browser ReadableStream
 ↓
Incremental UI update
```

This creates a more responsive conversational experience.

---

## 🎤 Voice Input

The frontend supports browser-based speech recognition.

Recruiters can use the microphone button to dictate a question instead of typing it.

The implementation uses the browser's:

```text
SpeechRecognition
webkitSpeechRecognition
```

with:

```text
en-IN
```

language configuration.

---

## 🚀 Recruiter Quick Actions

The interface provides predefined recruiter-oriented questions such as:

- Quick Overview
- Why Hire Him?
- Strongest Skills
- AI / LLM
- Best Project
- Growth Areas

These actions allow a recruiter to understand the candidate without manually constructing questions.

---

## 📊 Recruiter Snapshot

The portfolio includes a dedicated recruiter-focused section that surfaces questions around:

- Engineering differentiation
- Measurable engineering impact
- Technical depth
- Project experience

The goal is to help recruiters reach the important information faster.

---

# 👨‍💻 Candidate Profile

The AI profile represents:

**Swarnabha Dutta**

### Role

Full-Stack Engineer

### Current Focus

- AI-first SaaS
- Backend Performance
- LLM Integration

### Engineering Areas

- React
- Next.js
- Node.js
- Python
- TypeScript
- MongoDB
- PostgreSQL
- Redis
- Docker
- Gemini
- Vapi
- Three.js

---

# 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      Recruiter       │
                    └──────────┬───────────┘
                               │
                               │ Question
                               ▼
                    ┌──────────────────────┐
                    │ React + Vite Frontend│
                    │                      │
                    │ - Chat UI            │
                    │ - Quick Actions      │
                    │ - Voice Input        │
                    │ - Markdown Rendering │
                    └──────────┬───────────┘
                               │
                               │ HTTPS POST /chat
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ - Request validation │
                    │ - CORS              │
                    │ - Candidate loading │
                    │ - Prompt building   │
                    │ - Streaming         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Candidate Profile│       │ System Prompt    │
       │ candidate.json   │       │ prompts.py       │
       └────────┬─────────┘       └────────┬─────────┘
                │                          │
                └────────────┬─────────────┘
                             ▼
                    ┌──────────────────────┐
                    │      Groq LLM        │
                    │  openai/gpt-oss-120b  │
                    └──────────┬───────────┘
                               │
                         Streaming Output
                               │
                               ▼
                    ┌──────────────────────┐
                    │ React AI Response UI │
                    └──────────────────────┘
```

---

# 🧩 Project Structure

The project lives inside the `RAG_LEARNING` repository:

```text
RAG_LEARNING/
│
├── week2/
│   │
│   └── ai-candidate/
│       │
│       ├── backend/
│       │   │
│       │   ├── data/
│       │   │   └── candidate.json
│       │   │
│       │   ├── src/
│       │   │
│       │   ├── candidate.py
│       │   ├── chat.py
│       │   ├── id.py
│       │   ├── llm.py
│       │   ├── main.py
│       │   ├── prompts.py
│       │   ├── schemas.py
│       │   │
│       │   ├── pyproject.toml
│       │   ├── uv.lock
│       │   ├── .env
│       │   └── .env.example
│       │
│       └── frontend/
│           │
│           ├── public/
│           │   └── resume.pdf
│           │
│           ├── src/
│           │   ├── App.jsx
│           │   ├── App.css
│           │   ├── index.css
│           │   └── main.jsx
│           │
│           ├── package.json
│           ├── package-lock.json
│           ├── vite.config.js
│           └── .env
│
└── README.md
```

---

# 🧠 Backend Architecture

The backend is intentionally lightweight and modular.

## Candidate Loading

`candidate.py` loads the structured candidate profile from:

```text
backend/data/candidate.json
```

The JSON data is validated using the project's candidate schema before being used by the application.

```text
candidate.json
      ↓
load_candidate()
      ↓
Candidate schema validation
      ↓
Candidate object
```

---

## Prompt Construction

The candidate profile is passed into:

```python
build_system_prompt(candidate)
```

This produces the system-level instruction used by the LLM.

```text
Candidate Profile
       ↓
System Prompt
       ↓
LLM
```

This helps the model answer questions specifically about the candidate instead of behaving like a general-purpose assistant.

---

# 🤖 LLM Integration

The backend uses the Groq Python SDK.

Current model:

```text
openai/gpt-oss-120b
```

The API key is loaded from:

```text
GROQ_API_KEY
```

The LLM is called with streaming enabled.

```python
client.chat.completions.create(
    model=model,
    messages=messages,
    stream=True
)
```

The backend exposes the generated chunks through FastAPI's:

```text
StreamingResponse
```

---

# 🌊 Streaming Request Flow

When a recruiter asks:

```text
What makes Swarnabha different from a typical junior developer?
```

the request flows through:

```text
React
  ↓
POST /chat
  ↓
FastAPI
  ↓
Validate question
  ↓
Candidate system prompt
  ↓
Groq LLM
  ↓
Streaming chunks
  ↓
FastAPI StreamingResponse
  ↓
ReadableStream
  ↓
React state updates
  ↓
Markdown-rendered answer
```

---

# 🌐 API

## `GET /`

Basic API status endpoint.

Example response:

```json
{
  "message": "AI Candidate API is running"
}
```

---

## `GET /health`

Health-check endpoint.

Example response:

```json
{
  "status": "ok"
}
```

---

## `POST /chat`

Main AI endpoint.

### Request

```json
{
  "question": "What are Swarnabha's strongest technical skills?"
}
```

### Response

The endpoint returns a streamed plain-text response.

---

# 🔐 Environment Variables

## Backend

Create:

```text
backend/.env
```

Example:

```env
GROQ_API_KEY=your_groq_api_key
FRONTEND_URLS=http://localhost:5173
```

For production, configure the production frontend origin as well:

```env
FRONTEND_URLS=http://localhost:5173,https://ai-candidate-xi.vercel.app
```

Never commit the real API key.

---

# 🎨 Frontend

The frontend is built with:

- React
- Vite
- JavaScript
- CSS
- React Markdown
- remark-gfm
- Browser Speech Recognition API

The main application state handles:

```text
Question
Answer
Loading
Theme
Voice listening
Resume menu
Copied email state
Active project
Contact UI
```

---

# 🖥️ Frontend Experience

## Hero Section

The landing section introduces the product as:

```text
AI-POWERED ENGINEERING PROFILE

Understand the
engineer.

Not just the resume.
```

The interface is positioned as an interactive engineering profile rather than a traditional portfolio.

---

## AI Interview Layer

The main interaction area is:

```text
AI INTERVIEW LAYER

Ask the Candidate Profile
```

The interface visually separates:

```text
RECRUITER
```

and

```text
AI Candidate
Evidence-based response
```

This makes the portfolio feel like a lightweight recruiter interview interface.

---

# 🎤 Voice Interaction

The frontend uses browser speech recognition:

```javascript
window.SpeechRecognition ||
window.webkitSpeechRecognition
```

Voice input is configured for:

```text
en-IN
```

The recognized transcript is inserted directly into the question input.

---

# 📝 Markdown Response Rendering

AI responses are rendered using:

```text
react-markdown
remark-gfm
```

This allows responses containing:

- Headings
- Lists
- Tables
- Bold text
- Structured Markdown

to be displayed as readable recruiter-facing content.

---

# 🧹 AI Response Cleaning

The frontend includes a response-cleaning layer that:

- Converts accidental `<br>` tags into newlines
- Removes unwanted HTML tags
- Prevents excessive blank lines
- Normalizes the final response before rendering

This keeps streamed LLM output visually consistent.

---

# 📁 Resume Integration

The frontend provides:

```text
Resume ↗
```

with two actions:

```text
View Resume
Download Resume
```

The resume is served from:

```text
/public/resume.pdf
```

---

# 📌 Projects Included

The candidate profile currently presents five major projects.

## 01 — AI Code Reviewer

**AI-Powered Code Analysis Platform**

Technologies:

```text
React
Node.js
Express
MongoDB
Redis
Gemini
Docker
TypeScript
```

Highlights:

- 93% API latency reduction
- 82.4% fewer redundant API/DB requests
- 137+ automated tests
- 84%+ line coverage
- 98 Lighthouse performance

---

## 02 — Bookify

**AI Voice Learning SaaS**

Technologies:

```text
Next.js
TypeScript
MongoDB
Clerk
Vapi
ElevenLabs
PostHog
```

Highlights:

- Semantic PDF search
- PDF chunking and indexing
- Real-time voice interaction
- Usage-based throttling
- Product analytics

---

## 03 — StockPilot

**Real-Time AI Stock Intelligence**

Technologies:

```text
Next.js
TypeScript
PostgreSQL
Prisma
Gemini
BetterAuth
TradingView
```

Highlights:

- Real-time TradingView charts
- Gemini-powered insights
- Persistent watchlists
- PostgreSQL persistence
- Secure session management

---

## 04 — HealthCheckBuddy

**Healthcare SaaS**

Technologies:

```text
Next.js
PostgreSQL
Prisma
Clerk
Vonage
```

Highlights:

- Doctor verification
- Appointment booking
- Atomic database transactions
- Real-time video consultations
- Role-based security

---

## 05 — Animated 3D Portfolio

**Interactive Developer Portfolio**

Technologies:

```text
React
Vite
Three.js
Tailwind CSS
```

Highlights:

- 99/100 Lighthouse performance
- 3D scenes and animations
- Responsive experience
- Performance-focused implementation

---

# 🧭 Recruiter-Oriented Questions

The system intentionally includes questions that map to real hiring decisions.

Examples:

### Technical Strength

```text
What are Swarnabha's strongest technical skills?
```

### Differentiation

```text
What makes Swarnabha different from a typical junior full-stack developer?
```

### Engineering Impact

```text
What measurable engineering impact has Swarnabha demonstrated?
```

### AI Experience

```text
Explain Swarnabha's AI, LLM and AI product integration experience.
```

### Project Deep Dive

```text
Explain Swarnabha's Bookify project to a recruiter.
```

### Growth

```text
What are Swarnabha's main technical gaps or areas he is currently improving?
```

---

# 🚀 Local Development

## 1. Clone the repository

```bash
git clone https://github.com/swarnabha-dutta/RAG_LEARNING.git
cd RAG_LEARNING/week2/ai-candidate
```

---

# Backend Setup

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure:

```env
GROQ_API_KEY=your_groq_api_key
FRONTEND_URLS=http://localhost:5173
```

Run FastAPI:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
.env
```

with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# ☁️ Production Deployment

The application uses a split deployment architecture.

```text
GitHub
  │
  ├── frontend
  │      ↓
  │    Vercel
  │      ↓
  │    Public UI
  │
  └── backend
         ↓
       Render
         ↓
       FastAPI API
         ↓
       Groq LLM
```

---

## Frontend — Vercel

Root directory:

```text
week2/ai-candidate/frontend
```

Environment variable:

```env
VITE_API_URL=https://ai-candidate-api.onrender.com
```

Build command:

```bash
npm run build
```

The frontend is deployed at:

```text
https://ai-candidate-xi.vercel.app/
```

---

## Backend — Render

Root directory:

```text
week2/ai-candidate/backend
```

Runtime:

```text
Python 3
```

Required environment variables:

```env
GROQ_API_KEY=your_groq_api_key
FRONTEND_URLS=https://ai-candidate-xi.vercel.app
```

The backend is deployed at:

```text
https://ai-candidate-api.onrender.com
```

---

# 🔒 CORS

The backend supports:

```text
localhost:5173
127.0.0.1:5173
```

and additional production origins configured through:

```env
FRONTEND_URLS
```

This allows the same backend code to support local development and the deployed Vercel frontend.

---

# 🧠 Design Philosophy

The project is built around one idea:

> **A developer portfolio should communicate engineering ability, not just list technologies.**

Instead of forcing recruiters to manually navigate:

```text
Resume
Projects
GitHub
Experience
Skills
```

the application provides an interactive layer where they can ask directly:

```text
"What should I know about this engineer?"
```

The AI then turns structured candidate information into a recruiter-oriented explanation.

---

# 💡 What Makes It Different?

Most developer portfolios follow:

```text
Static Portfolio
+
Project Cards
+
Resume
+
Contact Form
```

AI Candidate follows:

```text
Engineering Profile
+
Candidate Knowledge
+
LLM Reasoning
+
Recruiter Interaction
+
Streaming Responses
+
Evidence-Oriented Answers
```

The portfolio itself becomes an interface for understanding the candidate.

---

# 🛠️ Engineering Concepts Demonstrated

This project demonstrates practical experience with:

- React application architecture
- Vite-based frontend development
- FastAPI backend development
- REST API integration
- CORS configuration
- Pydantic validation
- Environment-based configuration
- LLM API integration
- Streaming LLM responses
- Browser streaming with `ReadableStream`
- Markdown rendering
- Browser speech recognition
- Responsive UI design
- Interactive state management
- Production deployment
- Vercel
- Render
- GitHub-based CI/CD workflow

---

# ⚠️ Current Scope

The current implementation is intentionally lightweight.

Candidate information is loaded from a structured local JSON knowledge source and transformed into a system prompt before being passed to the LLM.

The current version does **not** require:

- A vector database
- External document ingestion
- Embedding generation
- Semantic vector retrieval
- Multi-user authentication
- Persistent chat history

This keeps the architecture simple while demonstrating the core idea of an AI-powered candidate intelligence interface.

---

# 🔮 Future Improvements

Potential future iterations could introduce:

- Vector-based candidate retrieval
- GitHub repository ingestion
- Resume/document ingestion
- Semantic search
- Hybrid retrieval
- Reranking
- Evidence citations
- Conversation history
- Candidate knowledge graph
- Automated GitHub analysis
- Job-description-aware candidate analysis
- Recruiter-specific interview workflows
- Candidate/job matching
- Evaluation pipelines for answer faithfulness
- Rate limiting and abuse protection
- Observability and LLM cost tracking

These additions could evolve the current system into a more complete **Candidate Intelligence OS**.

---

# 📊 Current System Characteristics

| Area | Implementation |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI |
| LLM Provider | Groq |
| LLM Model | `openai/gpt-oss-120b` |
| Candidate Data | Structured JSON |
| Prompt Layer | Custom system prompt |
| Response | Streaming |
| Markdown | React Markdown + GFM |
| Voice Input | Browser Speech Recognition |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| Source Control | GitHub |
| API Protocol | HTTP/REST |
| CORS | FastAPI CORSMiddleware |

---

# 🎯 Key Takeaway

AI Candidate is not designed to replace a resume.

It is designed to make the resume **queryable**.

Instead of asking a recruiter to read everything and infer the candidate's strengths, the system allows them to directly interrogate the engineering profile.

```text
Traditional Portfolio

Recruiter
   ↓
Reads Resume
   ↓
Opens Projects
   ↓
Reads GitHub
   ↓
Forms an Opinion


AI Candidate

Recruiter
   ↓
Asks a Question
   ↓
AI analyzes candidate profile
   ↓
Evidence-oriented response
   ↓
Recruiter gets the signal faster
```

---

# 👨‍💻 Author

## Swarnabha Dutta

**Full-Stack Engineer**

Focused on:

```text
AI-first SaaS
Backend Performance
LLM Integration
Full-Stack Engineering
System Design
```

### Links

- GitHub: https://github.com/swarnabha-dutta
- LinkedIn: https://www.linkedin.com/in/swarnabha-dutta909/
- Portfolio: https://ai-candidate-xi.vercel.app/

---

## ⭐ Project Philosophy

> **Don't just show the resume. Let the engineer speak through the system.**
