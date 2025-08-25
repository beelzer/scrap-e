# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **@beelzer** via GitHub Security Advisory or by email. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

### Process

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email your findings to the maintainer or use GitHub's Security Advisory feature
3. Provide sufficient information to reproduce the problem
4. Include the following in your report:
   - Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
   - Full paths of source file(s) related to the manifestation of the issue
   - The location of the affected source code (tag/branch/commit or direct URL)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit the issue

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed about the progress towards a fix and full announcement
- **Credit**: We will credit you for the discovery when we announce the vulnerability (unless you prefer to remain anonymous)
- **Disclosure Timeline**: We aim to fully disclose the vulnerability within 90 days of the initial report

## Security Best Practices for Users

When using scrap-e:

1. **Keep your installation updated** to the latest version
2. **Never commit credentials** or API keys to your repository
3. **Use environment variables** for sensitive configuration
4. **Review scraped data** for sensitive information before sharing
5. **Respect rate limits** and terms of service of scraped sources
6. **Use secure connections** (HTTPS) when possible
7. **Validate and sanitize** all scraped data before use
8. **Monitor your logs** for suspicious activity

## Security Features

scrap-e includes several security features:

- Automatic credential masking in logs
- Support for proxy rotation and authentication
- Rate limiting and backoff strategies
- Secure storage of session data
- Input validation and sanitization
- Support for various authentication methods

## Contact

For any security concerns, please contact:
- GitHub: @beelzer
- Use GitHub's private vulnerability reporting feature

Thank you for helping keep scrap-e and its users safe!
