# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. Email the maintainers directly or use GitHub's private vulnerability reporting feature
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

### Security Measures

EVE Gatekeeper implements the following security measures:

#### API Security
- Rate limiting (configurable, default 100 req/min)
- Request size limits (10MB default)
- Security headers (CSP, X-Frame-Options, etc.)
- CORS configuration

#### Authentication (When Enabled)
- API key authentication
- EVE SSO OAuth2 integration (for ESI)

#### Data Security
- No sensitive data stored (ESI tokens are ephemeral)
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM

#### Infrastructure Security
- Non-root Docker container
- Health checks for orchestration
- Dependency scanning in CI/CD

### Security Best Practices for Deployment

1. **Always use HTTPS** in production
2. **Change default secrets** (SECRET_KEY in .env)
3. **Enable rate limiting** for public deployments
4. **Use PostgreSQL** instead of SQLite for production
5. **Keep dependencies updated** (`pip-audit` runs in CI)
6. **Monitor logs** for suspicious activity

### Dependency Security

We use automated tools to monitor dependencies:
- `pip-audit` in CI pipeline
- Dependabot alerts (when enabled)
- Regular dependency updates

## Disclosure Policy

- We follow responsible disclosure practices
- Security fixes are released as soon as possible
- Public disclosure occurs after patches are available
- Credit is given to reporters (unless anonymity is requested)

## Contact

For security concerns, contact the repository maintainers through GitHub.
