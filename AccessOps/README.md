# IT Access Management — AccessOps

Cotiviti IT Engineering | Internal IAM Tool

AccessOps is a web-based Identity & Access Management dashboard for IT administrators. It provides real-time visibility into user access across Okta and Active Directory, with approval workflows, audit logging, and bulk offboarding.

---

## Features

| Section | What it does |
|---------|-------------|
| **Users** | Search users, view Okta profile, AD account, app access, and licenses |
| **Applications** | See all application assignments across the org |
| **Licenses** | Manage Microsoft 365 and software license assignments |
| **Requests** | Approve or deny access requests with one click |
| **Audit Log** | Full tamper-evident log of every IAM action taken |
| **Agent View** | Side-by-side user comparison and risk flag view |
| **Bulk Offboarding** | CSV upload → review → execute to offboard multiple users at once |

---

## Setup

**1. Create and activate a virtual environment:**

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
```

**2. Install dependencies:**

```powershell
uv pip install -r requirements.txt
```

**3. Configure environment variables:**

Copy `.env` and fill in your real credentials:

```powershell
copy .env .env.local
```

Edit `.env` with:
- `OKTA_DOMAIN` — your Okta org domain (e.g. `cotiviti.okta.com`)
- `OKTA_API_TOKEN` — Okta API token (Admin → Security → API → Tokens)
- `AD_SERVER` — LDAP URL of your Active Directory server
- `AD_BIND_USER` — Service account UPN for LDAP bind
- `AD_BIND_PASSWORD` — Service account password

**4. Run:**

```powershell
python main.py
```

Open your browser at: **http://localhost:5050**

---

## API Endpoints

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/okta/user?email=` | Fetch Okta profile, groups, and app links |
| GET | `/api/ad/user?email=` | Fetch AD account details and group memberships |

### Okta Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/okta/user/{id}/suspend` | Suspend Okta account |
| POST | `/api/okta/user/{id}/activate` | Reactivate Okta account |
| POST | `/api/okta/user/{id}/reset-mfa` | Clear all MFA factors |
| POST | `/api/okta/user/{id}/reset-password` | Send password reset email |
| POST | `/api/okta/user/{id}/remove-app` | Remove app assignment |

### Active Directory Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ad/user/disable` | Disable AD account (sets UAC disabled flag) |
| POST | `/api/ad/user/remove-group` | Remove user from AD security group |

### Access Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/requests` | List all access requests |
| POST | `/api/requests` | Submit a new access request |
| POST | `/api/requests/{id}/approve` | Approve a request |
| POST | `/api/requests/{id}/deny` | Deny a request |

### Bulk Offboarding
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/offboard/preview` | Upload CSV, get parsed preview |
| POST | `/api/offboard/execute` | Execute offboarding for confirmed users |
| GET | `/api/offboard/history` | View past offboarding records |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audit` | Retrieve audit log (last 200 entries) |
| GET | `/api/health` | Health check — Okta and AD connectivity status |

---

## CSV Offboarding Template

| Column | Required | Description |
|--------|----------|-------------|
| `email` | Yes | Employee email (unique identifier) |
| `employee_id` | No | Employee ID for reference |
| `reason` | No | Offboarding reason (e.g. Resignation, Termination) |
| `notes` | No | Additional notes for the audit log |

---

## Data Files

All persistent data is stored locally under `data/`:

| File | Contents |
|------|----------|
| `data/audit_log.jsonl` | Every IAM action, timestamped |
| `data/access_requests.jsonl` | Submitted access requests and their status |
| `data/offboarded_users.jsonl` | Offboarding history with per-step results |

---

## Security Notes

- All credentials are loaded from environment variables — never hardcoded.
- All user input is sanitized (email regex, string length limits) before use.
- Audit log is append-only and records every action with timestamp and actor.
- LDAP bind uses a dedicated service account with read + modify permissions only.
- Okta API token should use a scoped read-write token, not a super-admin token.
