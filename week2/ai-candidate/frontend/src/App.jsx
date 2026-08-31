import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

/* =========================================================
   CONTACT
   ========================================================= */

const CONTACT = {
  email: "swarnabhadutta909@gmail.com",
  phone: "+919883402671",
  github: "https://github.com/swarnabha-dutta",
  linkedin: "https://www.linkedin.com/in/swarnabhadutta909/",
};

/* =========================================================
   PROJECT DATA
   ========================================================= */

const PROJECTS = [
  {
    number: "01",
    name: "AI Code Reviewer",
    type: "AI-Powered Code Analysis Platform",
    description:
      "Full-stack platform that analyzes source code for bugs, security issues, anti-patterns and performance opportunities.",
    technologies: [
      "React",
      "Node.js",
      "Express",
      "MongoDB",
      "Redis",
      "Gemini",
      "Docker",
      "TypeScript",
    ],
    highlights: [
      "93% API latency reduction",
      "82.4% fewer redundant API/DB requests",
      "137+ automated tests",
      "84%+ line coverage",
      "98 Lighthouse performance",
    ],
    github: "https://github.com/swarnabha-dutta/AI_Code_Reviewer",
    live: "https://ai-code-reviewer-frontend-feb.onrender.com",
    featured: true,
    aiQuestion:
      "Give me a recruiter-focused explanation of the AI Code Reviewer project, including what was built, the technologies used, engineering challenges, and measurable results.",
  },

  {
    number: "02",
    name: "Bookify",
    type: "AI Voice Learning SaaS",
    description:
      "Transforms static PDFs into interactive voice-based learning experiences using semantic search and voice AI.",
    technologies: [
      "Next.js",
      "TypeScript",
      "MongoDB",
      "Clerk",
      "Vapi",
      "ElevenLabs",
      "PostHog",
    ],
    highlights: [
      "Semantic PDF search",
      "PDF chunking & indexing",
      "Real-time voice interaction",
      "Usage-based throttling",
      "Product analytics",
    ],
    github: "https://github.com/swarnabha-dutta/bookify",
    live: null,
    featured: false,
    aiQuestion:
      "Explain Swarnabha's Bookify project to a recruiter, including its purpose, architecture, technologies and AI-related work.",
  },

  {
    number: "03",
    name: "StockPilot",
    type: "Real-Time AI Stock Intelligence",
    description:
      "Stock intelligence dashboard combining TradingView charts with Gemini-powered contextual AI insights.",
    technologies: [
      "Next.js",
      "TypeScript",
      "PostgreSQL",
      "Prisma",
      "Gemini",
      "BetterAuth",
      "TradingView",
    ],
    highlights: [
      "Real-time TradingView charts",
      "Gemini-powered insights",
      "Persistent watchlists",
      "PostgreSQL persistence",
      "Secure session management",
    ],
    github: "https://github.com/swarnabha-dutta/stock_pilot",
    live: "https://stock-pilot-tau.vercel.app",
    featured: false,
    aiQuestion:
      "Explain Swarnabha's StockPilot project and specifically highlight its AI integration, database architecture and real-time features.",
  },

  {
    number: "04",
    name: "HealthCheckBuddy",
    type: "Healthcare SaaS",
    description:
      "Full-stack healthcare platform supporting patients, doctors and admins through secure role-based workflows.",
    technologies: [
      "Next.js",
      "PostgreSQL",
      "Prisma",
      "Clerk",
      "Vonage",
    ],
    highlights: [
      "Doctor verification",
      "Appointment booking",
      "Atomic DB transactions",
      "Real-time video consultations",
      "Role-based security",
    ],
    github: "https://github.com/swarnabha-dutta/Health_Check_Buddy",
    live: "https://health-check-buddy.vercel.app",
    featured: false,
    aiQuestion:
      "Explain the HealthCheckBuddy project to a recruiter, focusing on architecture, security, database transactions and real-time communication.",
  },

  {
    number: "05",
    name: "Animated 3D Portfolio",
    type: "Interactive Developer Portfolio",
    description:
      "Three.js-powered developer portfolio focused on immersive visual experience, responsiveness and frontend performance.",
    technologies: [
      "React",
      "Vite",
      "Three.js",
      "Tailwind CSS",
    ],
    highlights: [
      "99/100 Lighthouse performance",
      "3D scenes & animations",
      "Responsive experience",
      "Performance-focused implementation",
    ],
    github:
      "https://github.com/swarnabha-dutta/Animated_3D_portfolio",
    live: "https://animated-3-d-portfolio.vercel.app",
    featured: false,
    aiQuestion:
      "Explain Swarnabha's Animated 3D Portfolio project and what it demonstrates about his frontend engineering skills.",
  },
];

