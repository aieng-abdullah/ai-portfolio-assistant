# AI Portfolio Assistant

A SaaS platform that provides a **REST API** for AI-powered chat. Clients call the API from their own frontend to let visitors ask questions about the portfolio owner, view projects/services, and book meetings.

## What It Does

- **REST API** — clients fetch portfolio data and send chat messages from their own UI
- **Multi-tenant** — each user gets their own widget with custom data
- **Customizable** — colors, logo, personality, system prompt
- **Guardrails** — input validation, output filtering, rate limiting
- **Production-ready** — PostgreSQL, health checks, kill switch, abuse logging

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  CLIENT'S FRONTEND                    │
│   Calls REST API from their own UI                   │
└──────────────┬───────────────────────────────────────┘
               │ HTTP requests
               ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend                          │
│  GET  /api/widget/{slug}/config  — Theme settings    │
│  GET  /api/widget/{slug}/profile — Portfolio data    │
│  POST /api/chat/{slug}           — Chat proxy → n8n  │
│  POST /api/admin/widget/{slug}/* — Admin controls    │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│          n8n Workflow (Multi-Tenant)                  │
│  Input Guard → AI Agent → Output Guard               │
│  Tools: profile, projects, services, calendar        │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│  PostgreSQL     │  Groq LLM     │  Google Calendar   │
└──────────────────────────────────────────────────────┘
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A [Groq API key](https://console.groq.com/keys) (free tier available)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/aieng-abdullah/ai-portfolio-assistant.git
cd ai-portfolio-assistant
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

### 3. Start services

```bash
docker compose up -d
```

Services running:
- **API**: http://localhost:3000
- **API Docs**: http://localhost:3000/docs
- **n8n**: http://localhost:5678
- **PostgreSQL**: localhost:5432

### 4. Set up n8n credentials

1. Open http://localhost:5678
2. Go to Settings → Credentials
3. Add Groq API credential with your key
4. Import workflow: `n8n/workflows/AI Portfolio Assistant v3.json`
5. Activate the workflow

### 5. Create a widget

```bash
curl -X POST http://localhost:3000/api/widget \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "my-portfolio",
    "name": "My Portfolio",
    "profile": {
      "name": "John Doe",
      "title": "Developer",
      "bio": "Building cool stuff",
      "skills": ["React", "Node.js"],
      "contact": {"email": "john@example.com"}
    }
  }'
```

### 6. Use the API

```javascript
// Fetch config for theming
const config = await fetch('http://localhost:3000/api/widget/my-portfolio/config').then(r => r.json());

// Send chat message
const response = await fetch('http://localhost:3000/api/chat/my-portfolio', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sessionId: 'user-123', message: 'Hello!' })
}).then(r => r.json());
```

## Project Structure

```
ai-portfolio-assistant/
├── api/                        # FastAPI backend
│   ├── main.py                 # App entry point
│   ├── config.py               # Environment config
│   ├── database.py             # SQLAlchemy + PostgreSQL
│   ├── models.py               # Pydantic models
│   ├── routes/
│   │   ├── widget.py           # Widget data endpoints
│   │   ├── chat.py             # Chat proxy + rate limiting
│   │   ├── admin.py            # Kill switch + stats
│   │   └── abuse.py            # Abuse logging
│   ├── services/
│   │   └── chat_proxy.py       # n8n proxy + rate limiter
│   ├── Dockerfile
│   └── requirements.txt
├── n8n/
│   └── workflows/
│       ├── AI Portfolio Assistant v3.json    # Agent orchestrator + multi-tenant
│       └── Book Meeting Sub-Workflow.json    # Meeting booking sub-workflow
├── streamlit/                  # Prototype dashboard
│   ├── app.py
│   └── pages/
├── docs/
│   ├── integration.md          # API integration guide
│   ├── api.md                  # API documentation
│   └── changelog.md            # Per-chunk changelog
├── docker-compose.yml          # Production stack
├── docker-compose.dev.yml      # Development stack
└── .env.example
```

## API Documentation

See [docs/integration.md](docs/integration.md) for integration examples, or visit http://localhost:3000/docs (auto-generated Swagger UI).

## Guardrails

The n8n workflow includes 7 layers of protection:

1. **Input Guard** — blocks injection, spam, oversized messages
2. **Hardened System Prompt** — enforces scope, blocks prompt leaks
3. **Output Filter** — catches data leaks, sensitive info
4. **Tool Restrictions** — read-only tools except calendar booking
5. **Rate Limiting** — per-session and per-widget limits
6. **Abuse Logger** — flags suspicious activity
7. **Kill Switch** — disable widget instantly

## Development

```bash
# Start in development mode
docker compose -f docker-compose.dev.yml up -d

# Run tests
cd api
pip install -r requirements.txt
pytest tests/ -v

# Run Streamlit prototype
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## License

MIT
