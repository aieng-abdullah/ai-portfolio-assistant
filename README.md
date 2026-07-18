# AI Portfolio Assistant

An AI-powered portfolio assistant that answers visitor questions, showcases projects and services, and books meetings automatically via Google Calendar. Built with [n8n](https://n8n.io) and [Groq](https://groq.com) LLM.

## What It Does

- **Answers questions** about your profile, skills, projects, and services
- **Books meetings** by checking Google Calendar availability and creating events
- **Remembers context** within a conversation (15-message buffer)
- **Runs 24/7** as a self-hosted Docker container

## Architecture

```
Visitor sends message
    |
    v
n8n Chat Trigger (webhook)
    |
    v
AI Agent (LangChain via n8n)
    |-- Groq LLM
    |-- Conversation Memory (buffer window)
    |-- Tools:
    |     |-- get_profile
    |     |-- get_projects
    |     |-- get_services
    |     |-- get_current_date
    |     |-- check_availability (Google Calendar)
    |     |-- book_meeting (sub-workflow)
    v
Response to visitor
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A [Groq API key](https://console.groq.com/keys) (free tier available)
- A [Google Calendar](https://calendar.google.com/) account (only if using meeting booking)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/aieng-abdullah/ai-portfolio-assistant.git
cd ai-portfolio-assistant
```

### 2. Start n8n

```bash
docker compose up -d
```

n8n is now running at `http://localhost:5678`.

### 3. Set up credentials inside n8n

Open `http://localhost:5678` and complete the setup wizard. Then go to **Settings > Credentials**:

#### Groq API
1. Click **Add Credential** > search **Groq API**
2. Paste your Groq API key (free at [console.groq.com](https://console.groq.com/keys))
3. Save

#### Google Calendar (OAuth2) — only if using meeting booking
1. Click **Add Credential** > search **Google Calendar OAuth2 API**
2. Set up OAuth2 in [Google Cloud Console](https://console.cloud.google.com/):
   - Enable the Google Calendar API
   - Create OAuth2 credentials (Web Application)
   - Add `http://localhost:5678/rest/oauth2-credential/callback` as redirect URI
3. Paste Client ID and Client Secret into n8n
4. Connect your Google account

### 4. Import the workflow

1. In n8n, go to **Workflows > Import from File**
2. Select `n8n/workflows/AI Portfolio Assistant (1).json`
3. Open each node and select your newly created credentials from step 3
4. Activate the workflow

### 5. Create the "Book Meeting" sub-workflow

The main workflow references a sub-workflow for booking. Create it in n8n:

1. Create a new workflow with a **Workflow Trigger** node
2. Add input fields: `client_name`, `client_email`, `meeting_date`, `meeting_time`, `start_time`, `end_time`, `duration`
3. Add a **Google Calendar > Create Event** node using the same calendar credentials
4. Add validation logic (one booking per email per day)
5. Return `{ success: true/false, message: "...", event_id, event_link }`
6. Note the workflow ID and update the `book_meeting` tool in the main workflow

### 6. Test it

Open the chat widget and try:

- "Tell me about you"
- "What projects have you worked on?"
- "What services do you offer?"
- "I'd like to book a meeting"

## Project Structure

```
ai-portfolio-assistant/
├── docker-compose.yml          # n8n container
├── .env.example                # Environment variable template
├── .gitignore
├── README.md
├── docs/
│   ├── architecture.md
│   └── roadmap.md
├── knowledge/                  # Knowledge base reference files
│   ├── profile.md
│   ├── projects.md
│   ├── services.md
│   └── faq.md
└── n8n/
    └── workflows/
        └── AI Portfolio Assistant (1).json
```

## Customization

Edit the JavaScript code inside the `get_profile`, `get_projects`, and `get_services` tool nodes in the n8n workflow with your own details.

### Changing the LLM model

Update the **Groq Chat Model** node's `model` parameter. See [Groq Models](https://console.groq.com/docs/models).

### Changing the conversation memory window

In the **Simple Memory** node, adjust `contextWindowLength` (default: 15 messages).

## Troubleshooting

| Issue | Solution |
|---|---|
| n8n won't start | Check logs: `docker compose logs n8n` |
| Groq errors | Verify your API key is valid and has quota |
| Google Calendar not working | Re-authenticate OAuth2 credentials in n8n |
| Webhook not reachable | Ensure `WEBHOOK_URL` matches your setup |

## License

MIT
