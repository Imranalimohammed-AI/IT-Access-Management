# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` (latest) | ✅ Active |
| `develop` | ✅ Active |
| Older tags | ❌ Not supported |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately to: **imranali.mohammed@cotiviti.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

We acknowledge within **48 hours** and provide a remediation timeline within **7 days**.

## Security Controls

| Control | Implementation |
|---------|---------------|
| Credentials | Loaded from environment variables only — never hardcoded |
| Input validation | Email regex + string length limits on all user-supplied fields |
| LDAP injection | DN components escaped before bind |
| Audit log | Append-only JSONL; every IAM action recorded with timestamp + actor |
| Session cookies | `HttpOnly`, `SameSite=Lax` |
| HTTPS | Set `SESSION_COOKIE_SECURE = True` when serving over TLS |
| Okta token | Scoped read-write token — never super-admin |
| AD service account | Minimum permissions: read + targeted modify only |

## Security Principles

- All secrets live in `.env` (excluded from version control via `.gitignore`)
- SSL verification is always enabled — never disabled
- No credentials, tokens, or PII in logs
- Branch `main` is protected — direct pushes are blocked
