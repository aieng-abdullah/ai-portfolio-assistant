# AGENTS.md — AI Portfolio Assistant

> This file helps AI assistants (and humans) understand the project quickly.
> Read this before making any changes.

---

## What This Project Is

A **SaaS platform** that provides a REST API for AI-powered chat.
Clients call the API from their own frontend to let visitors ask questions about the portfolio owner, view projects/services, and book meetings.

**Current state:** API-only (no auth, no payment yet).

---

## Tech Stack

| Layer | Tech | Notes |
|-------|------|-------|
| API Backend | **FastAPI** (Python) | `api/main.py` entry point |
| Database | **SQLAlchemy + PostgreSQL** | `api/database.py` |
| AI Workflow | **n8n** | `n8n/workflows/AI Portfolio Assistant v3.json` |
| LLM | **Groq** | Model: `openai/gpt-oss-120b` |
| Prototype Dashboard | **Streamlit** | `streamlit/app.py` |
| Deploy | **Docker Compose** | `docker-compose.yml` (prod), `docker-compose.dev.yml` (dev) |

---

## Project Structure

```
ai-portfolio-assistant/
├── api/                        # FastAPI backend (MAIN CODEBASE)
│   ├── main.py                 # App entry, routes
│   ├── config.py               # Environment variables
│   ├── database.py             # SQLAlchemy + PostgreSQL connection
│   ├── models.py               # Pydantic request/response models
│   ├── routes/
│   │   ├── widget.py           # GET /api/widget/{slug}/config, /profile, /projects, /services, /faq
│   │   ├── chat.py             # POST /api/chat/{slug} + GET /rate-limit
│   │   ├── admin.py            # POST /disable, /enable, /stats, /create
│   │   └── abuse.py            # POST /abuse-log
│   ├── services/
│   │   └── chat_proxy.py       # n8n proxy + local fallback + rate limiting
│   ├── tests/                  # Tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml          # pytest config
├── prisma/
│   └── schema.prisma           # DB schema (reference only, not used at runtime)
├── n8n/
│   └── workflows/
│       ├── AI Portfolio Assistant v3.json    # Agent orchestrator + multi-tenant (USE THIS)
│       └── Book Meeting Sub-Workflow.json    # Meeting booking sub-workflow
├── streamlit/                  # Prototype dashboard (demo tool, NOT production)
│   ├── app.py
│   └── pages/
│       ├── 1_Profile.py
│       ├── 2_Widget_Customize.py
│       └── 3_Embed.py
├── docs/
│   ├── integration.md          # User integration guide
│   ├── api.md                  # API documentation
│   ├── changelog.md            # Per-chunk build log
│   └── future-plan.md          # Production hardening roadmap
├── docker-compose.yml          # Production: postgres + n8n + api
├── docker-compose.dev.yml      # Development: same but with volume mounts
├── .env.example                # All environment variables
└── README.md                   # Project overview
```

---

## Key Architecture Decisions

### 1. Multi-Tenancy
- Each user gets a **Widget** with a unique `slug`
- All data (profile, projects, services, FAQ, theme, personality) stored as JSON in the Widget model
- n8n workflow uses the `slug` to fetch data from the API dynamically
- **No hardcoded data** in n8n — everything comes from the database

### 2. Chat Flow
```
Client's frontend → POST /api/chat/{slug}
  → Rate limit check (SQLAlchemy)
  → Guard input (injection, spam, length)
  → Log message to DB
  → Try n8n webhook (10s timeout)
    → If n8n available: AI Agent processes with Groq LLM
    → If n8n down: Local fallback (keyword-based responses)
  → Guard output (data leaks, prompt leaks)
  → Log response to DB
  → Return to client
```

### 3. Local Fallback Mode
When n8n is not running, `chat_proxy.py` uses `_local_fallback()` which:
- Matches keywords in the user message (skill, project, service, contact, etc.)
- Returns relevant data from the widget's database record
- Works fully offline for testing/demo

