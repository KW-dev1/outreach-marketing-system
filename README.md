# Outreach Marketing System

A personal cold-outreach tool: manage contacts, send an initial email plus
up to two automated follow-ups from your own Outlook mailbox, track opens,
and watch everything in a dashboard. Runs entirely on your laptop — no paid
services required.

## Status

This is the initial project scaffold. What's wired up so far:

- Flask JSON API with the SQLite data model and `/api/sequences`,
  `/api/contacts`, `/track/<id>.png` endpoints implemented.
- Next.js dashboard (list + add-contact views) with polling and error
  states.
- Background worker and Microsoft Graph client are stubbed out
  (`backend/app/worker.py`, `backend/app/graph_client.py`) — the actual
  MSAL device-code auth, sending, and reply/follow-up logic land in a
  follow-up commit.

## Architecture

- **Backend**: Python + Flask, JSON REST API only (no server-rendered
  pages), SQLite (single local file).
- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS.
- **Email**: Microsoft Graph API, delegated permissions, MSAL device-code
  flow — sends and reads mail as your own mailbox.
- **Open tracking**: optional 1x1 pixel; only active when a public URL
  (e.g. via `ngrok`) is configured.

Two independently-runnable processes: backend on port 5000, frontend on
port 3000.

## Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in AZURE_CLIENT_ID, AZURE_TENANT_ID, SENDER_EMAIL
python run.py
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit http://localhost:3000.

### Azure App Registration

Required before Graph sending/reading works (not yet wired up in this
scaffold, but the config keys are already in place):

1. Go to https://portal.azure.com → **Azure Active Directory** → **App
   registrations** → **New registration**.
2. Name it (e.g. "Outreach Marketing System"), choose **Accounts in this
   organizational directory only** (or as appropriate for your tenant),
   leave Redirect URI blank for now.
3. Under **Authentication**, enable **Allow public client flows** → Yes.
4. Under **API permissions**, add **Microsoft Graph** → **Delegated
   permissions** → `Mail.Send` and `Mail.Read`. Grant admin consent if
   required by your tenant.
5. Copy the **Application (client) ID** and **Directory (tenant) ID** from
   the app's Overview page into `backend/.env`.

No client secret is needed — this app uses the public client device-code
flow.

### Optional: open tracking

Open tracking needs a publicly reachable URL for the backend's `/track`
endpoint. Run a free tunnel (e.g. `ngrok http 5000`) and set
`PUBLIC_BASE_URL` in `backend/.env` to the tunnel's HTTPS URL. Leave it
blank to disable tracking entirely — sending works fine without it.

## Configuration

| Variable | Default | Notes |
| --- | --- | --- |
| `AZURE_CLIENT_ID` | *(required)* | Azure App Registration client ID |
| `AZURE_TENANT_ID` | *(required)* | Azure tenant ID |
| `SENDER_EMAIL` | *(required)* | Informational/display only |
| `MIN_DELAY_SECONDS` | 45 | Minimum delay between sends |
| `MAX_DELAY_SECONDS` | 180 | Maximum delay between sends |
| `MAX_EMAILS_PER_DAY` | 40 | Rolling 24h send cap |
| `FOLLOWUP_1_DAYS` | 1 | Days after first send before follow-up 1 |
| `FOLLOWUP_2_DAYS` | 3 | Days after follow-up 1 before follow-up 2 |
| `PUBLIC_BASE_URL` | *(blank)* | Enables open tracking when set |
| `NEXT_PUBLIC_API_URL` (frontend) | `http://127.0.0.1:5000` | Backend base URL |

## Project layout

```
backend/
  run.py              # entrypoint (Flask app + worker)
  config.py           # env-driven configuration
  app/
    __init__.py       # app factory
    models.py         # SQLAlchemy models (contacts, sequences, events, send log)
    routes.py         # JSON API + tracking pixel endpoint
    worker.py          # background scheduler (send/follow-up logic - stub)
    graph_client.py    # MSAL + Graph API client (auth/send/read - stub)
frontend/
  app/
    page.tsx          # dashboard (main view)
    add/page.tsx       # add-contact form
  lib/api.ts           # backend API client
```

## Non-goals

No multi-user/login, no CRM features beyond what's listed, no built-in
anti-spam/compliance checks — you're responsible for complying with
applicable regulations (e.g. CAN-SPAM) for who you contact and how.
