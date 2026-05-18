# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (main) | ✅ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it by opening a [GitHub Security Advisory](../../security/advisories/new) in this repository.

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix

You can expect an acknowledgement within 48 hours and a resolution timeline within 7 days for critical issues.

## Security Considerations

### API Keys

- **Never commit `.env` files** — they are gitignored by default
- All credentials (IBM Orchestrate, LLM provider, GitHub token) must be stored in environment variables or HF Space secrets
- Rotate any keys that are accidentally exposed immediately

### Generated Agent Code

- AgentForge executes LLM-generated Python code inside IBM watsonx Orchestrate's sandboxed runtime
- Only `urllib.request`, `urllib.parse`, `json`, `os`, and `yaml` are permitted in generated tools
- `httpx` and `requests` are explicitly blocked by validators

### CORS

- The production CORS policy allows all origins (`*`) for demo purposes
- For production deployments, restrict `allow_origins` in `api/main.py` to your specific frontend domain
