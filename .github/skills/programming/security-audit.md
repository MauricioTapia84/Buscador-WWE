# 🛡️ Security Audit & Hardening Skill

Automation for the `@security-agent` to validate against OWASP.

## 🎯 Purpose
Continuous security validation of APIs and Authentication flow.

## 🛠️ Actions
1. **JWT Validation Check**: Verify all private routes use the `auth` middleware.
2. **Input Sanitization**: Scan routes for missing Zod validations.
3. **CORS Policy Review**: Check `app.js` for strict origin definitions.
4. **Dependency Audit**: Run and analyze `npm audit` results.

## ⚠️ Constraints
- Reject any endpoint without explicit authorization (unless documented as public).
- Sensitive data (passwords, tokens) must never be logged.
