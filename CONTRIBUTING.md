# Contributing to IT Access Management

Thank you for your interest in contributing!

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, protected — merge via PR only |
| `develop` | Integration branch — all feature PRs target here |
| `feature/<name>` | New features, branched from `develop` |
| `fix/<name>` | Bug fixes, branched from `develop` |
| `hotfix/<name>` | Critical fixes branched directly from `main` |

## Workflow

1. Branch from `develop`: `git checkout -b feature/your-feature develop`
2. Make your changes — keep commits small and focused
3. Push and open a PR targeting `develop`
4. After review and approval, `develop` is merged into `main` via PR

## Commit Message Format

```
type(scope): short description

Types: feat | fix | docs | style | refactor | test | chore | security
```

Examples:
- `feat(users): add bulk group removal endpoint`
- `fix(audit): correct timestamp timezone handling`
- `security(ldap): sanitise DN input before bind`

## Code Style

- Follow PEP 8
- Keep functions small and single-purpose
- Run `python -m py_compile <file>.py` before committing
- No unused imports

## Security Requirements

- Never commit secrets, API keys, or passwords — use environment variables
- Never disable SSL verification or input sanitisation
- All user input must be validated at the boundary
- See [SECURITY.md](SECURITY.md) for the full policy

## Pull Request Checklist

- [ ] Branched from `develop`, not `main`
- [ ] No secrets or credentials in the diff
- [ ] Tested locally against real Okta/AD endpoints (or clearly documented as untested)
- [ ] README updated if behaviour changed
- [ ] SECURITY.md updated if security controls changed
