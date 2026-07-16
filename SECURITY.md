# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Active development |

## Reporting a Vulnerability

If you discover a security vulnerability, please open a private issue on GitHub or email the project maintainer.

We will acknowledge receipt within 48 hours and provide a timeline for the fix.

## Best Practices

- Never commit `.env` files with real secrets
- Use environment variables for all sensitive configuration
- Keep dependencies updated via `pip-audit` or `dependabot`
- Enable CSRF protection (enabled by default in Django)
- Use HTTPS in production (Vercel handles SSL at the edge)
