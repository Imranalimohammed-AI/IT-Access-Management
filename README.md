<div align="center">

# IT Access Management — AccessOps

**Web-based Identity & Access Management dashboard for IT administrators**

[![Python](https://img.shields.io/badge/Python-3.14-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Branch](https://img.shields.io/badge/branch-main-3b82f6?style=flat-square&logo=git&logoColor=white)](https://github.com/Imranalimohammed-AI/IT-Access-Management)

*Cotiviti IT Engineering · Internal IAM Platform*

</div>

---

## Overview

AccessOps gives IT administrators a single pane of glass over user identities across **Okta** and **Active Directory**. Approve or deny access requests in one click, run bulk offboarding workflows from a CSV upload, and maintain a tamper-evident audit log of every IAM action taken.

---

## Features

| Module | Description |
|--------|-------------|
| **Users** | Search users, view Okta profile, AD account, app assignments, and licences |
| **Applications** | Full application assignment matrix across the organisation |
| **Licences** | Microsoft 365 and software licence management |
| **Requests** | One-click approval / denial with full audit trail |
| **Audit Log** | Append-only, timestamped record of every IAM action |
| **Agent View** | Side-by-side user comparison with risk flag highlighting |
| **Bulk Offboarding** | CSV upload → review → execute; supports hundreds of users at once |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.14 · Flask 3.1 |
| Identity | Okta REST API · Active Directory (LDAP) |
| Frontend | Vanilla JS · HTML5 · CSS3 |
| Persistence | Append-only JSONL (audit, requests, offboarding history) |
| Package manager | [uv](https://github.com/astral-sh/uv) |

---

## Branch Strategy

```
main          ← production, protected (PR-only)
  └── develop ← integration, all PRs target here
        ├── feature/<name>
        ├── fix/<name>
        └── hotfix/<name>  (branched from main for critical patches)
```

---

## Quick Start

```powershell
# Clone
git clone git@github.com:Imranalimohammed-AI/IT-Access-Management.git
cd IT-Access-Management/AccessOps

# Create virtual environment
uv venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Configure environment (never commit .env)
copy .env.example .env
# Edit .env — see Environment Variables section below

# Start the server
python main.py
```

Open **http://localhost:5050** in your browser.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OKTA_DOMAIN` | Okta org domain (e.g. `cotiviti.okta.com`) |
| `OKTA_API_TOKEN` | Scoped Okta API token — **not** a super-admin token |
| `AD_SERVER` | LDAP URL of your Active Directory server |
| `AD_BIND_USER` | Service account UPN for LDAP bind |
| `AD_BIND_PASSWORD` | Service account password |

> `.env` is excluded from version control by `.gitignore`. Never commit credentials.

---

## API Reference

<details>
<summary><strong>Users</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/okta/user?email=` | Okta profile, groups, and app links |
| `GET` | `/api/ad/user?email=` | AD account details and group memberships |

</details>

<details>
<summary><strong>Okta Actions</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/okta/user/{id}/suspend` | Suspend Okta account |
| `POST` | `/api/okta/user/{id}/activate` | Reactivate account |
| `POST` | `/api/okta/user/{id}/reset-mfa` | Clear all MFA factors |
| `POST` | `/api/okta/user/{id}/reset-password` | Send password reset email |
| `POST` | `/api/okta/user/{id}/remove-app` | Remove app assignment |

</details>

<details>
<summary><strong>Active Directory</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ad/user/disable` | Disable AD account |
| `POST` | `/api/ad/user/remove-group` | Remove user from security group |

</details>

<details>
<summary><strong>Bulk Offboarding</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/offboard/preview` | Upload CSV, get parsed preview |
| `POST` | `/api/offboard/execute` | Execute offboarding |
| `GET` | `/api/offboard/history` | View past offboarding records |

</details>

<details>
<summary><strong>System</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/audit` | Last 200 audit log entries |
| `GET` | `/api/health` | Okta and AD connectivity status |

</details>

---

## Security

| Control | Implementation |
|---------|---------------|
| Credentials | Environment variables only — never hardcoded |
| Input validation | Email regex + string length limits on all inputs |
| Audit log | Append-only; every action recorded with timestamp and actor |
| Session cookies | `HttpOnly`, `SameSite=Lax` |
| Okta token | Scoped token — not super-admin |
| AD service account | Read + targeted modify permissions only |

See [SECURITY.md](SECURITY.md) for the full security policy and vulnerability reporting process.

---

## CSV Offboarding Format

| Column | Required | Description |
|--------|----------|-------------|
| `email` | Yes | Employee email (unique identifier) |
| `employee_id` | No | Reference ID |
| `reason` | No | Resignation · Termination · Contract end |
| `notes` | No | Additional notes for the audit log |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branching conventions, commit format, and PR guidelines.

## License

MIT © 2026 Imranali Mohammed — see [LICENSE](LICENSE)