### 4. Guardrails (7 Layers)
1. **Input Guard** — Blocks injection, spam, oversized messages (in n8n workflow)
2. **Hardened System Prompt** — Enforces scope, blocks prompt leaks (in n8n workflow)
3. **Output Filter** — Catches data leaks, sensitive info (in n8n workflow)
4. **Tool Restrictions** — Read-only tools except calendar booking
5. **Rate Limiting** — Per-session (30/hr) + per-widget (1000/day), configurable
6. **Abuse Logger** — Flags suspicious activity
7. **Kill Switch** — Disable widget instantly via admin endpoint

---

## API Endpoints

### Public (Widget Data)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/widget/{slug}/config` | Theme + personality |
| GET | `/api/widget/{slug}/profile` | Profile data |
| GET | `/api/widget/{slug}/projects` | Projects array |
| GET | `/api/widget/{slug}/services` | Services array |
| GET | `/api/widget/{slug}/faq` | FAQ array |
| GET | `/api/widget/{slug}/rate-limit?sessionId=x` | Rate limit status |

### Chat
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat/{slug}` | Send message → get AI response |

### Admin
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/widget/{slug}/create` | Create new widget |
| POST | `/api/admin/widget/{slug}/disable` | Kill switch |
| POST | `/api/admin/widget/{slug}/enable` | Re-enable |
| GET | `/api/admin/widget/{slug}/stats` | Chat statistics |
| POST | `/api/widget/{slug}/abuse-log` | Log abuse |

### Health
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check |

---

## Database Schema (SQLAlchemy)

```python
Widget:
  id, slug (unique), name, profile (JSON), projects (JSON), services (JSON),
  faq (JSON), personality (JSON), theme (JSON), rateLimit (int, default 30),
  dailyMessageLimit (int, default 1000), isActive (bool), userId, timestamps

ChatSession:
  id, sessionId, widgetId, messageCount, lastMessageAt, timestamps
  @@unique([sessionId, widgetId])

ChatLog:
  id, widgetId, sessionId, role, message, createdAt
```

---

## How to Run

### Local Development (no Docker)
```bash
cd api
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```
- API: http://localhost:3000
- API Docs: http://localhost:3000/docs

### With Docker
```bash
docker compose up -d
# or for dev with hot reload:
docker compose -f docker-compose.dev.yml up -d
```

### Streamlit Prototype
```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```
- Dashboard: http://localhost:8501

---

## Running Tests
```bash
cd api
python -m pytest tests/ -v
```
24 tests covering: widget endpoints, chat, admin, health, guardrails.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://portfolio:portfolio_dev@localhost:5432/portfolio` | Database connection |
| `N8N_WEBHOOK_URL` | `http://localhost:5678/webhook/` | n8n webhook endpoint |
| `GROQ_API_KEY` | (empty) | Groq LLM API key |
| `API_PORT` | `3000` | API server port |
| `ENVIRONMENT` | `development` | development / production |
| `GENERIC_TIMEZONE` | `UTC` | Timezone for n8n |

---

## Git Workflow

- `main` branch — protected, no direct pushes
- Feature branches: `feature/chunk-{N}-{description}`
- Commit format: `feat(chunk-N): description`
- Merge to main after review, then delete feature branch

---

## What's NOT Done Yet (Future Plan)

See `docs/future-plan.md` for full list. Key items:
- **Auth** — No user login/registration (web developer will add)
- **Payment** — No subscription system yet
- **Monitoring** — No Prometheus/Grafana yet
- **Token cost tracking** — Not implemented
- **Circuit breaker** — Not implemented
- **Redis caching** — Not implemented
- **Production Docker** — Needs health checks, resource limits

---

## Common Issues

| Issue | Fix |
|-------|-----|
| Chat returns "temporarily unavailable" | n8n not running — local fallback should work, or start n8n |
| "Widget not found" | Create widget via `POST /api/widget/{slug}/create` |
| Import errors | Run `pip install -r requirements.txt` |
| Database errors | Check PostgreSQL is running: `docker compose up -d postgres` |
| Tests fail | Make sure you're in `api/` directory, run `pip install pytest pytest-asyncio` |

---

## Contact / Ownership

- **AI Engineering Team** — Backend, n8n workflow, guardrails, infrastructure
- **Web Developer** — Dashboard UI, auth, widget frontend (not yet assigned)
- **Streamlit** — Prototype/demo tool only, not production
