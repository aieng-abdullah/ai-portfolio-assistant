# Integration Guide

The AI Portfolio Assistant exposes a **REST API**. Clients call the API from their own frontend to fetch portfolio data and send chat messages.

## Base URL

```
https://your-api-domain.com
```

CORS is enabled for all origins (`*`), so any website can call the API.

---

## Available Endpoints

### Widget Data

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/widget/{slug}/config` | Theme + personality settings |
| GET | `/api/widget/{slug}/profile` | Name, title, bio, skills, contact |
| GET | `/api/widget/{slug}/projects` | Projects array |
| GET | `/api/widget/{slug}/services` | Services array |
| GET | `/api/widget/{slug}/faq` | FAQ array |

### Chat

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat/{slug}` | Send message, get AI response |

### Admin

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/widget/{slug}/create` | Create a new widget |
| POST | `/api/admin/widget/{slug}/disable` | Disable widget (kill switch) |
| POST | `/api/admin/widget/{slug}/enable` | Re-enable widget |
| GET | `/api/admin/widget/{slug}/stats` | Chat statistics |

### Health

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | API + database status |

---

## How to Use

### 1. Fetch Widget Config (for theming)

```javascript
const response = await fetch('https://api.example.com/api/widget/my-portfolio/config');
const config = await response.json();

// config = {
//   name: "My Portfolio",
//   theme: { primaryColor: "#4F46E5", chatTitle: "Chat with me!" },
//   personality: { tone: "witty_professional" }
// }
```

### 2. Send Chat Message

```javascript
const response = await fetch('https://api.example.com/api/chat/my-portfolio', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sessionId: 'user-123',
    message: 'What projects do you have?'
  })
});
const data = await response.json();

// data = {
//   response: "Here are some of my projects...",
//   sessionId: "user-123"
// }
```

### 3. Get Profile Data

```javascript
const response = await fetch('https://api.example.com/api/widget/my-portfolio/profile');
const profile = await response.json();

// profile = {
//   name: "John Doe",
//   title: "Developer",
//   bio: "Building cool stuff",
//   skills: ["React", "Node.js"],
//   contact: { email: "john@example.com" }
// }
```

---

## Example: Vanilla HTML/JS

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Portfolio</title>
</head>
<body>
  <h1>John Doe - Developer</h1>
  <div id="chat"></div>

  <script>
    const API = 'https://api.example.com';
    const SLUG = 'my-portfolio';
    const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

    // Load profile
    fetch(`${API}/api/widget/${SLUG}/profile`)
      .then(r => r.json())
      .then(profile => {
        document.getElementById('chat').innerHTML = `
          <h2>${profile.name}</h2>
          <p>${profile.bio}</p>
          <p>Skills: ${profile.skills.join(', ')}</p>
        `;
      });

    // Send message
    function sendMessage(text) {
      fetch(`${API}/api/chat/${SLUG}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, message: text })
      })
      .then(r => r.json())
      .then(data => console.log('AI:', data.response));
    }
  </script>
</body>
</html>
```

---

## Example: React

```jsx
import { useState, useEffect } from 'react';

const API = 'https://api.example.com';
const SLUG = 'my-portfolio';

function ChatWidget() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [config, setConfig] = useState(null);
  const sessionId = useState('session_' + Math.random().toString(36).substr(2, 9))[0];

  useEffect(() => {
    fetch(`${API}/api/widget/${SLUG}/config`)
      .then(r => r.json())
      .then(setConfig);
  }, []);

  const sendMessage = async () => {
    if (!message.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text: message }]);
    setMessage('');

    const res = await fetch(`${API}/api/chat/${SLUG}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, message })
    });
    const data = await res.json();

    setMessages(prev => [...prev, { role: 'bot', text: data.response }]);
  };

  return (
    <div>
      <h2>{config?.name || 'Portfolio Assistant'}</h2>
      <div>
        {messages.map((m, i) => (
          <div key={i} className={m.role}>
            {m.text}
          </div>
        ))}
      </div>
      <input
        value={message}
        onChange={e => setMessage(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default ChatWidget;
```

---

## Rate Limits

| Limit | Default | Configurable |
|-------|---------|--------------|
| Per session | 30 messages/hour | Yes, per widget |
| Per widget | 1000 messages/day | Yes, per widget |

When rate limited, the API returns:
```json
{
  "response": "You've reached the chat limit. Please try again later.",
  "sessionId": "user-123"
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 404 | Widget not found |
| 403 | Widget disabled (kill switch) |
| 429 | Rate limited |

---

## Testing

Test the API at: `https://api.example.com/docs` (Swagger UI)

Or use curl:
```bash
# Health check
curl https://api.example.com/api/health

# Get config
curl https://api.example.com/api/widget/my-portfolio/config

# Send message
curl -X POST https://api.example.com/api/chat/my-portfolio \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test-123", "message": "Hello!"}'
```
