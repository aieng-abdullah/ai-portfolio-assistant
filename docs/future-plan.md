# Future Plan: Production Hardening

## Status: Planned (not yet implemented)

This document tracks what we'll add when moving from prototype to production.

---

## 1. Monitoring & Observability

- [ ] Structured JSON logging (every request: widget_id, session_id, latency, status, guardrail events)
- [ ] Prometheus metrics (auto-instrument all endpoints, track request rate, error rate, latency)
- [ ] Grafana dashboards (visualize metrics, set alerts)
- [ ] Sentry error tracking (capture exceptions with full context)
- [ ] Extend /api/health with service-level checks (n8n, DB, Groq)

## 2. Token Cost Tracking

- [ ] TokenUsage DB model (input_tokens, output_tokens, model, cost_cents)
- [ ] Accurate token counting (extract usage from Groq LLM response in n8n)
- [ ] Cost per widget aggregation (for billing)
- [ ] Cost dashboard in Streamlit/Grafana (daily/monthly costs, top widgets)
- [ ] Budget alerts (per-widget and per-user spending limits)

## 3. Resilience & Graceful Failure

- [ ] Circuit breaker pattern (n8n, Groq, DB, Calendar — open after 3 failures)
- [ ] Retry with exponential backoff (0.5s → 1s → 2s → fallback)
- [ ] Timeout enforcement (n8n: 10s, Groq: 15s, DB: 5s, Calendar: 5s)
- [ ] Graceful degradation (n8n down → local fallback, DB down → cached config)
- [ ] /api/status endpoint (service health dashboard)
- [ ] Alert rules (error rate > 5% = warning, > 20% = critical)
- [ ] Auto-restart on critical failures

## 4. Security Hardening

- [ ] API key authentication for admin endpoints
- [ ] CORS configuration per-widget
- [ ] SQL injection prevention (already handled by SQLAlchemy)
- [ ] Rate limiting per IP (in addition to per-session)
- [ ] DDoS protection (Cloudflare or similar)
- [ ] HTTPS enforcement in production

## 5. Scalability

- [ ] Redis caching layer (widget config, rate limits)
- [ ] Database connection pooling (PgBouncer)
- [ ] Horizontal scaling (multiple API instances)
- [ ] n8n queue mode for high throughput
- [ ] CDN for widget.js and static assets
- [ ] Load testing (k6 or locust)
