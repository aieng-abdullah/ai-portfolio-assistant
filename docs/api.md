# API Documentation

## Base URL
```
Development: http://localhost:3000
Production:  https://app.yourdomain.com
```

## Authentication
All endpoints are public (rate limited on chat). Auth will be added by web developer.

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

---

## Widget Management

### POST `/api/widget/{slug}/create`
Create a new widget with the given slug.

**Request:**
```json
{
  "name": "My Portfolio"
}
```

**Response:**
```json
{
  "slug": "my-portfolio",
  "name": "My Portfolio",
  "id": "abc123"
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
