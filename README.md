# Autonomous Life Admin & Opportunity Discovery Agent

A multi-agent personal assistant that manages tasks, bills, subscriptions,
and appointments, sends timely reminders, discovers career/educational
opportunities matched to your profile, and provides an AI chatbot with
long-term memory of your preferences.

## Architecture

```
User adds tasks/bills/appointments
        |
        v
Life Admin Module (unified LifeItem model)
        |
        v
Reminder Engine (rule-based, runs every 6h) ---> Notifications (web/email/push)
        |
        v
Opportunity Discovery Agent (Sentence Transformers + cosine similarity)
        |
        v
AI Assistant (Claude chat + daily schedule + opportunity summaries)
        |
        v
ChromaDB Memory (recalls past preferences across sessions)
        |
        v
Analytics Dashboard (deterministic aggregation + Claude tip)
```

**Why some modules aren't Claude calls:** Reminder timing and recurrence
math are deterministic date logic -- an LLM call would add latency and
cost with no benefit. Opportunity ranking uses embeddings + cosine
similarity (cheaper and more consistent than an LLM call for semantic
similarity at scale). Claude is used specifically where generation or
judgment is required: chat replies, daily schedule suggestions,
opportunity summaries, and productivity tips.

**Why ChromaDB over Pinecone:** ChromaDB runs embedded/local via
`PersistentClient` -- no separate server or cloud account needed, which
matters for a student project. Swapping to Pinecone later would only
require changing `app/memory/chroma_memory.py`.

## Tech stack

- **Backend**: FastAPI, SQLAlchemy, SQLite (swappable to PostgreSQL), JWT auth
- **Frontend**: React + Vite, React Router, Recharts, Axios
- **AI**: Claude API (chat, scheduling, summaries, tips)
- **Matching**: Sentence Transformers (opportunity relevance ranking)
- **Memory**: ChromaDB (embedded vector store for long-term user preferences)
- **Scheduling**: APScheduler (periodic reminder checks)

## Quick start (Docker -- recommended)

1. ```bash
   cp backend/.env.example backend/.env
   ```
   Leave every mode flag (`ANTHROPIC_API_KEY`, `OPPORTUNITY_SOURCE_MODE`,
   `SMTP_MODE`, `FIREBASE_MODE`, `GOOGLE_CALENDAR_MODE`) as `mock` to run
   everything without any real external credentials.

2. ```bash
   docker compose up --build
   ```

3. Seed the database (new terminal, once containers are up):
   ```bash
   docker compose exec backend python -m app.db.seed
   ```

4. Open:
   - Frontend: http://localhost:5173
   - Backend API docs: http://localhost:8000/docs

## Manual setup in VS Code (no Docker)

Use **Python 3.11 or 3.12** (avoids slow from-source builds of ML
packages on newer Python versions) and **Node.js 20 LTS**.

If `python --version` opens the Microsoft Store: Settings -> Apps ->
Advanced app settings -> App execution aliases -> turn OFF `python.exe`
and `python3.exe`.

If `npm` gives a PowerShell execution policy error:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Backend
```powershell
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.db.seed
uvicorn app.main:app --reload
```

### Frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```

## Demo account

| Email | Password |
|---|---|
| user@example.com | user1234 |

The seed script also creates 6 sample life items (a bill, a
subscription, an appointment, two tasks, and a document-expiry tracker)
and ~9 opportunities pulled through the mocked source adapters (jobs,
scholarships, government schemes, courses, hackathons).

## Suggested demo flow

1. Log in as the demo user.
2. **Dashboard**: see upcoming items and an AI-generated daily plan.
3. **Life Admin**: add a new bill or task, mark something complete --
   if it's recurring, watch the next occurrence get created
   automatically.
4. **Opportunities**: see jobs/scholarships/courses ranked by relevance
   to your profile (set in **Profile** first for personalized results).
5. **AI Assistant**: ask something like "what should I focus on today?"
   -- the reply factors in your actual tracked items.
6. **Notifications**: see reminders that have already fired (the seed
   data includes items due soon, so some reminders fire within the
   48-hour window automatically).
7. **Analytics**: completion rate, task breakdown chart, and a
   productivity tip.

## Switching from mock mode to real integrations

Every external dependency is controlled by a mode flag in `backend/.env`
-- flipping it to anything other than `mock` (and supplying the
corresponding credentials) switches that one piece to real behavior
without touching code:

- `ANTHROPIC_API_KEY=sk-ant-...` -- real Claude responses
- `OPPORTUNITY_SOURCE_MODE=live` -- would need real implementations added
  to `app/agents/opportunity_sources.py` (LinkedIn Jobs/Google Jobs/
  Coursera APIs each require their own partnership or paid access --
  the adapter functions are where that real HTTP call would go)
- `SMTP_MODE=live` + SMTP credentials -- real email sending
- `FIREBASE_MODE=live` + server key -- real push notifications
- `GOOGLE_CALENDAR_MODE=live` + credentials -- real calendar sync (not
  yet wired to an endpoint; would extend the Life Admin router)

## Project structure

```
life-admin-agent/
|-- backend/
|   |-- app/
|   |   |-- agents/        # Reminder, opportunity matching/sources, assistant, analytics
|   |   |-- core/          # Config, security, deps, scheduler
|   |   |-- db/            # DB session + seed script
|   |   |-- memory/        # ChromaDB-backed long-term user memory
|   |   |-- models/        # SQLAlchemy models + Pydantic schemas
|   |   |-- routers/       # API endpoints
|   |   `-- main.py
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- .env.example
|-- frontend/
|   |-- src/
|   |   |-- api/           # Axios client + auth context
|   |   |-- components/    # Shared UI components
|   |   `-- pages/         # Route pages (one per module)
|   |-- package.json
|   `-- Dockerfile
`-- docker-compose.yml
```

## Known limitations / next steps

- Opportunity sources (LinkedIn Jobs, Google Jobs, Coursera, government
  open data) are mocked with realistic sample data -- see
  `app/agents/opportunity_sources.py` for exactly where a real API call
  would replace each mock function. None of these were wired to real
  APIs since most require a paid tier or formal partnership most
  students won't have access to.
- Google Calendar sync is configured in settings but not yet wired to
  an endpoint -- the Life Admin module currently only stores items in
  the app's own database.
- The ChromaDB memory layer stores raw text memories; it doesn't yet
  do any explicit preference extraction/summarization before storing
  (e.g. distilling "I really want a remote ML internship" into a
  structured preference) -- it relies on embedding similarity over the
  raw text, which works but could be made more precise.
- No automated test suite -- core agent logic (recurrence date math
  including leap-year/month-overflow edge cases, the reminder window
  check, and the opportunity-matching empty-profile edge case) was
  manually verified during development, but there's no `pytest` suite.
