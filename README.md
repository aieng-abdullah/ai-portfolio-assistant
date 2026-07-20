# AI Portfolio Assistant

A SaaS platform that lets users add an AI-powered chat widget to their website. Visitors can ask questions about the portfolio owner, view projects/services, and book meetings.

## What It Does

- **Embeddable chat widget** — one line of code to add to any website
- **Multi-tenant** — each user gets their own widget with custom data
- **Customizable** — colors, logo, personality, system prompt
- **Guardrails** — input validation, output filtering, rate limiting
- **Production-ready** — health checks, kill switch, abuse logging

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  USER'S WEBSITE                       │
│   <script src="widget.js" data-widget-id="abc123">   │
└──────────────┬───────────────────────────────────────┘
               │ loads iframe
               ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend                          │
│  /widget/{slug}  — Chat UI (iframe)                  │
│  /widget.js      — Loader script                     │
│  /api/chat/{slug} — Chat proxy → n8n                 │
│  /api/widget/*   — Config, profile, projects         │
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
- **n8n**: http://localhost:5678
- **PostgreSQL**: localhost:5432

### 4. Set up n8n credentials

1. Open http://localhost:5678
2. Go to Settings → Credentials
3. Add Groq API credential with your key
4. Import workflow: `n8n/workflows/AI Portfolio Assistant v2.json`
5. Activate the workflow

### 5. Create a widget

```bash
# Create a widget via API
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

### 6. Embed on your website

```html
<script src="http://localhost:3000/widget.js" data-widget-id="my-portfolio" async></script>
```

## Project Structure

```
ai-portfolio-assistant/
├── api/                        # FastAPI backend
│   ├── main.py                 # App entry point
│   ├── config.py               # Environment config
│   ├── database.py             # Prisma connection
│   ├── models.py               # Pydantic models
│   ├── routes/
│   │   ├── widget.py           # Widget data endpoints
│   │   ├── chat.py             # Chat proxy + rate limiting
│   │   ├── admin.py            # Kill switch + stats
│   │   └── abuse.py            # Abuse logging
│   ├── services/
│   │   └── chat_proxy.py       # n8n proxy + rate limiter
│   ├── static/
│   │   ├── widget.js           # Loader script
│   │   └── widget.html         # Chat UI template
│   ├── Dockerfile
│   └── requirements.txt
├── prisma/
│   └── schema.prisma           # Database schema
├── n8n/
│   └── workflows/
│       └── AI Portfolio Assistant v2.json
├── streamlit/                  # Prototype dashboard
│   ├── app.py
│   └── pages/
├── docs/
│   ├── integration.md          # User integration guide
│   ├── api.md                  # API documentation
│   └── changelog.md            # Per-chunk changelog
├── docker-compose.yml          # Production stack
├── docker-compose.dev.yml      # Development stack
└── .env.example
```

## API Documentation

See [docs/api.md](docs/api.md) or visit http://localhost:3000/docs (auto-generated).

## Integration Guide

See [docs/integration.md](docs/integration.md) for platform-specific instructions.

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

# Run Streamlit prototype
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## License

MIT