/* =========================================================
   QUICK QUESTIONS
   ========================================================= */

const QUICK_ACTIONS = [
  {
    label: "Quick Overview",
    question:
      "Give me a concise recruiter-focused overview of Swarnabha's engineering profile.",
  },
  {
    label: "Why Hire Him?",
    question:
      "Why should a recruiter consider Swarnabha for a Full-Stack or Backend Engineer role? Use only documented evidence.",
  },
  {
    label: "Strongest Skills",
    question:
      "What are Swarnabha's strongest technical skills? Give concise evidence for each.",
  },
  {
    label: "AI / LLM",
    question:
      "Explain Swarnabha's AI, LLM and AI product integration experience. Clearly distinguish experience from learning.",
  },
  {
    label: "Best Project",
    question:
      "Which project best demonstrates Swarnabha's engineering ability? Explain using documented evidence and avoid inventing personal preferences.",
  },
  {
    label: "Growth Areas",
    question:
      "What are Swarnabha's main technical gaps or areas he is currently improving?",
  },
];

/* =========================================================
   AI RESPONSE CLEANER
   ========================================================= */

function cleanAIResponse(text) {
  if (!text) return "";

  return text
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]*>/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/* =========================================================
   APP
   ========================================================= */

function App() {
  const [darkMode, setDarkMode] = useState(true);

  const [question, setQuestion] = useState(
    "Tell me something about him that is not in his resume."
  );

  const [answer, setAnswer] = useState(
    "Ask the candidate anything about his projects, technical experience, AI work or engineering profile."
  );

  const [loading, setLoading] = useState(false);

  const [showResumeMenu, setShowResumeMenu] = useState(false);

  const [listening, setListening] = useState(false);

  const [copied, setCopied] = useState(false);

  const [activeProject, setActiveProject] = useState(null);

  const [showContact, setShowContact] = useState(false);

  const resumeRef = useRef(null);

  /* =========================================================
     THEME
     ========================================================= */

  useEffect(() => {
    document.body.className = darkMode ? "dark-body" : "light-body";
  }, [darkMode]);

  /* =========================================================
     CLOSE RESUME MENU
     ========================================================= */

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        resumeRef.current &&
        !resumeRef.current.contains(event.target)
      ) {
        setShowResumeMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  /* =========================================================
     ASK FASTAPI STREAMING ENDPOINT
     ========================================================= */

  const askQuestion = async (customQuestion = null) => {
    const finalQuestion =
      customQuestion ?? question.trim();

    if (!finalQuestion || loading) return;

    setQuestion(finalQuestion);
    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: finalQuestion,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      if (!response.body) {
        throw new Error("Streaming response not supported.");
      }

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder();

      let fullText = "";

      while (true) {
        const { value, done } =
          await reader.read();

        if (done) break;

        const chunk =
          decoder.decode(value, {
            stream: true,
          });

        fullText += chunk;

        setAnswer(fullText);
      }
    } catch (error) {
      console.error(error);

      setAnswer(
        "Unable to connect to the AI Candidate backend. Make sure FastAPI is running on http://127.0.0.1:8000."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     ENTER KEY
     ========================================================= */

  const handleQuestionKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      askQuestion();
    }
  };

  /* =========================================================
     VOICE INPUT
     ========================================================= */

  const startVoiceInput = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        "Voice input is not supported in this browser. Please use Chrome or Edge."
      );

      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.interimResults = true;

    recognition.continuous = false;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onresult = (event) => {
      let transcript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        transcript +=
          event.results[i][0].transcript;
      }

      setQuestion(transcript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  };

  /* =========================================================
     COPY EMAIL
     ========================================================= */

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(
        CONTACT.email
      );

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1800);
    } catch (error) {
      console.error(error);
    }
  };

  /* =========================================================
     PROJECT ASK
     ========================================================= */

  const askProject = (project) => {
    setActiveProject(project);

    askQuestion(project.aiQuestion);
  };

  /* =========================================================
     RENDER
     ========================================================= */

  return (
    <div
      className={
        darkMode
          ? "app dark"
          : "app light"
      }
    >
      {/* =====================================================
          UNIVERSE BACKGROUND
          ===================================================== */}

      <div className="universe">
        <div className="stars stars-one" />
        <div className="stars stars-two" />

        <div className="nebula nebula-one" />
        <div className="nebula nebula-two" />

        <div className="orb orb-one" />
        <div className="orb orb-two" />
      </div>

      {/* =====================================================
          NAVBAR
          ===================================================== */}

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            S
          </div>

          <div className="brand-copy">
            <strong>SWARNABHA</strong>
            <span>AI CANDIDATE</span>
          </div>
        </div>

        <div className="top-actions">
          {/* EMAIL */}

          <a
            href={`mailto:${CONTACT.email}`}
            className="header-icon"
            title="Email Swarnabha"
          >
            ✉
          </a>

          {/* PHONE */}

          <a
            href={`tel:${CONTACT.phone}`}
            className="header-icon"
            title="Call Swarnabha"
          >
            ☎
          </a>

          {/* THEME */}

          <button
            className="theme-button"
            onClick={() =>
              setDarkMode(
                (previous) => !previous
              )
            }
            title="Toggle theme"
          >
            {darkMode ? "☀" : "☾"}
          </button>

          {/* RESUME */}

          <div
            className="resume-wrapper"
            ref={resumeRef}
          >
            <button
              className="resume-button"
              onClick={() =>
                setShowResumeMenu(
                  (previous) => !previous
                )
              }
            >
              Resume ↗
            </button>

            {showResumeMenu && (
              <div className="resume-menu">
                <a
                  href="/resume.pdf"
                  target="_blank"
                  rel="noreferrer"
                >
                  <span>↗</span>

                  <div>
                    <strong>
                      View Resume
                    </strong>

                    <small>
                      Open PDF
                    </small>
                  </div>
                </a>

                <a
                  href="/resume.pdf"
                  download="Swarnabha_Dutta_Resume.pdf"
                >
                  <span>↓</span>

                  <div>
                    <strong>
                      Download Resume
                    </strong>

                    <small>
                      Save PDF
                    </small>
                  </div>
                </a>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* =====================================================
          MAIN
          ===================================================== */}

      <main className="page">
        {/* ===================================================
            HERO
            =================================================== */}

        <section className="hero">
          <div className="eyebrow">
            <span className="status-dot" />
            AI-POWERED ENGINEERING PROFILE
          </div>

          <h1>
            Understand the
            <br />

            <span>engineer.</span>
          </h1>

          <p className="hero-description">
            Not just the resume.
          </p>

          <p className="hero-subtitle">
            Explore Swarnabha's projects,
            technical experience, AI work and
            engineering profile through an
            interactive evidence-based
            assistant.
          </p>

          {/* QUICK ACTIONS */}

          <div className="quick-actions">
            {QUICK_ACTIONS.map(
              (action) => (
                <button
                  key={action.label}
                  onClick={() =>
                    askQuestion(
                      action.question
                    )
                  }
                  disabled={loading}
                >
                  {action.label}
                </button>
              )
            )}
          </div>
        </section>

        {/* ===================================================
            AI INTERVIEW + PROFILE
            =================================================== */}

        <section className="profile-grid">
          {/* AI PANEL */}

          <div className="ai-panel">
            <div className="panel-header">
              <div>
                <span className="panel-label">
                  AI INTERVIEW LAYER
                </span>

                <h2>
                  Ask the Candidate
                  Profile
                </h2>
              </div>

              <div className="live-status">
                <span />
                Live
              </div>
            </div>

            <div className="conversation">
              <div className="user-message">
                <span>
                  RECRUITER
                </span>

                <div className="user-bubble">
                  {question}
                </div>
              </div>

              <div className="ai-message">
                <div className="ai-avatar">
                  S
                </div>

                <div className="ai-content">
                  <div className="ai-name-row">
                    <strong>
                      AI Candidate
                    </strong>

                    <span>
                      Evidence-based response
                    </span>
                  </div>

                  <div className="answer">
                    {loading && (
                      <div className="thinking">
                        <span />
                        <span />
                        <span />
                        <small>
                          Thinking...
                        </small>
                      </div>
                    )}

                    {!loading && !answer && (
                      <span className="muted">
                        Waiting for response...
                      </span>
                    )}

                    {answer && (
                      <div className="answer-text">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {cleanAIResponse(answer)}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* INPUT */}

            <div className="chat-composer">
              <button
                type="button"
                className={`voice-button ${listening
                  ? "listening"
                  : ""
                  }`}
                onClick={
                  startVoiceInput
                }
                title="Ask using voice"
              >
                {listening
                  ? "●"
                  : "🎙"}
              </button>

              <input
                type="text"
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleQuestionKeyDown
                }
                placeholder="Ask something about Swarnabha..."
              />

              <button
                className="ask-button"
                onClick={() =>
                  askQuestion()
                }
                disabled={
                  loading ||
                  !question.trim()
                }
              >
                {loading
                  ? "Thinking..."
                  : "Ask ↗"}
              </button>
            </div>

            <div className="composer-hint">
              <span>
                Enter ↵
              </span>

              <span>
                or use voice 🎙
              </span>
            </div>
          </div>

          {/* PROFILE SIDEBAR */}

          <aside className="sidebar">
            {/* PROFILE CARD */}

            <div className="profile-card">
              <div className="profile-top">
                <div className="profile-avatar">
                  SD
                </div>

                <div>
                  <strong>
                    Swarnabha Dutta
                  </strong>

                  <span>
                    Full-Stack Engineer
                  </span>
                </div>
              </div>

              <div className="focus-box">
                <span>
                  CURRENT FOCUS
                </span>

                <strong>
                  AI-first SaaS · Backend
                  Performance · LLM
                  Integration
                </strong>
              </div>

              <div className="stats">
                <div>
                  <strong>5</strong>
                  <span>Projects</span>
                </div>

                <div>
                  <strong>3</strong>
                  <span>AI Integrations</span>
                </div>

                <div>
                  <strong>284+</strong>
                  <span>DSA</span>
                </div>
              </div>
            </div>

            {/* ENGINEERING STACK */}

            <div className="stack-card">
              <span className="card-label">
                ENGINEERING STACK
              </span>

              <div className="stack-list">
                {[
                  "React",
                  "Next.js",
                  "Node.js",
                  "Python",
                  "TypeScript",
                  "MongoDB",
                  "PostgreSQL",
                  "Redis",
                  "Docker",
                  "Gemini",
                  "Vapi",
                  "Three.js",
                ].map(
                  (technology) => (
                    <span
                      key={technology}
                    >
                      {technology}
                    </span>
                  )
                )}
              </div>
            </div>

            {/* CONTACT */}

            <div className="contact-card">
              <div className="card-label">
                DIRECT CONTACT
              </div>

              <h3>
                Prefer a direct
                conversation?
              </h3>

              <p>
                Reach out directly or
                explore the profile
                first.
              </p>

              <div className="contact-grid">
                <a
                  href={`mailto:${CONTACT.email}`}
                >
                  ✉ Email
                </a>

                <a
                  href={`tel:${CONTACT.phone}`}
                >
                  ☎ Call
                </a>
              </div>

              <button
                className="copy-email"
                onClick={copyEmail}
              >
                {copied
                  ? "✓ Email copied"
                  : "Copy email address"}
              </button>

              <div className="social-links">
                <a
                  href={
                    CONTACT.github
                  }
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub ↗
                </a>

                <a
                  href={
                    CONTACT.linkedin
                  }
                  target="_blank"
                  rel="noreferrer"
                >
                  LinkedIn ↗
                </a>
              </div>
            </div>
          </aside>
        </section>

        {/* ===================================================
            RECRUITER SNAPSHOT
            =================================================== */}

        <section className="snapshot-section">
          <div className="section-heading">
            <div>
              <span className="section-label">
                RECRUITER SNAPSHOT
              </span>

              <h2>
                Get to the signal
                faster.
              </h2>
            </div>

            <p>
              Common questions,
              answered instantly by
              the candidate profile.
            </p>
          </div>

          <div className="snapshot-grid">
            <button
              onClick={() =>
                askQuestion(
                  "What makes Swarnabha different from a typical junior full-stack developer?"
                )
              }
            >
              <span>01</span>

              <strong>
                What makes him
                different?
              </strong>

              <small>
                Explore engineering
                depth
              </small>

              <b>↗</b>
            </button>

            <button
              onClick={() =>
                askQuestion(
                  "What measurable engineering impact has Swarnabha demonstrated in his projects?"
                )
              }
            >
              <span>02</span>

              <strong>
                What impact has
                he delivered?
              </strong>

              <small>
                Metrics & outcomes
              </small>

              <b>↗</b>
            </button>

            <button
              onClick={() =>
                askQuestion(
                  "Summarize Swarnabha's backend engineering capabilities."
                )
              }
            >
              <span>03</span>

              <strong>
                Backend capability
              </strong>

              <small>
                APIs, databases,
                caching
              </small>

              <b>↗</b>
            </button>

            <button
              onClick={() =>
                askQuestion(
                  "Summarize Swarnabha's current AI learning and experience while clearly distinguishing them."
                )
              }
            >
              <span>04</span>

              <strong>
                AI maturity
              </strong>

              <small>
                Experience vs learning
              </small>

              <b>↗</b>
            </button>
          </div>
        </section>

        {/* ===================================================
            PROJECTS
            =================================================== */}

        <section className="projects-section">
          <div className="section-heading">
            <div>
              <span className="section-label">
                ENGINEERING WORK
              </span>

              <h2>
                Featured Projects
              </h2>
            </div>

            <p>
              Built, shipped and
              documented.
            </p>
          </div>

          <div className="projects-grid">
            {PROJECTS.map(
              (project) => (
                <article
                  key={project.name}
                  className={`project-card ${project.featured
                    ? "featured"
                    : ""
                    } ${activeProject?.name ===
                      project.name
                      ? "active"
                      : ""
                    }`}
                >
                  <div className="project-top">
                    <span className="project-number">
                      {project.number}
                    </span>

                    {project.featured && (
                      <span className="featured-badge">
                        FEATURED PROJECT
                      </span>
                    )}

                    {!project.featured && (
                      <span className="project-type">
                        {project.type}
                      </span>
                    )}
                  </div>

                  <h3>
                    {project.name}
                  </h3>

                  <p className="project-description">
                    {project.description}
                  </p>

                  {/* TECH STACK */}

                  <div className="technology-list">
                    {project.technologies.map(
                      (technology) => (
                        <span
                          key={technology}
                        >
                          {technology}
                        </span>
                      )
                    )}
                  </div>

                  <div className="project-divider" />

                  {/* KEY WORK */}

                  <div className="key-work">
                    <span>
                      KEY WORK
                    </span>

                    <ul>
                      {project.highlights.map(
                        (highlight) => (
                          <li
                            key={
                              highlight
                            }
                          >
                            {highlight}
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  {/* PROJECT ACTIONS */}

                  <div className="project-actions">
                    <a
                      href={
                        project.github
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      GitHub ↗
                    </a>

                    {project.live ? (
                      <a
                        href={
                          project.live
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        Live Project ↗
                      </a>
                    ) : (
                      <a
                        href={
                          project.github
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        Explore ↗
                      </a>
                    )}

                    <button
                      onClick={() =>
                        askProject(
                          project
                        )
                      }
                      disabled={loading}
                    >
                      Ask AI →
                    </button>
                  </div>
                </article>
              )
            )}
          </div>
        </section>

        {/* ===================================================
            RESUME / CONTACT CTA
            =================================================== */}

        <section className="final-cta">
          <div>
            <span className="section-label">
              INTERESTED IN THE ENGINEER?
            </span>

            <h2>
              Start with the
              evidence.
            </h2>

            <p>
              Explore the work, ask the
              AI profile questions, or
              go directly to the resume.
            </p>
          </div>

          <div className="cta-actions">
            <button
              onClick={() =>
                setShowContact(
                  (previous) => !previous
                )
              }
            >
              Contact ↗
            </button>

            <a
              href="/resume.pdf"
              target="_blank"
              rel="noreferrer"
            >
              View Resume ↗
            </a>

            <a
              href="/resume.pdf"
              download="Swarnabha_Dutta_Resume.pdf"
            >
              Download PDF ↓
            </a>
          </div>

          {showContact && (
            <div className="cta-contact">
              <a
                href={`mailto:${CONTACT.email}`}
              >
                {CONTACT.email}
              </a>

              <a
                href={`tel:${CONTACT.phone}`}
              >
                {CONTACT.phone}
              </a>
            </div>
          )}
        </section>
      </main>

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="footer">
        <span>
          AI CANDIDATE · SWARNABHA DUTTA
        </span>

        <span>
          Evidence over exaggeration.
        </span>
      </footer>
    </div>
  );
}

export default App;