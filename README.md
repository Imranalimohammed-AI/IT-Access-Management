# IT Access Management

Cotiviti IT Engineering | Internal IAM Platform

A collection of tools for Identity & Access Management — providing IT administrators with real-time visibility into user access across Okta and Active Directory, with approval workflows, audit logging, and bulk offboarding.

---

## Projects

### AccessOps — IAM Dashboard

A web-based dashboard for IT administrators built with Flask.

| Feature | Description |
|---------|-------------|
| **Users** | Search users, view Okta profile, AD account, app access, and licenses |
| **Applications** | See all application assignments across the org |
| **Licenses** | Manage Microsoft 365 and software license assignments |
| **Requests** | Approve or deny access requests with one click |
| **Audit Log** | Full tamper-evident log of every IAM action taken |
| **Agent View** | Side-by-side user comparison and risk flag view |
| **Bulk Offboarding** | CSV upload → review → execute to offboard multiple users at once |

---

## Quick Start

```powershell
cd AccessOps
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python main.py
```

Open your browser at: **http://localhost:5050**

---

## Requirements

- Python 3.14+ (managed via [uv](https://github.com/astral-sh/uv))
- Okta API token
- Active Directory service account (LDAP)

---

## Security Notes

- All credentials are loaded from environment variables — never hardcoded.
- All user input is sanitized before use.
- Audit log is append-only with timestamps and actor tracking.
- LDAP bind uses a dedicated read + modify service account.
- Okta API token should be scoped, not a super-admin token.
