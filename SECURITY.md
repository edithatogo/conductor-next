# Security Policy

**Last Updated:** March 3, 2026  
**Version:** 1.0

## Supported Versions

Conductor uses the following versioning scheme for security updates:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest | :x:                |

We recommend always using the latest version of Conductor to ensure you have all security patches and improvements.

---

## Reporting a Vulnerability

We take the security of Conductor seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### **Important: Do NOT Report Publicly**

**Please do NOT report security vulnerabilities through public GitHub issues.** This helps prevent potential exploitation before a fix is available.

### How to Report

Instead, please report vulnerabilities via email to:

**Email:** [security@edithatogo.com](mailto:security@edithatogo.com)

If you prefer not to use email, you can also:

1. Create a private security advisory on GitHub:
   - Go to the [Security tab](https://github.com/edithatogo/conductor-next/security)
   - Click "Report a vulnerability"
   - Provide details privately to maintainers

### Information to Include

When reporting, please include as much information as possible:

1. **Description:** Clear description of the vulnerability
2. **Steps to Reproduce:** Detailed steps to reproduce the issue
3. **Impact:** Potential impact if exploited
4. **Affected Versions:** Which versions are affected (if known)
5. **Suggested Fix:** Any suggestions for fixing the issue (optional)

### What to Expect

#### Response Timeline

- **Initial Response:** You should receive a response within **48 hours** acknowledging your report
- **Status Update:** Within **5 business days**, we'll provide an initial assessment and timeline
- **Resolution:** We aim to resolve critical issues within **30 days**

#### Process

After you submit a report:

1. **Acknowledgment:** We'll confirm receipt of your report
2. **Assessment:** Our security team will evaluate the vulnerability
3. **Communication:** We'll keep you informed of our progress
4. **Resolution:** Once fixed, we'll notify you and publish a security advisory (if appropriate)
5. **Credit:** With your permission, we'll acknowledge your responsible disclosure

#### Follow-up

If you haven't received a response within 48 hours, or if you don't hear back for 5 business days after the initial response, please follow up via the same channel to ensure we received your message.

---

## Security Best Practices

When using Conductor, please follow these security best practices:

### 1. Protect Sensitive Information

- **Never commit API keys, tokens, or passwords** to your repository
- Use environment variables for sensitive configuration
- Add `.env` files to your `.gitignore`
- Review all generated code before execution

### 2. Keep Dependencies Updated

- Regularly update Conductor to the latest version
- Enable Dependabot or similar tools for dependency monitoring
- Review and apply security patches promptly

### 3. Secure Your Environment

- Use Conductor in secure, trusted environments only
- Ensure your AI CLI tools are authenticated properly
- Review permissions granted to extensions and plugins

### 4. Review AI-Generated Code

- **Always review AI-generated code** before committing or executing
- AI may suggest insecure patterns - apply security best practices
- Use static analysis tools (e.g., `bandit` for Python, `npm audit` for Node.js)

### 5. Token Consumption Awareness

- Conductor uses AI services that may expose project context
- Be mindful of what context is shared with AI services
- Consider using local AI models for sensitive projects

### 6. Git Operations

- Review Git operations before execution (reverts, rebases, etc.)
- Understand that some operations rewrite history
- Backup important work before major operations

---

## Known Security Considerations

### AI-Generated Code

Conductor uses AI to generate code suggestions. Important considerations:

- **Review Required:** All AI-generated code should be reviewed before use
- **No Guarantees:** AI may suggest insecure or vulnerable code patterns
- **Your Responsibility:** You are responsible for the security of code you commit

### Token Consumption

Conductor's context-driven approach involves:

- Reading and analyzing your project's context
- Sharing context with AI services for processing
- Potential exposure of project structure and patterns

**Mitigation:**
- Review what context is shared
- Use local AI models when possible
- Be cautious with sensitive projects

### Git Operations

Conductor performs Git operations automatically:

- Branch creation and checkout
- Commits with git notes
- Potential history rewrites (revert operations)

**Mitigation:**
- Review operations before confirming
- Understand the impact of each operation
- Backup before major operations

---

## Security Tools & Scanning

We use the following tools to maintain security:

### Automated Scanning

- **Dependabot:** Monitors dependencies for known vulnerabilities
- **GitHub Security Advisories:** Tracks vulnerabilities in our dependencies
- **npm audit:** Scans Node.js dependencies
- **safety / pip-audit:** Scans Python dependencies

### Manual Reviews

- Security review for all major releases
- Code review for security-sensitive changes
- Regular dependency audits

### Reporting Issues Found by Scanners

If automated scanners report issues:

1. **Verify:** Confirm the issue is real (not a false positive)
2. **Prioritize:** Assess severity and impact
3. **Fix:** Apply patches or updates
4. **Document:** Update changelog with fix

---

## Security Changelog

### Version 1.0 (March 3, 2026)

- Initial security policy created
- Added vulnerability reporting process
- Documented security best practices
- Established response timeline

---

## Acknowledgments

We would like to thank the following for their contributions to our security:

- Community members who report vulnerabilities responsibly
- Security researchers who help improve our security posture
- Contributors who fix security issues

*(This section will be updated to acknowledge specific contributors as appropriate)*

---

## Contact & Questions

### Security Questions

For general security questions:

- **Email:** [security@edithatogo.com](mailto:security@edithatogo.com)
- **GitHub:** Create an issue with the "security" label (for non-sensitive questions)

### Updates

This policy is reviewed and updated regularly. For the latest version, please refer to the [SECURITY.md](https://github.com/edithatogo/conductor-next/blob/main/SECURITY.md) file in our repository.

---

## References

- [GitHub Security Features](https://docs.github.com/en/code-security)
- [Responsible Disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

**Thank you for helping keep Conductor and our users safe!**
