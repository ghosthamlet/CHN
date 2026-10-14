# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| < 1.1   | :x:                |

## Security Updates

### Version 1.1.0 (2026-10-14)
- **CRITICAL**: Fixed CWE-502 pickle deserialization vulnerability
- Replaced pickle with JSON for cookie storage
- Replaced pickle with joblib for ML model storage
- Added automatic migration from old pickle format

## Reporting a Vulnerability

If you discover a security vulnerability in CHN, please report it by:

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email the maintainer directly (see GitHub profile)
3. Or use GitHub Security Advisories (preferred):
   - Go to the Security tab
   - Click "Report a vulnerability"
   - Provide detailed information

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)
- Your contact information for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical issues within 30 days

## Security Best Practices

### For Users

1. **Docker Security**:
   - Never use `chmod 777` on volume mounts
   - Use read-only mounts when possible: `--volume path:/app/data:ro`
   - Run containers as non-root: `--user 1000:1000`
   - Use named volumes instead of bind mounts

2. **File Permissions**:
   - Cookie files should be `0600` (user read/write only)
   - Model files should be `0644` (user write, others read)
   - Data directory should be `0755` (not world-writable)

3. **Network Security**:
   - Use HTTPS proxy when configured
   - Verify SSL certificates in production
   - Keep dependencies updated

### For Developers

1. **Serialization**:
   - Never use `pickle` for untrusted data
   - Use JSON for configuration and cookies
   - Use joblib for scikit-learn models
   - Add integrity checks (HMAC) for sensitive files

2. **Input Validation**:
   - Validate all external inputs
   - Sanitize URLs before opening
   - Check file permissions before operations
   - Verify file paths stay within expected directories

3. **Dependencies**:
   - Keep all dependencies updated
   - Use `pip-audit` to check for vulnerabilities
   - Pin dependency versions in production

## Known Security Considerations

### Cookie Storage
Cookies are stored in plaintext JSON files. For production:
- Ensure proper file permissions (`chmod 600 data/hn.cookie`)
- Consider encrypting the cookie file at rest
- Use Docker secrets or environment variables for sensitive data

### ML Model Integrity
The ML model file is loaded without signature verification. To enhance security:
- Store model checksums separately
- Verify file hash before loading
- Use signed models in production

### Docker Considerations
- Default user is root (consider adding non-root user)
- No security profiles applied (consider AppArmor/SELinux)
- Volume mounts can expose host filesystem

## Security Changelog

### 2026-10-14 - Version 1.1.0
- **[CRITICAL]** Fixed CWE-502: Pickle deserialization vulnerability in cookie handling (hn.py:89)
- **[CRITICAL]** Fixed CWE-502: Pickle deserialization vulnerability in model loading (hn.py:247)
- Added automatic migration from pickle to JSON/joblib formats
- Added this SECURITY.md file
- Updated documentation with security best practices

### Prior to 1.1.0
- No formal security policy
- Pickle used for serialization (vulnerable to RCE)

## References

- [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
- [Python Pickle Security](https://docs.python.org/3/library/pickle.html)
- [OWASP Deserialization](https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Scikit-learn Model Persistence](https://scikit-learn.org/stable/model_persistence.html)

## Acknowledgments

Security vulnerabilities reported by:
- Issue #1 (2026-10-14): Pickle deserialization RCE

## License

This security policy is part of CHN and follows the same MIT license.
