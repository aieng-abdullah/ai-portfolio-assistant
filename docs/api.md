# API Documentation

## Base URL
```
Development: http://localhost:3000
Production:  https://app.yourdomain.com
```

## Authentication
- Widget endpoints (`/api/widget/*`): Public (serving widget data)
- Admin endpoints (`/api/admin/*`): Bearer token required
- Chat endpoint (`/api/chat/*`): Public (rate limited)

---

## Widget Endpoints

### GET `/api/widget/{slug}/config`
Returns theme + personality configuration for widget rendering.

**Response:**
```json
{
  "name": "John's Portfolio",
  "theme": {
    "primaryColor": "#4F46E5",
    "secondaryColor": "#1E1B4B",
    "fontFamily": "Inter",
    "borderRadius": "12px",
    "logoUrl": "https://...",
    "chatTitle": "Chat with John's AI",
    "chatSubtitle": "Ask about my work",
    "welcomeMessage": "Hey there!",
    "position": "bottom-right"
  },
  "personality": {
    "tone": "witty_professional",
    "greeting": "Hey there!"
  }
}
```

### GET `/api/widget/{slug}/profile`
Returns profile data.

**Response:**
```json
{
  "name": "John Doe",
  "title": "Full Stack Developer",
  "bio": "Building cool stuff with code.",
  "location": "Remote",
  "skills": ["React", "Node.js", "Python"],
  "experience": ["5 years at Tech Co", "3 years freelance"],
  "contact": {
    "email": "john@example.com",
    "website": "https://johndoe.com",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

### GET `/api/widget/{slug}/projects`
Returns projects array.

**Response:**
```json
[
  {
    "name": "Project Alpha",
    "description": "A cool project",
    "technologies": ["React", "Node.js"]
  }
]
```

### GET `/api/widget/{slug}/services`
Returns services array.

### GET `/api/widget/{slug}/faq`
Returns FAQ array.

### GET `/api/widget/{slug}/rate-limit`
Returns rate limit status for a session.

**Query Params:** `sessionId` (required)

**Response:**
```json
{
  "over_limit": false,
  "session_messages": 12,
  "session_limit": 30,
  "daily_messages": 450,
  "daily_limit": 1000
}
```

---

## Chat Endpoints

### POST `/api/chat/{slug}`
Send a chat message. Proxies to n8n.

**Request:**
```json
{
  "sessionId": "abc-123",
  "message": "Tell me about your projects"
}
```

**Response:**
```json
{
  "response": "I've worked on several exciting projects...",
  "sessionId": "abc-123"
}
```

### POST `/api/widget/{slug}/log`
Log a chat message (called by n8n).

**Request:**
```json
{
  "sessionId": "abc-123",
  "role": "user",
  "message": "Hello"
}
```

### POST `/api/widget/{slug}/abuse-log`
Log abuse attempt.

**Request:**
```json
{
  "sessionId": "abc-123",
  "filtered": true,
  "timestamp": "2026-07-20T12:00:00Z"
}
```

---

## Widget Serving

### GET `/widget.js`
Serves the loader script (minified in production).

### GET `/widget/{slug}`
Serves the chat UI HTML page (loaded in iframe).

---

## Admin Endpoints

### POST `/api/admin/widget/{slug}/disable`
Disable a widget (kill switch).

**Response:**
```json
{
  "message": "Widget 'abc123' disabled",
  "isActive": false
}
```

### POST `/api/admin/widget/{slug}/enable`
Re-enable a widget.

### GET `/api/admin/widget/{slug}/stats`
Get chat statistics.

**Response:**
```json
{
  "slug": "abc123",
  "isActive": true,
  "rateLimit": 30,
  "dailyMessageLimit": 1000,
  "totalMessages": 1234,
  "hourlyMessages": 45,
  "dailyMessages": 320,
  "activeSessions": 12
}
```

---

## Health

### GET `/api/health`
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "timestamp": "2026-07-20T12:00:00Z"
  },
  "timestamp": "2026-07-20T12:00:00Z"
}
```
