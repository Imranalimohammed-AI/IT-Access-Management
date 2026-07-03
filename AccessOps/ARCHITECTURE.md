# IT Access Management — Architecture

## Overview

AccessOps is a two-layer application:

```
Browser (index.html)
        │
        │  REST API calls  (fetch /api/...)
        ▼
Flask Backend (main.py)  :5050
        │
        ├── Okta REST API  (HTTPS)
        ├── Active Directory  (LDAP/NTLM via ldap3)
        └── Local data/  (JSONL files — audit, requests, offboarding)
```

---

## Component Map

```
IT-Access-Management/
├── index.html           — Single-page frontend (vanilla JS, no build step)
├── main.py              — Flask REST API + static file server
├── data/
│   ├── audit_log.jsonl          — Append-only IAM action log
│   ├── access_requests.jsonl    — Access request queue
│   └── offboarded_users.jsonl   — Offboarding execution history
├── .env                 — Credentials (not committed)
├── requirements.txt     — Pinned Python dependencies
└── requirements.in      — Source dependency list
```

---

## Frontend — index.html

Single self-contained HTML/CSS/JS file. No framework, no build tool.

### Sections (client-side routing via `setNav()`)

| Section | Description |
|---------|-------------|
| `#section-users` | User search → profile card + Okta/AD/Apps/Licenses tabs |
| `#section-apps` | Global application access table |
| `#section-licenses` | License assignment table |
| `#section-requests` | Access request approval queue |
| `#section-audit` | Audit log viewer |
| `#section-agent` | Side-by-side agent view with risk flags |
| `#section-offboard` | 3-step bulk offboarding: Upload → Review → Results |

### Data flow (frontend)
```
User types in search box
        │
        ▼
onSearch() → fetch /api/okta/user?email=... + fetch /api/ad/user?email=...
        │
        ▼
renderProfile() + renderAccessTabs()   → Okta, AD, Apps, Licenses panels
        │
        ▼
Action button clicked (Suspend / Reset MFA / Disable AD / etc.)
        │
        ▼
confirmAction() → fetch POST /api/okta/user/{id}/suspend etc.
        │
        ▼
toast notification + audit log updated
```

---

## Backend — main.py

Flask app with 6 API groups:

### 1. Okta Integration
Uses Okta REST API v1 with SSWS token auth.

| Function | Okta endpoint called |
|----------|---------------------|
| User lookup | `GET /api/v1/users?filter=profile.email eq "..."` |
| Get groups | `GET /api/v1/users/{id}/groups` |
| Get apps | `GET /api/v1/users/{id}/appLinks` |
| Suspend | `POST /api/v1/users/{id}/lifecycle/suspend` |
| Activate | `POST /api/v1/users/{id}/lifecycle/activate` |
| Reset MFA | `POST /api/v1/users/{id}/lifecycle/reset_factors` |
| Reset password | `POST /api/v1/users/{id}/lifecycle/reset_password` |
| Remove app | `DELETE /api/v1/apps/{app_id}/users/{user_id}` |

### 2. Active Directory Integration
Uses `ldap3` with NTLM authentication.

| Function | LDAP operation |
|----------|---------------|
| User lookup | `SEARCH (mail=email)` |
| Disable account | `MODIFY userAccountControl` — sets bit `0x2` (ACCOUNTDISABLE) |
| Remove group | `MODIFY group.member` — `MODIFY_DELETE` of user DN |

### 3. Access Requests
Stored in `data/access_requests.jsonl`. Each record:
```json
{
  "id": "uuid",
  "timestamp": "2026-06-26T...",
  "status": "pending|approved|denied",
  "requester": "admin@cotiviti.com",
  "target_user": "user@cotiviti.com",
  "resource": "Salesforce - Standard User",
  "reason": "New joiner access required"
}
```

### 4. Audit Log
Append-only `data/audit_log.jsonl`. Written on every API action:
```json
{
  "id": "uuid",
  "timestamp": "2026-06-26T...",
  "action": "OKTA_SUSPEND",
  "target": "user@cotiviti.com",
  "performed_by": "system",
  "detail": "User suspended via AccessOps"
}
```

### 5. Bulk Offboarding Workflow

```
Step 1 — Upload CSV
    POST /api/offboard/preview  (multipart/form-data)
    ├── Parse CSV (max 500 rows)
    ├── Validate email column exists
    ├── Sanitize each row
    └── Return preview JSON for UI review

Step 2 — Review & Confirm
    User reviews parsed rows in browser
    Selects actions: okta_suspend | ad_disable | remove_apps

Step 3 — Execute
    POST /api/offboard/execute  (JSON body)
    ├── For each user:
    │   ├── Okta: look up by email → suspend
    │   ├── AD: search by mail attr → set UAC disabled bit
    │   └── Write offboarding record to data/offboarded_users.jsonl
    ├── Audit each action
    └── Return per-user results: success | partial | error
```

### 6. Input Sanitization
All external input is validated before use:
- Email addresses validated against strict regex `^[a-zA-Z0-9._%+\-]+@...`
- String fields truncated to safe max lengths (64–500 chars)
- No user input is passed directly to LDAP filters (constructed separately)
- No shell commands, no SQL, no eval

---

## Security Design

| Layer | Control |
|-------|---------|
| Credentials | Environment variables only — never in code |
| Input validation | Email regex + length limits on all inputs |
| LDAP | Service account with minimal permissions; NTLM auth |
| Okta | Scoped API token (not super-admin) |
| Audit | Append-only log — every action recorded with timestamp |
| CORS | Flask-CORS enabled for localhost dev; restrict in production |
| No secrets in responses | API keys/passwords never returned to frontend |

---

## Production Hardening (recommended before going live)

1. Run behind a reverse proxy (nginx) with HTTPS
2. Add authentication to the Flask app (Okta SSO or Basic Auth)
3. Restrict CORS to your internal domain
4. Move JSONL files to a proper database (PostgreSQL, SQLite)
5. Add rate limiting (`flask-limiter`) to all API endpoints
6. Use a dedicated Okta API token with minimum required scopes
7. Use an AD service account with read + targeted modify only
