# Changelog

## Chunk 1 — Database Schema + Docker PostgreSQL
- Added Prisma schema with Widget, ChatSession, ChatLog models
- Added PostgreSQL service to docker-compose.yml
- Updated .env.example with DATABASE_URL and postgres config
- Updated .gitignore for Python, Prisma, IDE files

## Chunk 2 — FastAPI Skeleton
- FastAPI app entry point with CORS and lifespan management
- config.py with environment variable loading
- database.py with Prisma connection management
- models.py with Pydantic request/response models
- Placeholder route files (widget.py, chat.py)
- Dockerfile and .dockerignore for API service
- requirements.txt with dependencies
- API service added to docker-compose.yml

## Chunk 3 — Widget Endpoints
- GET /api/widget/{slug}/config — theme + personality
- GET /api/widget/{slug}/profile — profile data
- GET /api/widget/{slug}/projects — projects array
- GET /api/widget/{slug}/services — services array
- GET /api/widget/{slug}/faq — FAQ array
- Widget lookup with 404 and active status checks

## Chunk 4 — Widget Frontend
- widget.js — lightweight loader script (floating bubble + iframe)
- widget.html — chat UI template with theme support
- Routes to serve widget.js and /widget/{slug}
- Position, greeting, and theme customization support

## Chunk 5 — Chat Proxy + Rate Limiting
- POST /api/chat/{slug} — proxies messages to n8n webhook
- GET /api/widget/{slug}/rate-limit — rate limit status check
- Session-based rate limiting (per hour, configurable per widget)
- Daily message limit (configurable per widget)
- Chat logging to database (user + assistant messages)
- Graceful error handling for n8n timeouts and failures

## Chunk 6 — n8n Workflow Redesign
- Replaced hardcoded data tools with dynamic system prompt injection
- Added Input Guard node for injection/spam detection
- Added Output Guard node for data leak prevention
- Added Build System Prompt node (merges personality + guardrails)
- Kept get_current_date, check_availability, book_meeting tools
- Removed broken Data Table rate limiting (handled by API now)
- Added Is Blocked? conditional routing

## Chunk 7 — Guardrails
- Input Guard: prompt injection, spam, length, empty message detection
- Output Guard: data leak, prompt leak, sensitive info filtering
- Hardened system prompt with scope enforcement
- Tool restrictions (read-only except book_meeting)

## Chunk 8 — Kill Switch + Abuse Logging
- POST /api/admin/widget/{slug}/disable — kill switch
- POST /api/admin/widget/{slug}/enable — re-enable widget
- GET /api/admin/widget/{slug}/stats — chat statistics
- POST /api/widget/{slug}/abuse-log — log abuse attempts

## Chunk 9 — Docker Compose Production Stack
- Finalized docker-compose.yml with 3 services (postgres, n8n, api)
- Added healthchecks for all services
- Added backend network for service communication
- Created docker-compose.dev.yml for development
- Updated .env.example with all variables

## Chunk 10 — Streamlit Prototype
- Dashboard app with health check, stats, chat test
- Profile editor page
- Widget customizer with live preview
- Embed code generator with platform instructions
- requirements.txt for Streamlit dependencies
